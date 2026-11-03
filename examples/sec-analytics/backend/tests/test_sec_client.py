"""SEC client rules (brief §7): allowlist, User-Agent, throttle, Retry-After, 403, redirects.

Offline: respx mocks every request and has no pass-through, so an unmocked URL fails the test.
Time is fake: `FakeClock.sleep` advances the clock instead of waiting.
"""

from datetime import datetime, timedelta, timezone

import httpx
import pytest
import respx

from app.clients.sec import (
    COMPANY_TICKERS_URL,
    SecClient,
    SecContactNotConfigured,
    SecRefused,
    SecUnavailable,
    UpstreamNotAllowed,
    check_allowed,
    companyfacts_url,
    submissions_url,
)
from app.logic.cik import InvalidCik

# Fake contact on a reserved .invalid domain (RFC 2606), assembled so no address is written out.
FAKE_UA = "SEC Analytics tests " + "tests" + "@" + "sec-analytics.invalid"
APPLE_SUBMISSIONS = "https://data.sec.gov/submissions/CIK0000320193.json"
WALL_START = datetime(2026, 11, 3, 12, 0, 0, tzinfo=timezone.utc)


class FakeClock:
    """Monotonic and wall clocks that move only when `sleep` is called."""

    def __init__(self) -> None:
        self.now = 1000.0
        self.sleeps: list[float] = []

    def monotonic(self) -> float:
        return self.now

    def wall(self) -> datetime:
        return WALL_START + timedelta(seconds=self.now - 1000.0)

    def sleep(self, seconds: float) -> None:
        self.sleeps.append(seconds)
        self.now += seconds


@pytest.fixture
def clock() -> FakeClock:
    return FakeClock()


@pytest.fixture
def mock():
    with respx.mock(assert_all_mocked=True, assert_all_called=False) as router:
        yield router


def make_client(clock: FakeClock, user_agent: str | None = FAKE_UA) -> SecClient:
    return SecClient(user_agent, clock=clock.monotonic, sleep=clock.sleep, wall_clock=clock.wall)


# --- URL building and allowlist -------------------------------------------------------------


def test_urls_are_built_from_a_normalized_cik() -> None:
    assert submissions_url("320193") == APPLE_SUBMISSIONS
    assert companyfacts_url("CIK320193") == (
        "https://data.sec.gov/api/xbrl/companyfacts/CIK0000320193.json"
    )
    assert COMPANY_TICKERS_URL == "https://www.sec.gov/files/company_tickers.json"
    with pytest.raises(InvalidCik):
        submissions_url("../../etc")


@pytest.mark.parametrize(
    "url",
    [
        APPLE_SUBMISSIONS,
        "https://data.sec.gov/submissions/CIK0000320193-submissions-001.json",
        "https://data.sec.gov/api/xbrl/companyfacts/CIK0000320193.json",
        "https://www.sec.gov/files/company_tickers.json",
        "https://www.sec.gov/Archives/edgar/data/320193/000032019325000079/aapl-20250927.htm",
    ],
)
def test_allowlisted_urls_pass(url: str) -> None:
    check_allowed(url)


@pytest.mark.parametrize(
    "url",
    [
        "https://example.com/",
        "http://data.sec.gov/submissions/CIK0000320193.json",
        "https://data.sec.gov/submissions/CIK320193.json",
        "https://data.sec.gov/submissions/CIK0000320193.json?x=1",
        "https://data.sec.gov/submissions/CIK0000320193.json#frag",
        "https://data.sec.gov:8443/submissions/CIK0000320193.json",
        "https://user:pw@data.sec.gov/submissions/CIK0000320193.json",
        "https://data.sec.gov/api/xbrl/frames/us-gaap/Revenues/USD/CY2024.json",
        "https://www.sec.gov/files/company_tickers_exchange.json",
        "https://www.sec.gov/Archives/edgar/daily-index/xbrl/companyfacts.zip",
        "https://www.sec.gov/Archives/edgar/data/320193/000032019325000079/../../x",
        "https://data.sec.gov.example.com/submissions/CIK0000320193.json",
        "https://data.sec.gov/submissions/CIK0000320193.json\n",
        "https://data.sec.gov/submissions/CIK0000320193.json/",
    ],
)
def test_non_allowlisted_urls_are_refused(url: str) -> None:
    with pytest.raises(UpstreamNotAllowed):
        check_allowed(url)


def test_non_allowlisted_url_is_refused_before_any_request(clock: FakeClock, mock) -> None:
    route = mock.get("https://example.com/").respond(200, json={})
    with pytest.raises(UpstreamNotAllowed):
        make_client(clock).get_json("https://example.com/")
    assert not route.called


# --- Redirects ------------------------------------------------------------------------------


def test_redirect_to_foreign_host_is_refused_before_following(clock: FakeClock, mock) -> None:
    mock.get(COMPANY_TICKERS_URL).respond(302, headers={"Location": "https://example.com/"})
    foreign = mock.get("https://example.com/").respond(200, json={})
    with pytest.raises(UpstreamNotAllowed):
        make_client(clock).get_json(COMPANY_TICKERS_URL)
    assert not foreign.called


def test_redirect_to_allowlisted_path_is_followed(clock: FakeClock, mock) -> None:
    old = "https://data.sec.gov/submissions/CIK0000000001.json"
    mock.get(old).respond(301, headers={"Location": "/submissions/CIK0000320193.json"})
    target = mock.get(APPLE_SUBMISSIONS).respond(200, json={"cik": "320193"})
    assert make_client(clock).get_json(old) == {"cik": "320193"}
    assert target.call_count == 1


def test_more_than_three_redirects_are_refused(clock: FakeClock, mock) -> None:
    urls = [f"https://data.sec.gov/submissions/CIK000000000{i}.json" for i in range(6)]
    routes = [
        mock.get(here).respond(302, headers={"Location": there})
        for here, there in zip(urls[:-1], urls[1:], strict=True)
    ]
    with pytest.raises(UpstreamNotAllowed):
        make_client(clock).get_json(urls[0])
    assert [route.called for route in routes] == [True, True, True, True, False]


# --- User-Agent -----------------------------------------------------------------------------


@pytest.mark.parametrize(
    "value",
    [
        None,
        "",
        "   ",
        "OnlyOneWord",
        "Name without contact",
        "tests" + "@" + "sec-analytics.invalid",
        FAKE_UA + "\nX-Other: 1",
        FAKE_UA + "\r",
    ],
)
def test_missing_or_malformed_user_agent_refuses_naming_the_setting(
    clock: FakeClock, mock, value: str | None
) -> None:
    route = mock.get(APPLE_SUBMISSIONS).respond(200, json={})
    with pytest.raises(SecContactNotConfigured) as caught:
        make_client(clock, user_agent=value).get_json(APPLE_SUBMISSIONS)
    assert "SEC_USER_AGENT" in str(caught.value)
    if value and value.strip():
        assert value.strip() not in str(caught.value)
    assert not route.called


def test_request_sends_declared_user_agent_and_encoding(clock: FakeClock, mock) -> None:
    route = mock.get(APPLE_SUBMISSIONS).respond(200, json={"ok": True})
    make_client(clock).get_json(APPLE_SUBMISSIONS)
    sent = route.calls.last.request
    assert sent.headers["User-Agent"] == FAKE_UA
    assert sent.headers["Accept-Encoding"] == "gzip, deflate"


def test_user_agent_is_not_in_the_client_repr(clock: FakeClock) -> None:
    assert "sec-analytics.invalid" not in repr(make_client(clock))


# --- Throttle -------------------------------------------------------------------------------


def test_two_calls_are_at_least_one_second_apart(clock: FakeClock, mock) -> None:
    times: list[float] = []

    def record(request: httpx.Request) -> httpx.Response:
        times.append(clock.now)
        return httpx.Response(200, json={})

    mock.get(APPLE_SUBMISSIONS).mock(side_effect=record)
    client = make_client(clock)
    client.get_json(APPLE_SUBMISSIONS)
    client.get_json(APPLE_SUBMISSIONS)
    client.get_json(APPLE_SUBMISSIONS)
    assert len(times) == 3
    assert times[1] - times[0] >= 1.0
    assert times[2] - times[1] >= 1.0
    assert clock.sleeps[0] == pytest.approx(1.0)  # first call did not wait


# --- Retry-After, 429/503, 403 --------------------------------------------------------------


def test_429_with_retry_after_waits_then_succeeds(clock: FakeClock, mock) -> None:
    times: list[float] = []
    replies = iter(
        [httpx.Response(429, headers={"Retry-After": "5"}), httpx.Response(200, json={"a": 1})]
    )

    def reply(request: httpx.Request) -> httpx.Response:
        times.append(clock.now)
        return next(replies)

    mock.get(APPLE_SUBMISSIONS).mock(side_effect=reply)
    assert make_client(clock).get_json(APPLE_SUBMISSIONS) == {"a": 1}
    assert len(times) == 2
    assert times[1] - times[0] >= 5.0


def test_retry_after_as_http_date_is_honoured(clock: FakeClock, mock) -> None:
    times: list[float] = []
    later = (WALL_START + timedelta(seconds=7)).strftime("%a, %d %b %Y %H:%M:%S GMT")
    replies = iter(
        [httpx.Response(503, headers={"Retry-After": later}), httpx.Response(200, json={})]
    )

    def reply(request: httpx.Request) -> httpx.Response:
        times.append(clock.now)
        return next(replies)

    mock.get(APPLE_SUBMISSIONS).mock(side_effect=reply)
    make_client(clock).get_json(APPLE_SUBMISSIONS)
    assert times[1] - times[0] >= 7.0


def test_retry_after_is_capped_at_30_seconds(clock: FakeClock, mock) -> None:
    replies = iter(
        [httpx.Response(429, headers={"Retry-After": "3600"}), httpx.Response(200, json={})]
    )
    mock.get(APPLE_SUBMISSIONS).mock(side_effect=lambda request: next(replies))
    make_client(clock).get_json(APPLE_SUBMISSIONS)
    assert max(clock.sleeps) <= 30.0


def test_429_retries_at_most_twice_with_default_backoff(clock: FakeClock, mock) -> None:
    route = mock.get(APPLE_SUBMISSIONS).respond(429)
    with pytest.raises(SecUnavailable) as caught:
        make_client(clock).get_json(APPLE_SUBMISSIONS)
    assert route.call_count == 3  # first try + 2 retries
    assert clock.sleeps == [pytest.approx(2.0), pytest.approx(4.0)]
    assert caught.value.upstream_status == 429


def test_403_is_not_retried(clock: FakeClock, mock) -> None:
    route = mock.get(APPLE_SUBMISSIONS).respond(403)
    with pytest.raises(SecRefused) as caught:
        make_client(clock).get_json(APPLE_SUBMISSIONS)
    assert route.call_count == 1
    assert str(caught.value) == "SEC refused the request (403)"


def test_timeout_is_reported_without_retry(clock: FakeClock, mock) -> None:
    route = mock.get(APPLE_SUBMISSIONS).mock(side_effect=httpx.ReadTimeout("slow"))
    with pytest.raises(SecUnavailable):
        make_client(clock).get_json(APPLE_SUBMISSIONS)
    assert route.call_count == 1


def test_client_uses_a_20_second_timeout(clock: FakeClock) -> None:
    assert make_client(clock).timeout_seconds == 20.0
