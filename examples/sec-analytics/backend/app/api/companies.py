"""Company search and profile over the demo snapshot (overview arrives in step m1-07b)."""

from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_store
from app.data.fixtures import FixtureStore
from app.errors import AppError
from app.logic.cik import InvalidCik, normalize_cik
from app.logic.search import search
from app.models.companies import CompanyProfile, FormerName, SearchResponse, SearchResult

router = APIRouter(prefix="/api/companies", tags=["companies"])

QUERY_MAX = 100


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


@router.get("/search", response_model=SearchResponse)
def search_companies(
    store: Annotated[FixtureStore, Depends(get_store)],
    q: Annotated[str, Query(description="Name, ticker or CIK (1-100 characters)")],
    limit: Annotated[int, Query(ge=1, le=20)] = 10,
) -> SearchResponse:
    """Search the demo universe by name, ticker or CIK."""
    query = _clean_query(q)
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


@router.get("/{cik}", response_model=CompanyProfile)
def company_profile(
    cik: str, store: Annotated[FixtureStore, Depends(get_store)]
) -> CompanyProfile:
    """Profile and SEC identifiers exactly as in the recorded submissions file."""
    cik10 = parse_cik(cik)
    raw = store.submissions(cik10)
    if raw is None:
        raise AppError(
            "company_not_found",
            f"CIK {cik10} is not in the demo snapshot (Apple, Microsoft, Alphabet).",
            404,
            {"cik": cik10},
        )
    return CompanyProfile(
        cik=cik10,
        name=raw["name"],
        tickers=list(raw.get("tickers") or []),
        exchanges=list(raw.get("exchanges") or []),
        sic=_text(raw.get("sic")),
        sic_description=_text(raw.get("sicDescription")),
        fiscal_year_end=_text(raw.get("fiscalYearEnd")),
        state_of_incorporation=_text(raw.get("stateOfIncorporation")),
        former_names=_former_names(raw.get("formerNames")),
        source=store.source_info([store.submissions_path(cik10)]),
    )
