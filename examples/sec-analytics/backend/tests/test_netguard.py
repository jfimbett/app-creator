"""The `no_external_network` guard still refuses real network access; only loopback passes."""

import socket

import httpx
import pytest


def test_guard_refuses_remote_connections(no_external_network) -> None:
    with pytest.raises(AssertionError, match="network access attempted"):
        socket.create_connection(("192.0.2.1", 443), timeout=1)  # TEST-NET-1, never routed
    with pytest.raises(AssertionError, match="network access attempted"):
        socket.getaddrinfo("data.sec.gov", 443)
    with pytest.raises(AssertionError, match="network access attempted"):
        httpx.get("https://data.sec.gov/submissions/CIK0000320193.json", timeout=1)


def test_guard_allows_loopback(no_external_network) -> None:
    left, right = socket.socketpair()
    left.close()
    right.close()
