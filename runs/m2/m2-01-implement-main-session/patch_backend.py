#!/usr/bin/env python3
"""Exact edits to existing backend files for M2 (kept as a record). Run from the repo root."""
BE = "examples/sec-analytics/backend/app/"


def sub(path, pairs):
    p = BE + path
    s = open(p).read()
    for old, new in pairs:
        assert old in s, (path, old[:50])
        s = s.replace(old, new, 1)
    open(p, "w").write(s)


sub("clients/sec.py", [
    ('''At M1 only `scripts/capture_fixtures.py` uses it; the running app does not import it.
''', '''Used by the running app in live mode (through `data/source.py`), by `scripts/capture_fixtures.py`
and by `scripts/live_sec_smoke.py`. Thread-safe: FastAPI runs the sync endpoints in a thread pool, and
this client lets one request out at a time. Single flight and the disk cache are in `data/`.
'''),
    ('''  request per second, one request in flight, 20 s timeout.
''', '''  request per second by default (`max_requests_per_second`), one in flight, 20 s timeout.
'''),
    ('''# At most 1 request per second; SEC_MAX_REQUESTS_PER_SECOND arrives in M2.
MIN_INTERVAL_SECONDS = 1.0
''', '''DEFAULT_REQUESTS_PER_SECOND = 1.0
'''),
    ('''class SecNotFound(SecError):''', '''class SecRateLimited(SecUnavailable):
    """SEC kept limiting us after the retries. `retry_after` is the advised wait in seconds."""

    code = "sec_rate_limited"

    def __init__(self, message: str, retry_after: float, upstream_status: int | None = None) -> None:
        super().__init__(message, upstream_status=upstream_status)
        self.retry_after = retry_after


class SecNotFound(SecError):'''),
    ('''        wall_clock: Callable[[], datetime] = _utc_now,
    ) -> None:
        self._user_agent = user_agent
''', '''        wall_clock: Callable[[], datetime] = _utc_now,
        max_requests_per_second: float = DEFAULT_REQUESTS_PER_SECOND,
    ) -> None:
        self._user_agent = user_agent
        self._min_interval = 1.0 / max_requests_per_second
'''),
    ('''            self._sleep(self._retry_delay(response, attempt))
        raise SecUnavailable(
            f"SEC is busy ({response.status_code}); try again later",
            upstream_status=response.status_code,
        )
''', '''            self._sleep(self._retry_delay(response, attempt))
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
'''),
    ('''        """Sleep until at least MIN_INTERVAL_SECONDS have passed since the previous request."""
''', '''        """Sleep until the minimum interval has passed since the previous request started."""
'''),
    ('''            remaining = self._last_start + MIN_INTERVAL_SECONDS - self._clock()
''', '''            remaining = self._last_start + self._min_interval - self._clock()
'''),
])

sub("errors.py", [
    ('''from starlette.exceptions import HTTPException as StarletteHTTPException
''', '''from starlette.exceptions import HTTPException as StarletteHTTPException

from app.clients.sec import (
    SecContactNotConfigured,
    SecError,
    SecNotFound,
    SecRateLimited,
    SecRefused,
    UpstreamNotAllowed,
)
'''),
    ('''_CODE_BY_PARAM = {"q": "invalid_query", "limit": "invalid_query", "cik": "invalid_cik"}
''', '''_CODE_BY_PARAM = {
    "q": "invalid_query",
    "limit": "invalid_query",
    "cik": "invalid_cik",
    "years": "invalid_years",
}
'''),
    ('''    "invalid_request": "The request has an invalid parameter.",
''', '''    "invalid_request": "The request has an invalid parameter.",
    "invalid_years": "Choose from 5 to 10 years.",
'''),
    ('''async def _unexpected_error(request''', '''NOT_CONFIGURED_MESSAGE = (
    "Live SEC data is not configured: set SEC_USER_AGENT (see .env.example and docs/SETUP.md)"
)


async def _sec_error(_: Request, exc: SecError) -> JSONResponse:
    """Map a client error to the API's codes. The configured contact is never in a message."""
    if isinstance(exc, SecContactNotConfigured):
        return error_response(503, exc.code, NOT_CONFIGURED_MESSAGE, {"setting": "SEC_USER_AGENT"})
    if isinstance(exc, SecRateLimited):
        wait = round(exc.retry_after)
        message = f"SEC is limiting requests; try again in {wait} s"
        return error_response(503, exc.code, message, {"retry_after": wait})
    if isinstance(exc, SecRefused):
        message = "SEC refused the request (403). The app does not retry refused requests."
        return error_response(502, exc.code, message)
    if isinstance(exc, UpstreamNotAllowed):
        message = "SEC pointed to an address outside the allowlist, so it was not requested."
        return error_response(502, exc.code, message)
    if isinstance(exc, SecNotFound):
        return error_response(404, "company_not_found", "SEC has no record for this CIK.")
    return error_response(502, "sec_unavailable", "SEC is unavailable right now")


async def _unexpected_error(request'''),
    ('''    app.add_exception_handler(AppError, _app_error)
''', '''    app.add_exception_handler(AppError, _app_error)
    app.add_exception_handler(SecError, _sec_error)
'''),
])

sub("models/common.py", [
    ('''"""Where the data in a response comes from. At M1 `mode` is always "demo"."""''',
     '''"""Where the data in a response comes from: recorded demo data, SEC just now, or the cache."""'''),
])

sub("models/companies.py", [
    ('''UNIVERSE_NOTE = "Search covers the demo companies only: Apple, Microsoft, Alphabet"
''', '''UNIVERSE_NOTE = "Search covers the demo companies only: Apple, Microsoft, Alphabet"
LIVE_UNIVERSE_NOTE = (
    "Live search covers SEC filers listed in the SEC ticker file; other filers can be opened by CIK."
)
'''),
])

sub("logic/search.py", [
    ('''from collections.abc import Iterable
''', '''from collections.abc import Iterable, Mapping
'''),
    ('''def search(query: str, universe''', '''def universe_from_tickers(tickers: Mapping) -> list[UniverseCompany]:
    """The searchable companies in SEC's ticker file, one per CIK, in file order.

    The file lists a company once per ticker. Rows lacking a CIK or ticker are skipped.
    """
    names: dict[str, str] = {}
    by_cik: dict[str, list[str]] = {}
    for row in tickers.values():
        if not isinstance(row, Mapping) or row.get("cik_str") is None or not row.get("ticker"):
            continue
        cik = str(row["cik_str"]).zfill(10)
        names.setdefault(cik, str(row.get("title") or f"CIK {cik}"))
        by_cik.setdefault(cik, []).append(str(row["ticker"]))
    return [UniverseCompany(cik, names[cik], tuple(by_cik[cik])) for cik in by_cik]


def search(query: str, universe'''),
])

sub("api/deps.py", [
    ('''from app.data.fixtures import FixtureStore
''', '''from app.data.fixtures import FixtureStore
from app.data.source import DataSource
'''),
    ('''def get_settings(request''', '''def get_data(request: Request) -> DataSource:
    """The per-app data layer (fixtures, cache, SEC)."""
    return request.app.state.data


def get_settings(request'''),
])

sub("api/meta.py", [
    ('''"""Data mode and demo universe. M1 has no live mode, so live is never available."""''',
     '''"""Data mode, whether live is offered and configured, and the demo universe."""'''),
    ('''        live_available=False,
        live_configured=False,
''', '''        live_available=settings.live_available,
        live_configured=settings.live_configured,
'''),
])

sub("main.py", [
    ('''Next.js forwards /api/* to this server (see frontend/next.config.ts). At M1 the app serves only
recorded fixtures and makes no network request.
''', '''Next.js forwards /api/* to this server (see frontend/next.config.ts). Recorded fixtures need no
network; live requests go to SEC only when a request asks for `source=live` (see data/source.py).
'''),
    ('''from app.api import companies, meta
from app.data.fixtures import FixtureError, FixtureStore
''', '''from app.api import companies, financials, meta
from app.clients.sec import SecClient
from app.data.fixtures import FixtureError, FixtureStore
from app.data.source import DataSource
'''),
    ('''def create_app(settings: Settings | None = None) -> FastAPI:
''', '''def create_app(settings: Settings | None = None, sec_client: SecClient | None = None) -> FastAPI:
'''),
    ('''    Raises `SettingsError` (naming the setting) when DATA_MODE or FIXTURES_DIR is unusable.
''', '''    Raises `SettingsError` (naming the setting) when DATA_MODE or FIXTURES_DIR is unusable.
    `sec_client` lets tests inject a client with a fake clock and sleep.
'''),
    ('''    application.state.store = store
''', '''    application.state.store = store
    application.state.data = DataSource(settings, store, sec_client)
'''),
    ('''    application.include_router(companies.router)
''', '''    application.include_router(companies.router)
    application.include_router(financials.router)
'''),
])

api = open(BE + "api/companies.py").read()
start = api.index('@router.get("/search"')
end = api.index("def _text(value: Any)")
api = api[:start] + '''SourceParam = Annotated[Literal["demo", "live"], Query(description="demo (default) or live")]


def _no_cik_result(query: str) -> list[SearchResult]:
    """A valid CIK missing from the ticker file can still be opened."""
    try:
        cik = normalize_cik(query)
    except InvalidCik:
        return []
    return [SearchResult(cik=cik, ticker="", name=NOT_IN_TICKER_FILE, match="cik")]


@router.get("/search", response_model=SearchResponse)
def search_companies(
    store: Annotated[FixtureStore, Depends(get_store)],
    data: Annotated[DataSource, Depends(get_data)],
    q: Annotated[str, Query(description="Name, ticker or CIK (1-100 characters)")],
    limit: Annotated[int, Query(ge=1, le=20)] = 10,
    source: SourceParam = "demo",
) -> SearchResponse:
    """Search by name, ticker or CIK: the demo universe, or SEC's ticker file in live mode."""
    query = _clean_query(q)
    if source == "live":
        tickers = data.ticker_map()
        matches = search(query, universe_from_tickers(tickers.data), limit)
        results = [SearchResult(cik=m.cik, ticker=m.ticker, name=m.name, match=m.match)
                   for m in matches]
        return SearchResponse(
            query=query,
            results=results or _no_cik_result(query),
            universe_note=LIVE_UNIVERSE_NOTE,
            source=tickers.source,
        )
    matches = search(query, store.universe(), limit)
    return SearchResponse(
        query=query,
        results=[SearchResult(cik=m.cik, ticker=m.ticker, name=m.name, match=m.match)
                 for m in matches],
        source=store.source_info(store.universe_files()),
    )


''' + api[end:]
api = api.replace('''from typing import Annotated, Any
''', '''from typing import Annotated, Any, Literal
''')
api = api.replace('''from app.api.deps import get_store
from app.data.fixtures import FixtureStore
''', '''from app.api.deps import get_data, get_store
from app.data.fixtures import FixtureStore
from app.data.source import DataSource
''')
api = api.replace('''from app.logic.search import search
''', '''from app.logic.search import search, universe_from_tickers
''')
api = api.replace('''from app.models.companies import (
    CompanyProfile,''', '''from app.models.companies import (
    LIVE_UNIVERSE_NOTE,
    CompanyProfile,''')
api = api.replace('''QUERY_MAX = 100
''', '''QUERY_MAX = 100
NOT_IN_TICKER_FILE = "Not in the SEC ticker file: open by CIK"
''')
start = api.index('@router.get("/{cik}", response_model=CompanyProfile)')
api = api[:start] + '''@router.get("/{cik}", response_model=CompanyProfile)
def company_profile(
    cik: str, data: Annotated[DataSource, Depends(get_data)], source: SourceParam = "demo"
) -> CompanyProfile:
    """Profile and SEC identifiers exactly as in the submissions file."""
    cik10 = parse_cik(cik)
    fetched = data.submissions(cik10, source)
    raw = fetched.data
    if raw is None:
        raise _not_found(cik10)
    return CompanyProfile(
        cik=cik10,
        name=raw["name"],
        tickers=list(raw.get("tickers") or []),
        exchanges=[e for e in raw.get("exchanges") or [] if e],
        sic=_text(raw.get("sic")),
        sic_description=_text(raw.get("sicDescription")),
        fiscal_year_end=_text(raw.get("fiscalYearEnd")),
        state_of_incorporation=_text(raw.get("stateOfIncorporation")),
        former_names=_former_names(raw.get("formerNames")),
        source=fetched.source,
    )


@router.get("/{cik}/overview", response_model=OverviewResponse)
def company_overview(
    cik: str,
    data: Annotated[DataSource, Depends(get_data)],
    years: Annotated[int | None, Query(ge=1, le=20, description="Latest N fiscal years")] = None,
    source: SourceParam = "demo",
) -> OverviewResponse:
    """Key figures and annual revenue / net income (whole currency units) from Company Facts."""
    cik10 = parse_cik(cik)
    fetched = data.companyfacts(cik10, source)
    if fetched.data is None:
        raise _not_found(cik10)
    result = overview(fetched.data, companyfacts_url(cik10), years)
    return OverviewResponse(
        cik=cik10,
        key_figures=result.key_figures,
        chart=result.chart,
        notes=result.notes,
        source=fetched.source,
    )
'''
api = api.replace('''from app.logic.cik import InvalidCik, normalize_cik
''', '''from app.clients.sec import companyfacts_url
from app.logic.cik import InvalidCik, normalize_cik
''')
open(BE + "api/companies.py", "w").write(api)
print("ok")
