"""In fixture mode the app serves every M1 endpoint without any network access.

respx is active with no routes (any httpx call would fail) and opening a socket raises.
"""

import socket

import pytest
import respx
from fastapi.testclient import TestClient

from app.main import create_app

M1_REQUESTS = [
    ("/api/health", None),
    ("/api/meta", None),
    ("/api/companies/search", {"q": "aapl"}),
    ("/api/companies/search", {"q": "320193"}),
    ("/api/companies/search", {"q": "tesla"}),
    ("/api/companies/0000320193", None),
    ("/api/companies/789019", None),
    ("/api/companies/CIK1652044", None),
    ("/api/companies/320193/overview", None),
    ("/api/companies/0000789019/overview", None),
    ("/api/companies/1652044/overview", {"years": 5}),
]


@pytest.fixture
def no_sockets(monkeypatch):
    def refuse(*args, **kwargs):
        raise AssertionError("network access attempted in fixture mode")

    monkeypatch.setattr(socket.socket, "connect", refuse)
    monkeypatch.setattr(socket, "create_connection", refuse)
    monkeypatch.setattr(socket, "getaddrinfo", refuse)


def test_all_m1_endpoints_work_offline(no_sockets) -> None:
    with respx.mock(assert_all_called=False, assert_all_mocked=True) as router:
        client = TestClient(create_app())
        for path, params in M1_REQUESTS:
            response = client.get(path, params=params)
            assert response.status_code == 200, path
        assert router.calls.call_count == 0
