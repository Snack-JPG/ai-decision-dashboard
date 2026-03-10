import json
import logging
import os
from collections import deque
from datetime import datetime
from threading import Lock
from typing import Any, Dict, Optional
from urllib import request as urllib_request


logger = logging.getLogger(__name__)


class MetricsCollector:
    def __init__(self) -> None:
        self._lock = Lock()
        self._metrics: Dict[str, Any] = {
            "started_at": datetime.utcnow().isoformat(),
            "requests_total": 0,
            "requests_4xx": 0,
            "requests_5xx": 0,
            "uploads_total": 0,
            "upload_bytes_total": 0,
            "analysis_jobs_started": 0,
            "analysis_jobs_completed": 0,
            "analysis_jobs_failed": 0,
        }
        self._recent_errors: deque[str] = deque(maxlen=50)

    def record_request(self, status_code: int) -> None:
        with self._lock:
            self._metrics["requests_total"] += 1
            if 400 <= status_code < 500:
                self._metrics["requests_4xx"] += 1
            elif status_code >= 500:
                self._metrics["requests_5xx"] += 1
                self._recent_errors.append(datetime.utcnow().isoformat())

    def record_upload(self, upload_bytes: int) -> None:
        with self._lock:
            self._metrics["uploads_total"] += 1
            self._metrics["upload_bytes_total"] += max(upload_bytes, 0)

    def record_analysis_started(self) -> None:
        with self._lock:
            self._metrics["analysis_jobs_started"] += 1

    def record_analysis_completed(self) -> None:
        with self._lock:
            self._metrics["analysis_jobs_completed"] += 1

    def record_analysis_failed(self) -> None:
        with self._lock:
            self._metrics["analysis_jobs_failed"] += 1

    def snapshot(self) -> Dict[str, Any]:
        with self._lock:
            return {
                **self._metrics,
                "recent_errors_count": len(self._recent_errors),
            }


def maybe_send_alert(event: str, message: str, context: Optional[Dict[str, Any]] = None) -> None:
    webhook_url = os.getenv("ALERT_WEBHOOK_URL")
    payload = {
        "event": event,
        "message": message,
        "timestamp": datetime.utcnow().isoformat(),
        "context": context or {},
    }

    logger.error("ALERT %s: %s | context=%s", event, message, payload["context"])
    if not webhook_url:
        return

    try:
        req = urllib_request.Request(
            webhook_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        urllib_request.urlopen(req, timeout=3)  # nosec B310
    except Exception:
        logger.exception("Failed to deliver alert webhook")
