"""Document downloads stop on size (after unzipping, with capped memory) and on total time.

SEC is mocked with respx; the documents are invented. Security review 2026-11-09.
"""

import gzip
import zlib

import httpx
import pytest
import respx

from app.clients.sec import (
    DOWNLOAD_DEADLINE_SECONDS,
    SecClient,
    SecDocumentTooLarge,
    SecUnavailable,
)

URL = "https://www.sec.gov/Archives/edgar/data/999/000000099926000002/xmpl-k.htm"
FAKE_UA = "SEC Analytics tests " + "tests" + "@" + "sec-analytics.invalid"


class Clock:
    def __init__(self) -> None:
        self.now = 0.0

    def __call__(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        self.now += seconds


@pytest.fixture
def clock() -> Clock:
    return Clock()


@pytest.fixture
def client(clock):
    with respx.mock(assert_all_called=False, assert_all_mocked=True) as router:
        with SecClient(FAKE_UA, clock=clock, sleep=clock.sleep) as sec:
            yield sec, router


def test_gzip_bomb_in_one_piece_stops_at_the_limit(client) -> None:
    sec, router = client
    bomb = gzip.compress(b"\0" * 50_000_000)  # about 50 KB that unzips to 50 MB
    assert len(bomb) < 100_000
    router.get(URL).mock(
        return_value=httpx.Response(200, content=bomb, headers={"Content-Encoding": "gzip"})
    )
    with pytest.raises(SecDocumentTooLarge):
        sec.fetch(URL, max_bytes=1_000_000)


def test_gzip_and_deflate_under_the_limit_are_decoded_exactly(client) -> None:
    sec, router = client
    text = b"<p>" + b"Revenue grew. " * 5000 + b"</p>"
    router.get(URL).mock(
        return_value=httpx.Response(
            200, content=gzip.compress(text), headers={"Content-Encoding": "gzip"}
        )
    )
    assert sec.fetch(URL, max_bytes=len(text)).content == text
    router.get(URL).mock(
        return_value=httpx.Response(
            200, content=zlib.compress(text), headers={"Content-Encoding": "deflate"}
        )
    )
    assert sec.fetch(URL, max_bytes=len(text)).content == text


def test_exact_limit_passes_one_byte_more_fails(client) -> None:
    sec, router = client
    router.get(URL).mock(return_value=httpx.Response(200, content=b"x" * 1000))
    assert len(sec.fetch(URL, max_bytes=1000).content) == 1000
    with pytest.raises(SecDocumentTooLarge):
        sec.fetch(URL, max_bytes=999)


def test_slow_download_stops_after_the_deadline(client, clock) -> None:
    sec, router = client

    def dripping():
        for _ in range(100):
            clock.now += 15  # each piece arrives 15 s after the previous one
            yield b"<p>slow</p>"

    router.get(URL).mock(return_value=httpx.Response(200, content=dripping()))
    with pytest.raises(SecUnavailable, match="too slowly"):
        sec.fetch(URL, max_bytes=10_000_000)
    assert clock.now <= DOWNLOAD_DEADLINE_SECONDS + 30


def test_damaged_or_unknown_compression_is_an_error_not_text(client) -> None:
    sec, router = client
    router.get(URL).mock(
        return_value=httpx.Response(
            200, content=iter([b"not gzip"]), headers={"Content-Encoding": "gzip"}
        )
    )
    with pytest.raises(SecUnavailable, match="damaged"):
        sec.fetch(URL, max_bytes=10_000)
    router.get(URL).mock(
        return_value=httpx.Response(200, content=b"abc", headers={"Content-Encoding": "br"})
    )
    with pytest.raises(SecUnavailable, match="unexpected encoding"):
        sec.fetch(URL, max_bytes=10_000)
