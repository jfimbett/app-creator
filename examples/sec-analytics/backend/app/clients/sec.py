"""Minimal, polite SEC EDGAR client (brief §7; architecture.md "SEC client rules").

Used by the running app in live mode (through `data/source.py`), by
`scripts/capture_fixtures.py` and by `scripts/live_sec_smoke.py`. Thread-safe: FastAPI runs the
sync endpoints in a thread pool, and this client lets one request out at a time. Single flight and
the disk cache are in `data/`.

Rules this module enforces:
- Allowlist: HTTPS, two hosts, fixed path patterns, no query, userinfo or port. URLs are built
  from a normalized CIK, never taken from a caller. Redirects are followed by hand (at most 3),
  each target checked before any request. This is not a URL proxy.
- Fair access: declared User-Agent from `SEC_USER_AGENT` (passed in, never logged), at most one
  request per second by default (`max_requests_per_second`), one in flight, 20 s timeout.
- Failures: on 429/503 wait for Retry-After (capped at 30 s; default 2 s then 4 s) and retry at most
  twice; on 403 never retry.

Sources read 2026-11-03: https://www.sec.gov/os/accessing-edgar-data (User-Agent, 10 req/s) and
https://www.sec.gov/search-filings/edgar-application-programming-interfaces (endpoints, no CORS);
summary in docs/research/sec-edgar.md.
"""

from __future__ import annotations

import re
import threading
import time
from collections.abc import Callable
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Any
from urllib.parse import urljoin, urlsplit

import httpx

from app.logic.cik import normalize_cik

TIMEOUT_SECONDS = 20.0
DEFAULT_REQUESTS_PER_SECOND = 1.0
MAX_RETRIES = 2
DEFAULT_BACKOFF_SECONDS = (2.0, 4.0)
MAX_RETRY_AFTER_SECONDS = 30.0
MAX_REDIRECTS = 3
RETRY_STATUSES = frozenset({429, 503})

COMPANY_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"

ALLOWED_PATHS: dict[str, tuple[re.Pattern[str], ...]] = {
    "data.sec.gov": (
        re.compile(r"/submissions/CIK[0-9]{10}\.json"),
        re.compile(r"/submissions/CIK[0-9]{10}-submissions-[0-9]{3}\.json"),
        re.compile(r"/api/xbrl/companyfacts/CIK[0-9]{10}\.json"),
    ),
    "www.sec.gov": (
        re.compile(r"/files/company_tickers\.json"),
        re.compile(r"/Archives/edgar/data/[0-9]+/[0-9]{18}/[A-Za-z0-9._-]+"),
    ),
}

_EMAIL = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")
_CONTACT_HELP = (
    "SEC_USER_AGENT is missing or malformed. Set it yourself, in your environment or the "
    "git-ignored root .env (see .env.example), to your app name and your own contact email."
)


class SecError(Exception):
    """Base class. `code` is a stable error code; `upstream_status` is SEC's HTTP status, if any."""

    code = "sec_error"

    def __init__(self, message: str, upstream_status: int | None = None) -> None:
        super().__init__(message)
        self.upstream_status = upstream_status


class SecContactNotConfigured(SecError):
    """No usable `SEC_USER_AGENT`; no request was made."""

    code = "sec_contact_not_configured"


class UpstreamNotAllowed(SecError):
    """A URL or redirect target is not on the allowlist; no request was made to it."""

    code = "upstream_not_allowed"


class SecRefused(SecError):
    """SEC answered 403. Never retried or worked around."""

    code = "sec_refused"


class SecNotFound(SecError):
    """SEC answered 404."""

    code = "sec_not_found"


class SecUnavailable(SecError):
    """Timeout, network failure, retries exhausted or an unexpected answer."""

    code = "sec_unavailable"


class SecRateLimited(SecUnavailable):
    """SEC kept limiting us after the retries. `retry_after` is the advised wait in seconds."""

    code = "sec_rate_limited"

    def __init__(
        self, message: str, retry_after: float, upstream_status: int | None = None
    ) -> None:
        super().__init__(message, upstream_status=upstream_status)
        self.retry_after = retry_after


def submissions_url(cik: str) -> str:
    """Submissions JSON URL for a CIK in any accepted form (raises `InvalidCik`)."""
    return f"https://data.sec.gov/submissions/CIK{normalize_cik(cik)}.json"


def companyfacts_url(cik: str) -> str:
    """Company Facts JSON URL for a CIK in any accepted form (raises `InvalidCik`)."""
    return f"https://data.sec.gov/api/xbrl/companyfacts/CIK{normalize_cik(cik)}.json"


def check_allowed(url: str) -> None:
    """Raise `UpstreamNotAllowed` unless `url` is exactly an allowlisted SEC URL."""
    if not _is_allowed(url):
        raise UpstreamNotAllowed("This address is not on the SEC allowlist")


def _is_allowed(url: str) -> bool:
    """True when `url` is HTTPS, a listed host with no userinfo/port/query, and a listed path."""
    if not isinstance(url, str) or not url.isascii() or not url.isprintable() or " " in url:
        return False  # urlsplit silently drops tabs and newlines, so check the raw text first
    if "?" in url or "#" in url:
        return False
    parts = urlsplit(url)
    patterns = ALLOWED_PATHS.get(parts.netloc)  # exact netloc: rejects userinfo and any port
    if parts.scheme != "https" or patterns is None:
        return False
    if any(segment in {".", ".."} for segment in parts.path.split("/")):
        return False
    return any(pattern.fullmatch(parts.path) for pattern in patterns)


def validate_user_agent(value: str | None) -> str:
    """Return the trimmed User-Agent, or raise `SecContactNotConfigured` (value never echoed).

    Shape: two or more words, one of which looks like an email address, no control characters.
    """
    if not isinstance(value, str) or not value.isprintable():
        raise SecContactNotConfigured(_CONTACT_HELP)
    words = value.split()
    if len(words) < 2 or not any(_EMAIL.fullmatch(word) for word in words):
        raise SecContactNotConfigured(_CONTACT_HELP)
    return value.strip()


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class SecClient:
    """Throttled, allowlisted SEC fetcher. One instance per process; safe across threads."""

    def __init__(
        self,
        user_agent: str | None,
        *,
        transport: httpx.BaseTransport | None = None,
        clock: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], None] = time.sleep,
        wall_clock: Callable[[], datetime] = _utc_now,
        max_requests_per_second: float = DEFAULT_REQUESTS_PER_SECOND,
    ) -> None:
        self._user_agent = user_agent
        self._min_interval = 1.0 / max_requests_per_second
        self._clock = clock
        self._sleep = sleep
        self._wall_clock = wall_clock
        self._lock = threading.Lock()  # one request in flight
        self._last_start: float | None = None
        self._http = httpx.Client(
            timeout=TIMEOUT_SECONDS, follow_redirects=False, transport=transport
        )

    def __repr__(self) -> str:
        return "SecClient(user_agent=<hidden>)"

    def __enter__(self) -> SecClient:
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()

    def close(self) -> None:
        """Close the underlying HTTP connections."""
        self._http.close()

    @property
    def timeout_seconds(self) -> float:
        return TIMEOUT_SECONDS

    def get_json(self, url: str) -> Any:
        """Fetch an allowlisted URL and return its parsed JSON body."""
        response = self.fetch(url)
        try:
            return response.json()
        except ValueError as exc:
            raise SecUnavailable("SEC sent a response that is not JSON") from exc

    def fetch(self, url: str) -> httpx.Response:
        """Fetch an allowlisted URL, following up to 3 allowlisted redirects by hand."""
        check_allowed(url)
        headers = {
            "User-Agent": validate_user_agent(self._user_agent),
            "Accept-Encoding": "gzip, deflate",
        }
        with self._lock:
            for _ in range(MAX_REDIRECTS + 1):
                response = self._get_with_retries(url, headers)
                if not response.is_redirect:
                    return _checked(response)
                url = urljoin(url, response.headers["Location"])
                check_allowed(url)
        raise UpstreamNotAllowed("SEC redirected more than 3 times")

    def _get_with_retries(self, url: str, headers: dict[str, str]) -> httpx.Response:
        """GET once, then retry up to twice on 429/503 after the advised wait."""
        for attempt in range(MAX_RETRIES + 1):
            response = self._send(url, headers)
            if response.status_code not in RETRY_STATUSES:
                return response
            if attempt == MAX_RETRIES:
                break
            self._sleep(self._retry_delay(response, attempt))
        return self._raise_exhausted(response)

    def _raise_exhausted(self, response: httpx.Response) -> httpx.Response:
        """Retries used up. 429, or 503 with Retry-After, is limiting; a bare 503 is an outage."""
        status = response.status_code
        if status == 429 or response.headers.get("Retry-After"):
            wait = self._retry_delay(response, MAX_RETRIES - 1)
            raise SecRateLimited(
                f"SEC is limiting requests; try again in {wait:.0f} s", wait, upstream_status=status
            )
        raise SecUnavailable(f"SEC is busy ({status}); try again later", upstream_status=status)

    def _send(self, url: str, headers: dict[str, str]) -> httpx.Response:
        """One throttled GET. Network failures become `SecUnavailable` (no retry)."""
        self._wait_for_slot()
        try:
            return self._http.get(url, headers=headers)
        except httpx.TimeoutException as exc:
            raise SecUnavailable("SEC did not answer within 20 seconds") from exc
        except httpx.TransportError as exc:
            raise SecUnavailable("SEC could not be reached") from exc

    def _wait_for_slot(self) -> None:
        """Sleep until the minimum interval has passed since the previous request started."""
        if self._last_start is not None:
            remaining = self._last_start + self._min_interval - self._clock()
            if remaining > 0:
                self._sleep(remaining)
        self._last_start = self._clock()

    def _retry_delay(self, response: httpx.Response, attempt: int) -> float:
        """Seconds to wait: Retry-After (seconds or HTTP date) capped at 30 s, else 2 s / 4 s."""
        advised = _parse_retry_after(response.headers.get("Retry-After"), self._wall_clock())
        if advised is None:
            return DEFAULT_BACKOFF_SECONDS[attempt]
        return min(max(advised, 0.0), MAX_RETRY_AFTER_SECONDS)


def _parse_retry_after(value: str | None, now: datetime) -> float | None:
    """Retry-After as seconds from `now`, or None when absent or unreadable."""
    if not value:
        return None
    value = value.strip()
    if value.isdigit():
        return float(value)
    try:
        when = parsedate_to_datetime(value)
    except (TypeError, ValueError):
        return None
    if when.tzinfo is None:
        when = when.replace(tzinfo=timezone.utc)
    return (when - now).total_seconds()


def _checked(response: httpx.Response) -> httpx.Response:
    """Return a 2xx response; map other statuses to clear errors."""
    status = response.status_code
    if 200 <= status < 300:
        return response
    if status == 403:
        raise SecRefused("SEC refused the request (403)", upstream_status=403)
    if status == 404:
        raise SecNotFound("SEC has no such document (404)", upstream_status=404)
    raise SecUnavailable(f"SEC answered with status {status}", upstream_status=status)
