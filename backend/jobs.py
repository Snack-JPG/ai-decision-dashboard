from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, asdict
from datetime import datetime
from threading import Lock
from typing import Callable, Dict, Optional
import uuid


@dataclass
class AnalysisJob:
    id: str
    dataset_id: str
    status: str
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Optional[str]]:
        return asdict(self)


class AnalysisJobQueue:
    def __init__(self, workers: int = 2) -> None:
        self._executor = ThreadPoolExecutor(max_workers=max(workers, 1))
        self._lock = Lock()
        self._jobs: Dict[str, AnalysisJob] = {}
        self._active_dataset_jobs: Dict[str, str] = {}

    def submit(self, dataset_id: str, task: Callable[[str], None]) -> tuple[AnalysisJob, bool]:
        with self._lock:
            existing_job_id = self._active_dataset_jobs.get(dataset_id)
            if existing_job_id:
                existing = self._jobs.get(existing_job_id)
                if existing and existing.status in {"queued", "running"}:
                    return existing, False

            job_id = str(uuid.uuid4())
            job = AnalysisJob(
                id=job_id,
                dataset_id=dataset_id,
                status="queued",
                created_at=datetime.utcnow().isoformat(),
            )
            self._jobs[job_id] = job
            self._active_dataset_jobs[dataset_id] = job_id

        self._executor.submit(self._execute, job_id, task)
        return job, True

    def _execute(self, job_id: str, task: Callable[[str], None]) -> None:
        with self._lock:
            job = self._jobs[job_id]
            job.status = "running"
            job.started_at = datetime.utcnow().isoformat()
            dataset_id = job.dataset_id

        try:
            task(dataset_id)
            with self._lock:
                job.status = "completed"
                job.completed_at = datetime.utcnow().isoformat()
                self._active_dataset_jobs.pop(dataset_id, None)
        except Exception as exc:
            with self._lock:
                job.status = "failed"
                job.error = str(exc)
                job.completed_at = datetime.utcnow().isoformat()
                self._active_dataset_jobs.pop(dataset_id, None)

    def get_job(self, job_id: str) -> Optional[AnalysisJob]:
        with self._lock:
            return self._jobs.get(job_id)

    def get_dataset_job(self, dataset_id: str) -> Optional[AnalysisJob]:
        with self._lock:
            job_id = self._active_dataset_jobs.get(dataset_id)
            if not job_id:
                return None
            return self._jobs.get(job_id)
