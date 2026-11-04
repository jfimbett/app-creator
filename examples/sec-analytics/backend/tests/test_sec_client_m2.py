"""Live data layer over a mocked SEC (M2-AC9, M2-E12, M2-E13). Offline: respx, no pass-through."""

import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

import httpx
import pytest
import respx
from pydantic import SecretStr

from app.clients.sec import (
    SecClient,
    SecContactNotConfigured,
    SecRateLimited,
    SecRefused,
    SecUnavailable,
    UpstreamNotAllowed,
    submissions_url,
)
from app.data.fixtures import FixtureStore, default_fixtures_dir
from app.data.source import DataSource
from app.errors import AppError
from app.settings import Settings

FAKE_UA = "SEC Analytics tests " + "tests" + "@" + "sec-analytics.invalid"
CIK = "0000320193"
URL = submissions_url(CIK)
NOW = datetime(2026, 11, 3, 12, 30, tzinfo=timezone.utc)
STORE = FixtureStore(default_fixtures_dir())


class FakeTime:
    def __init__(self) -> None:
        self.now = 1000.0
        self.sleeps: list[float] = []

    def monotonic(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        self.sleeps.append(seconds)
        self.now += seconds


@pytest.fixture
def fake_time() -> FakeTime:
    return FakeTime()


@pytest.fixture
def client(fake_time: FakeTime) -> SecClient:
    return SecClient(FAKE_UA, clock=fake_time.monotonic, sleep=fake_time.sleep)


def _data(tmp_path: Path, client: SecClient | None, **settings) -> DataSource:
    config = {"data_mode": "live", "sec_user_agent": SecretStr(FAKE_UA), "sec_cache_dir": tmp_path}
    return DataSource(Settings(**{**config, **settings}), STORE, client, clock=lambda: NOW)


@respx.mock
def test_m2_ac9_five_identical_requests_make_one_sec_call_and_then_the_cache_answers(
    tmp_path: Path, client: SecClient
) -> None:
    release = threading.Event()

    def slow(_: httpx.Request) -> httpx.Response:
        release.wait(5)
        return httpx.Response(200, json={"name": "SYNTHETIC"})

    route = respx.get(URL).mock(side_effect=slow)
    data = _data(tmp_path, client)
    with ThreadPoolExecutor(5) as pool:
        futures = [pool.submit(data.submissions, CIK, "live") for _ in range(5)]
        time.sleep(0.2)  # let every caller join the flight before the answer arrives
        release.set()
        results = [f.result(timeout=5) for f in futures]
    assert route.call_count == 1
    assert {r.source.label for r in results} == {"LIVE · retrieved 2026-11-03 12:30 UTC"}

    repeat = data.submissions(CIK, "live")
    assert route.call_count == 1
    assert repeat.source.label == "CACHED · retrieved 2026-11-03"
    assert repeat.source.mode == "cached"
    assert repeat.data == {"name": "SYNTHETIC"}


@respx.mock
def test_different_urls_are_at_least_one_second_apart(
    client: SecClient, fake_time: FakeTime
) -> None:
    respx.get(URL).mock(return_value=httpx.Response(200, json={}))
    other = submissions_url("789019")
    respx.get(other).mock(return_value=httpx.Response(200, json={}))
    client.get_json(URL)
    client.get_json(other)
    assert fake_time.sleeps == [pytest.approx(1.0)]


@respx.mock
def test_the_rate_setting_sets_the_spacing(fake_time: FakeTime) -> None:
    fast = SecClient(
        FAKE_UA, clock=fake_time.monotonic, sleep=fake_time.sleep, max_requests_per_second=2
    )
    respx.get(URL).mock(return_value=httpx.Response(200, json={}))
    fast.get_json(URL)
    fast.get_json(URL)
    assert fake_time.sleeps == [pytest.approx(0.5)]


@respx.mock
def test_m2_e12_429_with_retry_after_waits_then_succeeds(
    client: SecClient, fake_time: FakeTime
) -> None:
    route = respx.get(URL).mock(
        side_effect=[
            httpx.Response(429, headers={"Retry-After": "5"}),
            httpx.Response(200, json={"ok": True}),
        ]
    )
    assert client.get_json(URL) == {"ok": True}
    assert route.call_count == 2
    assert fake_time.sleeps[0] >= 5


@respx.mock
def test_m2_e12_429_gives_up_after_two_retries_as_rate_limited(client: SecClient) -> None:
    route = respx.get(URL).mock(return_value=httpx.Response(429, headers={"Retry-After": "7"}))
    with pytest.raises(SecRateLimited) as caught:
        client.get_json(URL)
    assert route.call_count == 3
    assert caught.value.retry_after == 7


@respx.mock
def test_a_503_without_retry_after_is_an_outage(client: SecClient) -> None:
    route = respx.get(URL).mock(return_value=httpx.Response(503))
    with pytest.raises(SecUnavailable) as caught:
        client.get_json(URL)
    assert route.call_count == 3
    assert not isinstance(caught.value, SecRateLimited)


@respx.mock
def test_m2_e12_403_is_not_retried(client: SecClient) -> None:
    route = respx.get(URL).mock(return_value=httpx.Response(403))
    with pytest.raises(SecRefused):
        client.get_json(URL)
    assert route.call_count == 1


@respx.mock
def test_timeout_is_unavailable(client: SecClient) -> None:
    respx.get(URL).mock(side_effect=httpx.ReadTimeout("slow"))
    with pytest.raises(SecUnavailable):
        client.get_json(URL)


@pytest.mark.parametrize(
    "target",
    ["https://example.com/", "https://www.sec.gov/cgi-bin/browse-edgar"],
)
@respx.mock
def test_m2_e13_redirect_outside_the_allowlist_is_not_requested(
    client: SecClient, target: str
) -> None:
    respx.get(URL).mock(return_value=httpx.Response(302, headers={"Location": target}))
    forbidden = respx.get(target).mock(return_value=httpx.Response(200, json={}))
    with pytest.raises(UpstreamNotAllowed):
        client.get_json(URL)
    assert forbidden.call_count == 0


@respx.mock
def test_missing_contact_is_refused_before_any_request_even_with_a_cache(tmp_path: Path) -> None:
    route = respx.get(URL).mock(return_value=httpx.Response(200, json={}))
    configured = _data(tmp_path, None)
    configured._cache.put(URL, {"name": "cached"})
    unconfigured = _data(tmp_path, None, sec_user_agent=None)
    with pytest.raises(SecContactNotConfigured):
        unconfigured.submissions(CIK, "live")
    assert route.call_count == 0


def test_live_under_fixture_mode_is_refused(tmp_path: Path) -> None:
    data = _data(tmp_path, None, data_mode="fixtures")
    with pytest.raises(AppError) as caught:
        data.submissions(CIK, "live")
    assert (caught.value.code, caught.value.status) == ("live_disabled", 409)


@respx.mock
def test_failed_responses_are_not_cached(tmp_path: Path, client: SecClient) -> None:
    route = respx.get(URL).mock(
        side_effect=[httpx.Response(403), httpx.Response(200, json={"name": "later"})]
    )
    data = _data(tmp_path, client)
    with pytest.raises(SecRefused):
        data.submissions(CIK, "live")
    assert data.submissions(CIK, "live").data == {"name": "later"}
    assert route.call_count == 2


@respx.mock
def test_concurrent_callers_share_the_leaders_error(tmp_path: Path, client: SecClient) -> None:
    release = threading.Event()

    def refused(_: httpx.Request) -> httpx.Response:
        release.wait(5)
        return httpx.Response(403)

    route = respx.get(URL).mock(side_effect=refused)
    data = _data(tmp_path, client)
    with ThreadPoolExecutor(3) as pool:
        futures = [pool.submit(data.submissions, CIK, "live") for _ in range(3)]
        time.sleep(0.2)
        release.set()
        errors = [f.exception(timeout=5) for f in futures]
    assert route.call_count == 1
    assert all(isinstance(e, SecRefused) for e in errors)
