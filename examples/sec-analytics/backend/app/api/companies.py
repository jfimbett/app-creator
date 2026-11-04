"""Company search, profile and overview over the demo snapshot."""

from typing import Annotated, Any, Literal

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_data, get_store
from app.clients.sec import companyfacts_url
from app.data.fixtures import FixtureStore
from app.data.source import DataSource
from app.errors import AppError
from app.logic.cik import InvalidCik, normalize_cik
from app.logic.search import search, universe_from_tickers
from app.logic.statements import overview
from app.models.companies import (
    LIVE_UNIVERSE_NOTE,
    CompanyProfile,
    FormerName,
    OverviewResponse,
    SearchResponse,
    SearchResult,
)

router = APIRouter(prefix="/api/companies", tags=["companies"])

QUERY_MAX = 100
NOT_IN_TICKER_FILE = "Not in the SEC ticker file: open by CIK"


def parse_cik(raw: str) -> str:
    """Normalize a CIK from the path, or raise a 422 `invalid_cik` AppError."""
    try:
        return normalize_cik(raw)
    except InvalidCik as exc:
        raise AppError("invalid_cik", str(exc), 422) from None


def _clean_query(q: str) -> str:
    """Trim the query and check it has 1-100 characters, else raise 422 `invalid_query`."""
    query = q.strip()
    if not 1 <= len(query) <= QUERY_MAX:
        raise AppError(
            "invalid_query",
            f"Type 1 to {QUERY_MAX} characters: a company name, ticker or CIK.",
            422,
            {"length": len(query)},
        )
    return query


SourceParam = Annotated[Literal["demo", "live"], Query(description="demo (default) or live")]


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


def _text(value: Any) -> str | None:
    """SEC uses "" for a field it does not report: keep it missing (None), never invent text."""
    return value if isinstance(value, str) and value.strip() else None


def _former_names(raw: list[dict[str, Any]] | None) -> list[FormerName]:
    return [
        FormerName(name=item["name"], from_=item.get("from"), to=item.get("to"))
        for item in raw or []
    ]


def _not_found(cik10: str) -> AppError:
    """404 `company_not_found` for a valid CIK outside the demo snapshot."""
    return AppError(
        "company_not_found",
        f"CIK {cik10} is not in the demo snapshot (Apple, Microsoft, Alphabet).",
        404,
        {"cik": cik10},
    )


@router.get("/{cik}", response_model=CompanyProfile)
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
