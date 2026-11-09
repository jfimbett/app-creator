"""Shared test fixtures.

`no_external_network` makes any attempt to reach another machine fail the test.
Connections to this machine's own loopback address stay allowed: on Windows, Python's
event loop (used by the FastAPI test client) opens a socket pair to 127.0.0.1 inside the
same process. That is not network access, and blocking it would break the test client
rather than catch a real request.
"""

import socket

import pytest

LOOPBACK_HOSTS = {"127.0.0.1", "::1", "localhost"}


def _host_of(address) -> str | None:
    if isinstance(address, tuple) and address:
        return str(address[0])
    return None


@pytest.fixture
def no_external_network(monkeypatch):
    real_connect = socket.socket.connect
    real_create_connection = socket.create_connection
    real_getaddrinfo = socket.getaddrinfo

    def connect(self, address):
        if _host_of(address) in LOOPBACK_HOSTS:
            return real_connect(self, address)
        raise AssertionError(f"network access attempted: connect to {address!r}")

    def create_connection(address, *args, **kwargs):
        if _host_of(address) in LOOPBACK_HOSTS:
            return real_create_connection(address, *args, **kwargs)
        raise AssertionError(f"network access attempted: create_connection to {address!r}")

    def getaddrinfo(host, *args, **kwargs):
        if host in LOOPBACK_HOSTS:
            return real_getaddrinfo(host, *args, **kwargs)
        raise AssertionError(f"network access attempted: name lookup for {host!r}")

    monkeypatch.setattr(socket.socket, "connect", connect)
    monkeypatch.setattr(socket, "create_connection", create_connection)
    monkeypatch.setattr(socket, "getaddrinfo", getaddrinfo)
