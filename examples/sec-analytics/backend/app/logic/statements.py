"""Company overview: key figures and the revenue / net income chart rows (M1).

Pure logic over one SEC Company Facts document (no files, network or clock). Period selection,
duplicates, the revenue priority list and the reporting currency come from `logic/periods.py`.
Every value is `reported` (one SEC fact, with provenance) or `missing` (value None plus a
reason), never 0.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

from app.logic.concepts import NET_INCOME_CONCEPT, REVENUE_CONCEPTS
from app.logic.periods import (
    REVENUE_MISSING_REASON,
    AnnualValue,
    Period,
    annual_facts,
    annual_periods,
    parse_facts,
    pick_first,
    reporting_currency,
)
from app.models.common import MetricValue, Provenance
from app.models.companies import OverviewChartRow

NET_INCOME_MISSING_REASON = f"no {NET_INCOME_CONCEPT} fact"
RESTATEMENT_NOTE = "Values may reflect later restatements; not point-in-time."
NO_CURRENCY_NOTE = "No annual 10-K revenue in a currency unit was found in the snapshot."


@dataclass(frozen=True)
class Overview:
    """What the overview endpoint shows: latest key figures, chart rows (earliest first), notes."""

    key_figures: list[MetricValue] = field(default_factory=list)
    chart: list[OverviewChartRow] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


def _metric(metric_id: str, annual: AnnualValue, unit: str, source_url: str) -> MetricValue:
    """Turn a selected annual value into a reported MetricValue with provenance."""
    fact = annual.fact
    provenance = None
    if fact is not None:
        provenance = Provenance(
            concept=fact.concept, taxonomy=fact.taxonomy, unit=fact.unit, start=fact.start,
            end=fact.end, form=fact.form, accession=fact.accn, filed=fact.filed, fy=fact.fy,
            fp=fact.fp, source_url=source_url,
        )
    return MetricValue(
        metric_id=metric_id,
        period_start=annual.period.start,
        period_end=annual.period.end,
        fiscal_year_label=annual.period.label,
        value=annual.value,
        unit=unit,
        kind="reported",
        status=annual.status,
        reason=annual.reason,
        provenance=provenance,
    )


def _latest_reported(values: list[MetricValue]) -> MetricValue | None:
    """The latest value with status "ok"; else the latest (missing) one; None if empty."""
    reported = [v for v in values if v.status == "ok"]
    if reported:
        return reported[-1]
    return values[-1] if values else None


def overview(
    companyfacts: Mapping, source_url: str, years: int | None = None
) -> Overview:
    """Build the overview from a Company Facts document.

    `source_url` is the SEC URL of that document (recorded in every value's provenance).
    `years` keeps only the latest N annual periods in the chart (None = all in the snapshot);
    key figures always use the latest reported value in the snapshot.
    """
    facts = parse_facts(companyfacts, (*REVENUE_CONCEPTS, NET_INCOME_CONCEPT))
    unit = reporting_currency(facts, REVENUE_CONCEPTS)
    if unit is None:
        return Overview(notes=[NO_CURRENCY_NOTE])

    selected = annual_facts(facts, unit)
    periods: list[Period] = annual_periods(selected)
    revenue = [
        _metric("revenue", pick_first(selected, REVENUE_CONCEPTS, p, REVENUE_MISSING_REASON),
                unit, source_url)
        for p in periods
    ]
    net_income = [
        _metric("net_income",
                pick_first(selected, (NET_INCOME_CONCEPT,), p, NET_INCOME_MISSING_REASON),
                unit, source_url)
        for p in periods
    ]
    chart = [
        OverviewChartRow(fiscal_year_label=p.label, period_end=p.end, revenue=r, net_income=n)
        for p, r, n in zip(periods, revenue, net_income, strict=True)
    ]
    key_figures = [m for m in (_latest_reported(revenue), _latest_reported(net_income)) if m]
    if years is not None:
        chart = chart[-years:]
    return Overview(key_figures=key_figures, chart=chart, notes=[RESTATEMENT_NOTE])
