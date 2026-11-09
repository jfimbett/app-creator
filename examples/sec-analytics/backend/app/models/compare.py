"""Response shapes of the comparison (M4, milestones/architecture.md "API").

`value` is in whole currency units, index points or a decimal ratio; `unit` says which (a
currency code such as `USD`, `index`, or `ratio`). A value that is not `ok` is null with its
reason, never 0.
"""

from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel

from app.models.common import SourceInfo


class CompareCompany(BaseModel):
    """One compared company. `fiscal_year_end` is MM-DD of its latest period end in the window."""

    cik: str
    ticker: str
    name: str
    fiscal_year_end: str | None
    currency: str | None


class CompareRow(BaseModel):
    """One data point: one company, one metric, one fiscal year label."""

    cik: str
    metric_id: str
    fiscal_year_label: str
    period_start: date | None
    period_end: date
    value: float | None
    unit: str
    kind: Literal["reported", "derived"]
    status: Literal["ok", "missing", "unavailable", "not_meaningful"]
    reason: str | None = None
    indexed: bool
    source_concept: str | None = None
    accession: str | None = None
    data_source: str


class IndexBase(BaseModel):
    """The common base year of an indexed comparison and each company's own base period end."""

    fiscal_year_by_cik: dict[str, str]
    period_end_by_cik: dict[str, date]


class CompareWarning(BaseModel):
    code: Literal[
        "fiscal_years_not_aligned", "currencies_differ", "no_common_fiscal_year",
        "index_base_unavailable",
    ]
    message: str


class CompareResponse(BaseModel):
    companies: list[CompareCompany]
    metrics: list[str]
    rows: list[CompareRow]
    index_base: IndexBase | None
    warnings: list[CompareWarning]
    source: SourceInfo
