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

from collections import OrderedDict
from collections.abc import Callable
from concurrent.futures import Future
from dataclasses import dataclass
from datetime import date, datetime
from threading import Lock
from typing import Any, Literal

from app.clients import sec
from app.clients.sec import SecClient, SecDocumentTooLarge, SecNotFound, validate_user_agent
from app.data.cache import DiskCache, DocumentCache, utc_now
from app.data.fixtures import FixtureStore
from app.errors import AppError
from app.logic import filings as filing_logic
from app.logic.sanitize import SanitizedDocument, to_blocks
from app.logic.sections import SectionResult, detect_sections
from app.models.common import SourceInfo
from app.models.filings import FilingMeta
from app.settings import Settings

SourceChoice = Literal["demo", "live"]
LIVE_LABEL = "LIVE"
CACHED_LABEL = "CACHED"
MAX_DOCUMENT_BYTES = 20 * 1024 * 1024
MAX_OLDER_PAGES = 6
READABLE_SUFFIXES = (".htm", ".html", ".xhtml", ".txt", ".xml")
PARSED_DOCUMENTS_KEPT = 8


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


@dataclass(frozen=True)
class FilingList:
    """All 10-K and 10-Q rows found for a company, how they were read and where they came from."""

    rows: list[FilingMeta]
    source: SourceInfo
    listed_at: datetime | None
    pages_missing: bool


@dataclass(frozen=True)
class ParsedFiling:
    """A filing document as sanitized text, its sections and its retrieval details."""

    document: SanitizedDocument
    sections: SectionResult
    source: SourceInfo
    retrieved_at: datetime


class DataSource:
    """Fetches the SEC documents the app uses, for one app instance."""

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
        self._documents = DocumentCache(settings.sec_cache_dir, clock)
        self._parsed: OrderedDict[str, tuple[SanitizedDocument, SectionResult]] = OrderedDict()
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
        """Live JSON document: cache or SEC, one upstream call for concurrent requests."""
        self._require_live()
        return self._single_flight(url, lambda: self._fetch_or_cached(url))

    def _single_flight(self, key: str, work: Callable[[], Any]) -> Any:
        """Concurrent callers for one key share the leader's result or error."""
        with self._lock:
            flight = self._in_flight.get(key)
            leader = flight is None
            if leader:
                flight = Future()
                self._in_flight[key] = flight
        if not leader:
            return flight.result()
        try:
            result = work()
        except BaseException as exc:
            flight.set_exception(exc)
            raise
        else:
            flight.set_result(result)
            return result
        finally:
            with self._lock:
                self._in_flight.pop(key, None)

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

    def filing_list(self, cik: str, source: SourceChoice, today: date) -> FilingList | None:
        """Every 10-K/10-Q row in the 10-year window and beyond it, if already read.

        None for a demo company outside the snapshot. Live reads SEC's older pages only when the
        recent table falls short of the window, one at a time through the throttled client.
        """
        fetched = self.submissions(cik, source)
        if fetched.data is None:
            return None
        filings = fetched.data.get("filings") or {}
        recent = filings.get("recent") or {}
        tables = [filing_logic.parse_rows(recent, cik)]
        pages_missing = False
        if source == "demo":
            tables += [filing_logic.parse_rows(p, cik) for p in self._store.submission_pages(cik)]
            listed_at = self._store.retrieved_at(self._store.submissions_path(cik))
        else:
            listed_at = fetched.source.retrieved_at
            start = filing_logic.window_start(today, filing_logic.MAX_YEARS)
            names = filing_logic.older_pages_needed(recent, filings.get("files"), start)
            pages_missing = len(names) > MAX_OLDER_PAGES
            for name in names[:MAX_OLDER_PAGES]:
                table = self._older_page(name)
                if table is None:
                    pages_missing = True
                else:
                    tables.append(filing_logic.parse_rows(table, cik))
        rows = filing_logic.merge_rows(*tables)
        if source == "demo":
            rows = [
                row.model_copy(update={"document_in_snapshot": self._store.has_filing_document(
                    cik, row.accession, row.primary_document)})
                for row in rows
            ]
        return FilingList(rows, fetched.source, listed_at, pages_missing)

    def _older_page(self, name: str) -> dict[str, Any] | None:
        """One older submissions page. A page SEC no longer has is reported as missing history."""
        try:
            data = self._live(f"https://data.sec.gov/submissions/{name}").data
        except (SecNotFound, sec.UpstreamNotAllowed):
            return None
        return data if isinstance(data, dict) else None

    def parsed_filing(self, cik: str, filing: FilingMeta, source: SourceChoice) -> ParsedFiling:
        """A filing's primary document as sanitized blocks with sections.

        Reached only with a row from the company's own list, so its address is built from SEC's
        data.
        """
        details = {"source_link": filing.document_url, "index_url": filing.index_url}
        if filing.primary_document is None or filing.document_url is None:
            raise AppError(
                "document_unavailable",
                "SEC lists no primary document for this filing. Open its index page on sec.gov.",
                404,
                details,
            )
        if not filing.primary_document.lower().endswith(READABLE_SUFFIXES):
            raise AppError(
                "document_unavailable",
                "This filing's primary document is not a text format the reader can show. "
                "Open it on sec.gov.",
                404,
                details,
            )
        if source == "demo" and not self._store.has_filing_document(
            cik, filing.accession, filing.primary_document
        ):
            raise AppError(
                "document_not_in_snapshot",
                "This filing's document is not in the recorded demo snapshot",
                404,
                details,
            )
        if source == "live":
            self._require_live()
        key = f"document:{source}:{filing.document_url}"
        return self._single_flight(key, lambda: self._read_filing(cik, filing, source, details))

    def _read_filing(
        self, cik: str, filing: FilingMeta, source: SourceChoice, details: dict[str, Any]
    ) -> ParsedFiling:
        url = filing.document_url
        if source == "demo":
            path = self._store.filing_document_path(cik, filing.accession, filing.primary_document)
            raw = self._store.filing_document(path)
            info = self._store.source_info([path])
            retrieved_at = self._store.retrieved_at(path)
        else:
            raw, info, retrieved_at = self._live_document(url, details)
        document, sections = self._parse(filing, raw, details)
        return ParsedFiling(document, sections, info, retrieved_at)

    def _parse(
        self, filing: FilingMeta, raw: bytes, details: dict[str, Any]
    ) -> tuple[SanitizedDocument, SectionResult]:
        """Text and sections, kept in memory: the same bytes always give the same result."""
        key = filing.document_url
        with self._lock:
            kept = self._parsed.get(key)
        if kept is not None:
            return kept
        document = to_blocks(raw, filing.primary_document)
        if not document.blocks:
            raise AppError(
                "document_unavailable",
                "No readable text was found in this document. Open it on sec.gov.",
                404,
                details,
            )
        parsed = (document, detect_sections(document.blocks, filing.form))
        with self._lock:
            self._parsed[key] = parsed
            while len(self._parsed) > PARSED_DOCUMENTS_KEPT:
                self._parsed.popitem(last=False)
        return parsed

    def _live_document(
        self, url: str, details: dict[str, Any]
    ) -> tuple[bytes, SourceInfo, datetime]:
        """The document from the permanent cache, or once from SEC (bounded while it is read)."""
        cached = self._documents.get(url)
        if cached is not None:
            info = _live_source(url, cached.retrieved_at, cached=True)
            return cached.content, info, cached.retrieved_at
        try:
            content = self._sec().fetch(url, max_bytes=MAX_DOCUMENT_BYTES).content
        except SecDocumentTooLarge:
            raise AppError(
                "document_too_large",
                "This document is over the reader's 20 MB limit. Open it on sec.gov.",
                413,
                details,
            ) from None
        except SecNotFound:
            raise AppError(
                "document_unavailable",
                "SEC has no document at this address right now. Try its index page on sec.gov.",
                404,
                details,
            ) from None
        stored = self._documents.put(url, content)
        return content, _live_source(url, stored.retrieved_at, cached=False), stored.retrieved_at
