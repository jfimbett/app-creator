"""Company search over a small universe (pure: no files, network or clock).

Ranking (brief §8): exact ticker, then CIK, then ticker prefix, then name substring; ties by
name. One result per CIK, so a company with several tickers (Alphabet) appears once.

- Ticker: case-insensitive; exact beats prefix.
- CIK: any zero-padding, optional "CIK" prefix, 1-10 digits (see `normalize_cik`).
- Name: case-insensitive substring of the SEC company name.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from app.logic.cik import InvalidCik, normalize_cik

_TICKER_EXACT, _CIK, _TICKER_PREFIX, _NAME = range(4)


@dataclass(frozen=True)
class UniverseCompany:
    """A searchable company. `tickers` lists the primary ticker first."""

    cik: str
    name: str
    tickers: tuple[str, ...]

    @property
    def primary_ticker(self) -> str:
        """The first ticker, or "" when SEC lists none."""
        return self.tickers[0] if self.tickers else ""


@dataclass(frozen=True)
class Match:
    """One search result; `ticker` is the ticker that matched, else the primary ticker."""

    cik: str
    ticker: str
    name: str
    match: str  # "ticker" | "cik" | "name"


def _query_cik(query: str) -> str | None:
    """The 10-digit CIK the query stands for, or None if it is not a CIK."""
    try:
        return normalize_cik(query)
    except InvalidCik:
        return None


def _best_match(company: UniverseCompany, query: str, cik: str | None) -> tuple[int, Match] | None:
    """Return (rank, match) for the company's best way of matching `query`, or None."""
    needle = query.casefold()
    tickers = [t for t in company.tickers if t]
    exact = next((t for t in tickers if t.casefold() == needle), None)
    if exact:
        return _TICKER_EXACT, Match(company.cik, exact, company.name, "ticker")
    if cik is not None and cik == company.cik:
        return _CIK, Match(company.cik, company.primary_ticker, company.name, "cik")
    prefix = next((t for t in tickers if t.casefold().startswith(needle)), None)
    if prefix:
        return _TICKER_PREFIX, Match(company.cik, prefix, company.name, "ticker")
    if needle in company.name.casefold():
        return _NAME, Match(company.cik, company.primary_ticker, company.name, "name")
    return None


def search(query: str, universe: Iterable[UniverseCompany], limit: int) -> list[Match]:
    """Return at most `limit` matches for `query`, best first, one per CIK."""
    query = query.strip()
    if not query or limit < 1:
        return []
    cik = _query_cik(query)
    ranked = []
    seen: set[str] = set()
    for company in universe:
        if company.cik in seen:
            continue
        seen.add(company.cik)
        found = _best_match(company, query, cik)
        if found:
            ranked.append(found)
    ranked.sort(key=lambda item: (item[0], item[1].name.casefold(), item[1].cik))
    return [match for _, match in ranked[:limit]]
