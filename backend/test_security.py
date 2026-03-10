#!/usr/bin/env python3
"""
Security and quota integration test:
- API key auth
- RBAC checks
- Rate limiting
"""

import json
import os
import unittest
import asyncio
from pathlib import Path

import httpx


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = PROJECT_ROOT / "backend"

if str(BACKEND_DIR) not in os.sys.path:
    os.sys.path.append(str(BACKEND_DIR))


os.environ["AUTH_ENABLED"] = "true"
os.environ["DATABASE_URL"] = "sqlite:////tmp/ai_dashboard_security.db"
os.environ["API_KEYS_JSON"] = json.dumps(
    [
        {
            "key": "viewer-key",
            "client_id": "viewer-client",
            "role": "viewer",
            "requests_per_minute": 2,
            "daily_requests_limit": 100,
        },
        {
            "key": "analyst-key",
            "client_id": "analyst-client",
            "role": "analyst",
            "requests_per_minute": 30,
            "daily_requests_limit": 100,
        },
        {
            "key": "admin-key",
            "client_id": "admin-client",
            "role": "admin",
            "requests_per_minute": 30,
            "daily_requests_limit": 100,
        },
    ]
)

from security import load_api_keys  # noqa: E402

load_api_keys.cache_clear()

from database import init_database, DATABASE_URL  # noqa: E402
from main import app  # noqa: E402


class SecurityIntegrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if DATABASE_URL.startswith("sqlite:////"):
            db_path = Path(DATABASE_URL.replace("sqlite:////", "/", 1))
            if db_path.exists():
                db_path.unlink()
        init_database()

    def test_rbac_blocks_viewer_from_ingest(self):
        async def run():
            transport = httpx.ASGITransport(app=app)
            async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
                csv_body = "date,value\n2024-01-01,1\n2024-01-02,2\n"
                response = await client.post(
                    "/ingest",
                    headers={"x-api-key": "viewer-key"},
                    files={"file": ("blocked.csv", csv_body, "text/csv")},
                )
                self.assertEqual(response.status_code, 403, response.text)

        asyncio.run(run())

    def test_rbac_allows_analyst_for_ingest(self):
        async def run():
            transport = httpx.ASGITransport(app=app)
            async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
                csv_body = "date,value\n2024-01-01,1\n2024-01-02,2\n"
                response = await client.post(
                    "/ingest",
                    headers={"x-api-key": "analyst-key"},
                    files={"file": ("allowed.csv", csv_body, "text/csv")},
                )
                self.assertEqual(response.status_code, 200, response.text)

        asyncio.run(run())

    def test_rate_limit_enforced_for_viewer(self):
        async def run():
            transport = httpx.ASGITransport(app=app)
            async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
                headers = {"x-api-key": "viewer-key"}
                first = await client.get("/datasets", headers=headers)
                second = await client.get("/datasets", headers=headers)
                third = await client.get("/datasets", headers=headers)

                self.assertEqual(first.status_code, 200, first.text)
                self.assertEqual(second.status_code, 200, second.text)
                self.assertEqual(third.status_code, 429, third.text)

        asyncio.run(run())

    def test_metrics_is_admin_only(self):
        async def run():
            transport = httpx.ASGITransport(app=app)
            async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
                viewer = await client.get("/metrics", headers={"x-api-key": "viewer-key"})
                admin = await client.get("/metrics", headers={"x-api-key": "admin-key"})

                self.assertEqual(viewer.status_code, 403, viewer.text)
                self.assertEqual(admin.status_code, 200, admin.text)
                self.assertIn("requests_total", admin.json())

        asyncio.run(run())


if __name__ == "__main__":
    unittest.main()
