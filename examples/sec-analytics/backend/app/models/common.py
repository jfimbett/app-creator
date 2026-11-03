"""Shared response shapes (milestones/architecture.md "API").

Money values are whole units of the reporting currency (e.g. USD, not millions); the UI scales.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Literal

from pydantic import BaseModel


class SourceInfo(BaseModel):
    """Where the data in a response comes from. At M1 `mode` is always "demo"."""

    mode: Literal["demo", "live", "cached"]
    label: str
    retrieved_at: datetime | None
    snapshot_date: date | None
    source_urls: list[str]


class Provenance(BaseModel):
    """The SEC fact a reported value was taken from."""

    concept: str
    taxonomy: str
    unit: str
    start: date | None
    end: date
    form: str
    accession: str
    filed: date
    fy: int | None
    fp: str | None
    source_url: str


class MetricValue(BaseModel):
    """One value for one period. `value` is None whenever `status` is not "ok" (never 0)."""

    metric_id: str
    period_start: date | None
    period_end: date
    fiscal_year_label: str
    value: float | None
    unit: str
    kind: Literal["reported", "derived"]
    status: Literal["ok", "missing", "unavailable", "not_meaningful"]
    reason: str | None = None
    formula: str | None = None
    inputs: list[MetricValue] = []
    provenance: Provenance | None = None
    note: str | None = None


class ErrorBody(BaseModel):
    """The inside of the error envelope."""

    code: str
    message: str
    details: dict[str, Any] | None = None
    reference: str | None = None


class ErrorEnvelope(BaseModel):
    """Body of every error answer: {"error": {...}}."""

    error: ErrorBody
