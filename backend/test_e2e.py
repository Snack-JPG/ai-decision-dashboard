#!/usr/bin/env python3
"""
End-to-end API workflow test:
upload CSV -> queue analysis -> poll results.
"""

import os
import unittest
import asyncio
from pathlib import Path

import httpx


# Use dev-mode auth for tests.
os.environ.setdefault("AUTH_ENABLED", "false")
os.environ.setdefault("ANALYSIS_WORKERS", "1")
os.environ.setdefault("DATABASE_URL", "sqlite:////tmp/ai_dashboard_e2e.db")


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = PROJECT_ROOT / "backend"

if str(BACKEND_DIR) not in os.sys.path:
    os.sys.path.append(str(BACKEND_DIR))

from database import init_database, DATABASE_URL  # noqa: E402
from main import app  # noqa: E402


class ApiE2EWorkflowTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if DATABASE_URL.startswith("sqlite:////"):
            db_path = Path(DATABASE_URL.replace("sqlite:////", "/", 1))
        elif DATABASE_URL.startswith("sqlite:///./"):
            db_file = DATABASE_URL.replace("sqlite:///./", "", 1)
            db_path = Path(os.getcwd()) / db_file
        else:
            db_path = Path("/tmp/ai_dashboard_e2e.db")

        if db_path.exists():
            db_path.unlink()
        init_database()

    def test_upload_analyze_and_fetch_dashboard_payload(self):
        asyncio.run(self._run_workflow())

    async def _run_workflow(self):
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            csv_body = (
                "date,waiting_time_minutes,attendances\n"
                "2024-01-01,120,100\n"
                "2024-01-02,130,102\n"
                "2024-01-03,160,105\n"
                "2024-01-04,125,101\n"
                "2024-01-05,220,140\n"
                "2024-01-06,128,99\n"
                "2024-01-07,127,98\n"
                "2024-01-08,129,103\n"
                "2024-01-09,180,130\n"
                "2024-01-10,126,100\n"
                "2024-01-11,124,97\n"
                "2024-01-12,122,96\n"
                "2024-01-13,121,95\n"
                "2024-01-14,119,93\n"
            )

            upload_response = await client.post(
                "/ingest",
                files={"file": ("workflow.csv", csv_body, "text/csv")},
                data={"name": "Workflow Test Dataset"},
            )
            self.assertEqual(upload_response.status_code, 200, upload_response.text)
            dataset_id = upload_response.json()["dataset_id"]

            queue_response = await client.post(f"/analyze/{dataset_id}")
            self.assertIn(queue_response.status_code, (200, 202), queue_response.text)
            queue_payload = queue_response.json()
            self.assertIn("job", queue_payload)
            self.assertIn(queue_payload["status"], {"queued", "running", "completed"})

            latest_payload = None
            for _ in range(80):
                results_response = await client.get(f"/analyze/{dataset_id}/results")
                self.assertEqual(results_response.status_code, 200, results_response.text)
                latest_payload = results_response.json()
                if latest_payload.get("status") == "completed":
                    break
                await asyncio.sleep(0.2)

            self.assertIsNotNone(latest_payload)
            self.assertEqual(latest_payload["status"], "completed", str(latest_payload))
            self.assertIn("summary", latest_payload)
            self.assertIn("time_series_data", latest_payload)
            self.assertTrue(isinstance(latest_payload["summary"].get("key_metrics", []), list))


if __name__ == "__main__":
    unittest.main()
