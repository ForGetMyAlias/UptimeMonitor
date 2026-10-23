import asyncio
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest
from dishka import make_async_container
from litestar.testing import TestClient

from src.app import app
from src.core.ioc import AppProvider
from src.worker import run_checks_job


class _Ok(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ok")

    def log_message(self, *args):
        pass


@pytest.fixture
def site_url():
    server = HTTPServer(("127.0.0.1", 0), _Ok)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{server.server_port}/"
    server.shutdown()


def run_worker_once():
    async def job():
        container = make_async_container(AppProvider())
        try:
            await run_checks_job(container)
        finally:
            await container.close()

    asyncio.run(job())


def test_monitor_lifecycle(site_url):
    with TestClient(app) as client:
        up = client.post("/api/v1/monitors", json={"name": "up", "url": site_url, "interval_seconds": 10})
        assert up.status_code == 201
        down = client.post("/api/v1/monitors", json={"name": "down", "url": "http://127.0.0.1:1/"})
        assert down.status_code == 201
        assert len(client.get("/api/v1/monitors").json()) == 2

        run_worker_once()

        up_stats = client.get(f"/api/v1/monitors/{up.json()['id']}/stats").json()
        assert up_stats["total_checks"] == 1
        assert up_stats["uptime_percentage"] == 100.0
        down_stats = client.get(f"/api/v1/monitors/{down.json()['id']}/stats").json()
        assert down_stats["total_checks"] == 1
        assert down_stats["uptime_percentage"] == 0.0

        # interval_seconds ещё не прошёл, повторный запуск не должен дублировать проверку
        run_worker_once()
        assert client.get(f"/api/v1/monitors/{up.json()['id']}/stats").json()["total_checks"] == 1

        assert client.delete(f"/api/v1/monitors/{up.json()['id']}").status_code == 204
        assert len(client.get("/api/v1/monitors").json()) == 1


def test_unknown_site_is_404():
    with TestClient(app) as client:
        missing = "00000000-0000-0000-0000-000000000000"
        assert client.get(f"/api/v1/monitors/{missing}/stats").status_code == 404
        assert client.delete(f"/api/v1/monitors/{missing}").status_code == 404


def test_bad_input_rejected():
    with TestClient(app) as client:
        assert client.post("/api/v1/monitors", json={"name": "x", "url": "not-a-url"}).status_code == 400
        assert client.post("/api/v1/monitors", json={"name": "x", "url": "https://a.io", "interval_seconds": 1}).status_code == 400
