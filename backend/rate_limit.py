from collections import defaultdict, deque
from datetime import datetime, timedelta
from threading import Lock
from typing import Deque, Dict, Optional, Tuple

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models import UsageCounter
from security import LimitPolicy, Principal


class RequestRateLimiter:
    def __init__(self) -> None:
        self._lock = Lock()
        self._requests: Dict[Tuple[str, str], Deque[datetime]] = defaultdict(deque)

    def check(self, client_id: str, route_key: str, max_per_minute: int) -> None:
        if max_per_minute <= 0:
            return

        now = datetime.utcnow()
        cutoff = now - timedelta(minutes=1)
        key = (client_id, route_key)

        with self._lock:
            entries = self._requests[key]
            while entries and entries[0] < cutoff:
                entries.popleft()

            if len(entries) >= max_per_minute:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded",
                )

            entries.append(now)


class UsageQuotaManager:
    @staticmethod
    def _today() -> str:
        return datetime.utcnow().strftime("%Y-%m-%d")

    @staticmethod
    def _get_usage_row(
        db: Session,
        client_id: str,
        create_if_missing: bool = False,
    ) -> Optional[UsageCounter]:
        today = UsageQuotaManager._today()
        row = (
            db.query(UsageCounter)
            .filter(UsageCounter.client_id == client_id, UsageCounter.usage_date == today)
            .first()
        )

        if row or not create_if_missing:
            return row

        row = UsageCounter(client_id=client_id, usage_date=today)
        db.add(row)
        db.flush()
        return row

    def ensure_daily_request_quota(
        self,
        db: Session,
        principal: Principal,
        policy: LimitPolicy,
    ) -> None:
        row = self._get_usage_row(db, principal.client_id)
        if not row:
            return
        if row.requests_count >= policy.daily_requests_limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Daily request quota exceeded",
            )

    def ensure_upload_quota(
        self,
        db: Session,
        principal: Principal,
        policy: LimitPolicy,
        upload_bytes: int,
    ) -> None:
        row = self._get_usage_row(db, principal.client_id)
        if not row:
            return
        if row.upload_bytes + upload_bytes > policy.daily_upload_bytes_limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Daily upload quota exceeded",
            )

    def ensure_analysis_quota(
        self,
        db: Session,
        principal: Principal,
        policy: LimitPolicy,
    ) -> None:
        row = self._get_usage_row(db, principal.client_id)
        if not row:
            return
        if row.analysis_jobs_count >= policy.daily_analysis_jobs_limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Daily analysis quota exceeded",
            )

    def record_request(
        self,
        db: Session,
        principal: Principal,
    ) -> None:
        row = self._get_usage_row(db, principal.client_id, create_if_missing=True)
        row.requests_count += 1
        db.commit()

    def record_upload(
        self,
        db: Session,
        principal: Principal,
        upload_bytes: int,
    ) -> None:
        row = self._get_usage_row(db, principal.client_id, create_if_missing=True)
        row.upload_bytes += max(upload_bytes, 0)
        db.commit()

    def record_analysis_job(
        self,
        db: Session,
        principal: Principal,
    ) -> None:
        row = self._get_usage_row(db, principal.client_id, create_if_missing=True)
        row.analysis_jobs_count += 1
        db.commit()
