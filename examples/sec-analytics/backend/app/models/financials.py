"""Response shapes of /api/metrics and /api/companies/{cik}/financials|metrics (brief §5)."""

from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel

from app.models.common import MetricValue, SourceInfo


class MetricInfo(BaseModel):
    """One metric the explorer can show."""

    id: str
    label: str
    unit_kind: Literal["currency", "ratio", "percent"]
    kind: Literal["reported", "derived"]
    formula: str | None
    concepts: list[str]


class MetricsCatalog(BaseModel):
    """GET /api/metrics."""

    metrics: list[MetricInfo]


class PeriodInfo(BaseModel):
    """An annual period, identified by its dates. Its label is always shown with the end date."""

    fiscal_year_label: str
    start: date
    end: date


class Line(BaseModel):
    """One row of a statement summary: one value per period, in the order of `periods`."""

    metric_id: str
    label: str
    kind: Literal["reported", "derived"]
    unit: str
    values: list[MetricValue]


class Statements(BaseModel):
    """The three normalized statement summaries."""

    income: list[Line]
    balance: list[Line]
    cash_flow: list[Line]


class FinancialsResponse(BaseModel):
    """GET /api/companies/{cik}/financials."""

    cik: str
    currency: str | None
    fiscal_year_end: str | None
    periods: list[PeriodInfo]
    statements: Statements
    ratios: list[Line]
    notes: list[str]
    source: SourceInfo


class MetricSeries(BaseModel):
    """One metric over the requested periods, earliest first."""

    metric_id: str
    label: str
    unit: str
    kind: Literal["reported", "derived"]
    formula: str | None
    points: list[MetricValue]


class MetricSeriesResponse(BaseModel):
    """GET /api/companies/{cik}/metrics."""

    cik: str
    series: list[MetricSeries]
    source: SourceInfo
