"""Where each request's data comes from (fixtures, disk cache or SEC) and how it is labelled.

The rules (brief §3, §7):

- `source="demo"` always answers from the fixtures. `source="live"` answers from the cache or SEC.
- Live under DATA_MODE=fixtures is refused (409 `live_disabled`).
- A live failure raises an error. It never falls back to fixtures: only the person can switch mode.
- A response is labelled `LIVE · retrieved <time>` or `CACHED · retrieved <date>`; when several
  sources are combined, the oldest retrieval time is shown.
- Identical concurrent requests share one upstream call (single flight). No prefetching.
"""

from __future__ import annotations

from collections.abc import Callable
from concurrent.futures import Future
from dataclasses import dataclass
from datetime import datetime
from threading import Lock
from typing import Any, Literal

from app.clients import sec
from app.clients.sec import SecClient, SecNotFound, validate_user_agent
from app.data.cache import DiskCache, utc_now
from app.data.fixtures import FixtureStore
from app.errors import AppError
from app.models.common import SourceInfo
from app.settings import Settings

SourceChoice = Literal["demo", "live"]
LIVE_LABEL = "LIVE"
CACHED_LABEL = "CACHED"


@dataclass(frozen=True)
class Fetched:
    """Data plus where it came from. `data` is None for a demo company outside the snapshot."""

    data: Any
    source: SourceInfo


def _live_source(url: str, retrieved_at: datetime, *, cached: bool) -> SourceInfo:
    """The SourceInfo of one live or cached response."""
    if cached:
        label = f"{CACHED_LABEL} · retrieved {retrieved_at:%Y-%m-%d}"
    else:
        label = f"{LIVE_LABEL} · retrieved {retrieved_at:%Y-%m-%d %H:%M} UTC"
    return SourceInfo(
        mode="cached" if cached else "live",
        label=label,
        retrieved_at=retrieved_at,
        snapshot_date=None,
        source_urls=[url],
    )


def combine_sources(sources: list[SourceInfo]) -> SourceInfo:
    """One SourceInfo for a response built from several: the oldest retrieval is the one shown."""
    first = sources[0]
    urls = [url for item in sources for url in item.source_urls]
    if first.mode == "demo" or len(sources) == 1:
        return first.model_copy(update={"source_urls": urls})
    oldest = min(sources, key=lambda item: item.retrieved_at)
    cached = any(item.mode == "cached" for item in sources)
    combined = _live_source(urls[0], oldest.retrieved_at, cached=cached)
    return combined.model_copy(update={"source_urls": urls})


class DataSource:
    """Fetches the three SEC documents the app uses, for one app instance."""

    def __init__(
        self,
        settings: Settings,
        store: FixtureStore,
        client: SecClient | None = None,
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        self._settings = settings
        self._store = store
        self._client = client
        self._clock = clock
        self._cache = DiskCache(settings.sec_cache_dir, clock)
        self._lock = Lock()
        self._in_flight: dict[str, Future] = {}

    def _user_agent(self) -> str | None:
        secret = self._settings.sec_user_agent
        return secret.get_secret_value() if secret else None

    def _sec(self) -> SecClient:
        """The shared client, created on first live use (one throttle per running app)."""
        with self._lock:
            if self._client is None:
                self._client = SecClient(
                    self._user_agent(),
                    max_requests_per_second=self._settings.sec_max_requests_per_second,
                )
            return self._client

    def _require_live(self) -> None:
        """Refuse live when it is off, and when no contact is set, even if a cache exists."""
        if not self._settings.live_available:
            raise AppError(
                "live_disabled",
                "Live data is off in this run of the app (DATA_MODE=fixtures). "
                "Start it with npm run dev to use live SEC data.",
                409,
            )
        if self._client is None:
            validate_user_agent(self._user_agent())

    def _fetch_or_cached(self, url: str) -> Fetched:
        """Cache first, otherwise one upstream call that is then stored."""
        entry = self._cache.get(url)
        if entry is not None:
            return Fetched(entry.body, _live_source(url, entry.retrieved_at, cached=True))
        body = self._sec().get_json(url)
        stored = self._cache.put(url, body)
        return Fetched(body, _live_source(url, stored.retrieved_at, cached=False))

    def _live(self, url: str) -> Fetched:
        """Single flight: concurrent callers for one URL share the leader's result or error."""
        self._require_live()
        with self._lock:
            flight = self._in_flight.get(url)
            leader = flight is None
            if leader:
                flight = Future()
                self._in_flight[url] = flight
        if not leader:
            return flight.result()
        try:
            result = self._fetch_or_cached(url)
        except BaseException as exc:
            flight.set_exception(exc)
            raise
        else:
            flight.set_result(result)
            return result
        finally:
            with self._lock:
                self._in_flight.pop(url, None)

    def ticker_map(self) -> Fetched:
        """SEC's ticker file (live only: the demo universe comes from the fixtures)."""
        return self._live(sec.COMPANY_TICKERS_URL)

    def submissions(self, cik: str, source: SourceChoice) -> Fetched:
        """A company's submissions document; demo data is None when outside the snapshot."""
        if source == "live":
            return self._live(sec.submissions_url(cik))
        path = self._store.submissions_path(cik)
        data = self._store.submissions(cik)
        if data is None:
            return Fetched(None, self._store.source_info([]))
        return Fetched(data, self._store.source_info([path]))

    def companyfacts(self, cik: str, source: SourceChoice) -> Fetched:
        """A company's Company Facts document; demo data is None when outside the snapshot."""
        if source == "live":
            try:
                return self._live(sec.companyfacts_url(cik))
            except SecNotFound:
                raise AppError(
                    "company_not_found",
                    f"SEC has no Company Facts for CIK {cik}; this filer may not report XBRL data.",
                    404,
                    {"cik": cik},
                ) from None
        path = self._store.companyfacts_path(cik)
        data = self._store.companyfacts(cik)
        if data is None:
            return Fetched(None, self._store.source_info([]))
        return Fetched(data, self._store.source_info([path]))
