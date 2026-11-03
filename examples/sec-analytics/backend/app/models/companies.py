"""Response shapes of /api/meta and /api/companies/* (brief §5, "API at M1")."""

from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.models.common import MetricValue, SourceInfo

UNIVERSE_NOTE = "Search covers the demo companies only: Apple, Microsoft, Alphabet"


class DemoCompany(BaseModel):
    """One company of the demo universe, with its primary ticker."""

    cik: str
    ticker: str
    name: str


class MetaResponse(BaseModel):
    """GET /api/meta: data mode, snapshot date and the demo universe."""

    data_mode: Literal["fixtures", "live"]
    live_available: bool
    live_configured: bool
    snapshot_date: date
    demo_universe: list[DemoCompany]


class SearchResult(BaseModel):
    """One search hit; `match` says which field matched."""

    cik: str
    ticker: str
    name: str
    match: Literal["ticker", "name", "cik"]


class SearchResponse(BaseModel):
    """GET /api/companies/search."""

    query: str
    results: list[SearchResult]
    universe_note: str = UNIVERSE_NOTE
    source: SourceInfo


class FormerName(BaseModel):
    """A former company name with the dates exactly as in the SEC submissions file."""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    name: str
    from_: str | None = Field(default=None, alias="from")
    to: str | None = None


class CompanyProfile(BaseModel):
    """GET /api/companies/{cik}: identifiers exactly as in the submissions file.

    Empty SEC text fields become None ("Not reported by SEC" in the UI); nothing is invented.
    """

    cik: str
    name: str
    tickers: list[str]
    exchanges: list[str]
    sic: str | None
    sic_description: str | None
    fiscal_year_end: str | None = Field(description='"MMDD", e.g. "0926"')
    state_of_incorporation: str | None
    former_names: list[FormerName]
    source: SourceInfo


class OverviewChartRow(BaseModel):
    """One fiscal year of the overview chart and table."""

    fiscal_year_label: str
    period_end: date
    revenue: MetricValue
    net_income: MetricValue


class OverviewResponse(BaseModel):
    """GET /api/companies/{cik}/overview (endpoint added in step m1-07b)."""

    cik: str
    key_figures: list[MetricValue]
    chart: list[OverviewChartRow]
    notes: list[str]
    source: SourceInfo
