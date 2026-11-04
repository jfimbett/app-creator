"""Normalized annual statement summaries and the company overview.

These are labelled summaries built from SEC Company Facts, not reproductions of filed statements.
Pure logic over one Company Facts document (no files, network or clock). The selection policy is
in `logic/periods.py`.

- Durations (income statement, cash flow) must be annual and end on the period's end date.
- Instants (balance sheet) must be dated exactly the period's end date.
- Concepts in a priority list are alternatives: the first present per period wins, never a sum.
- A period is compared with a prior one only when that prior period ended about a year earlier.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

from app.logic import metrics
from app.logic.concepts import (
    ALL_CONCEPTS,
    NET_INCOME_CONCEPT,
    REPORTED_METRICS,
    REVENUE_CONCEPTS,
    ReportedMetric,
)
from app.logic.periods import (
    ANNUAL_MAX_DAYS,
    ANNUAL_MIN_DAYS,
    Fact,
    Period,
    annual_facts,
    instant_facts,
    parse_facts,
    reporting_currency,
    select_periods,
)
from app.models.common import MetricValue, Provenance
from app.models.companies import OverviewChartRow

NET_INCOME_MISSING_REASON = f"no {NET_INCOME_CONCEPT} fact"
RESTATEMENT_NOTE = "Values may reflect later restatements; not point-in-time."
NO_CURRENCY_NOTE = "No annual 10-K revenue in a currency unit was found."

INCOME_LINES = (
    "revenue",
    "operating_income",
    "income_tax",
    "interest_expense",
    "net_income",
    "ebit",
    "ebitda",
)
BALANCE_LINES = (
    "assets",
    "assets_current",
    "liabilities",
    "liabilities_current",
    "equity",
    "debt_long_term_noncurrent",
    "debt_long_term_current",
    "debt_short_term",
    "debt",
    "working_capital",
)
CASH_FLOW_LINES = ("operating_cash_flow", "capex", "fcf", "d_and_a")
RATIO_LINES = (
    "revenue_growth",
    "operating_margin",
    "net_margin",
    "fcf_margin",
    "debt_to_equity",
    "roe",
    "roa",
)
KEY_FIGURES = (
    "revenue",
    "revenue_growth",
    "net_income",
    "net_margin",
    "operating_cash_flow",
    "fcf",
    "debt_to_equity",
)


@dataclass(frozen=True)
class Financials:
    """Every metric for every annual period (earliest first), one value per period per metric."""

    currency: str | None
    periods: list[Period] = field(default_factory=list)
    series: dict[str, list[MetricValue]] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)

    def latest(self, years: int) -> Financials:
        """The same data limited to the latest `years` periods. Notes are rebuilt for that range."""
        kept = {metric_id: values[-years:] for metric_id, values in self.series.items()}
        notes = [RESTATEMENT_NOTE, *_concept_change_notes(kept.get("revenue", []))]
        return Financials(self.currency, self.periods[-years:], kept, notes if kept else self.notes)


@dataclass(frozen=True)
class Overview:
    """What the overview endpoint shows: latest key figures, chart rows (earliest first), notes."""

    key_figures: list[MetricValue] = field(default_factory=list)
    chart: list[OverviewChartRow] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


def _provenance(fact: Fact, source_url: str) -> Provenance:
    return Provenance(
        concept=fact.concept,
        taxonomy=fact.taxonomy,
        unit=fact.unit,
        start=fact.start,
        end=fact.end,
        form=fact.form,
        accession=fact.accn,
        filed=fact.filed,
        fy=fact.fy,
        fp=fact.fp,
        source_url=source_url,
    )


def _reported(
    metric: ReportedMetric, period: Period, fact: Fact | None, unit: str, source_url: str
) -> MetricValue:
    """A reported value with provenance, or missing with a reason (value None, never 0)."""
    return MetricValue(
        metric_id=metric.id,
        period_start=period.start,
        period_end=period.end,
        fiscal_year_label=period.label,
        value=None if fact is None else fact.val,
        unit=unit,
        kind="reported",
        status="missing" if fact is None else "ok",
        reason=metric.missing_reason if fact is None else None,
        provenance=None if fact is None else _provenance(fact, source_url),
    )


def _prior_index(periods: list[Period], index: int) -> int | None:
    """The previous period's index, only if it ended about one year earlier (no skipped years)."""
    if index == 0:
        return None
    gap = (periods[index].end - periods[index - 1].end).days
    return index - 1 if ANNUAL_MIN_DAYS <= gap <= ANNUAL_MAX_DAYS else None


def _concept_change_notes(revenue: list[MetricValue]) -> list[str]:
    """Flag the years in which the revenue concept changes; each year keeps its own concept."""
    shown = [m for m in revenue if m.provenance is not None]
    changes = [
        f"{a.fiscal_year_label}: {a.provenance.concept} → "
        f"{b.fiscal_year_label}: {b.provenance.concept}"
        for a, b in zip(shown, shown[1:], strict=False)
        if a.provenance.concept != b.provenance.concept
    ]
    return [f"Revenue concept changes between years: {'; '.join(changes)}"] if changes else []


def _derive(series: dict[str, list[MetricValue]], periods: list[Period]) -> None:
    """Add every derived metric to `series`, one value per period."""

    def add(metric_id: str, value: MetricValue) -> None:
        series.setdefault(metric_id, []).append(value)

    reported = dict(series)
    for i in range(len(periods)):
        at = {metric_id: values[i] for metric_id, values in reported.items()}
        prior = _prior_index(periods, i)
        before = None if prior is None else {k: v[prior] for k, v in reported.items()}
        free_cash_flow = metrics.fcf(at["operating_cash_flow"], at["capex"])
        earnings = metrics.ebit(at["net_income"], at["income_tax"], at["interest_expense"])
        total_debt = metrics.debt(
            [at["debt_long_term_noncurrent"], at["debt_long_term_current"], at["debt_short_term"]]
        )
        revenue = at["revenue"]
        add("fcf", free_cash_flow)
        add("ebit", earnings)
        add("ebitda", metrics.ebitda(earnings, at["d_and_a"]))
        add(
            "working_capital",
            metrics.working_capital(at["assets_current"], at["liabilities_current"]),
        )
        add("debt", total_debt)
        add(
            "revenue_growth", metrics.revenue_growth(revenue, before["revenue"] if before else None)
        )
        add(
            "operating_margin",
            metrics.margin("operating_margin", at["operating_income"], "operating income", revenue),
        )
        add("net_margin", metrics.margin("net_margin", at["net_income"], "net income", revenue))
        add("fcf_margin", metrics.margin("fcf_margin", free_cash_flow, "FCF", revenue))
        add("debt_to_equity", metrics.debt_to_equity(total_debt, at["equity"]))
        add(
            "roe",
            metrics.return_on(
                "roe", at["net_income"], at["equity"], before["equity"] if before else None
            ),
        )
        add(
            "roa",
            metrics.return_on(
                "roa", at["net_income"], at["assets"], before["assets"] if before else None
            ),
        )


def build_financials(companyfacts: Mapping, source_url: str) -> Financials:
    """All metrics for all annual periods of one Company Facts document."""
    facts = parse_facts(companyfacts, ALL_CONCEPTS)
    unit = reporting_currency(facts, REVENUE_CONCEPTS)
    if unit is None:
        return Financials(None, notes=[NO_CURRENCY_NOTE])

    selected = annual_facts(facts, unit)
    periods = select_periods(selected, (*REVENUE_CONCEPTS, NET_INCOME_CONCEPT))
    by_end = {(concept, period.end): fact for (concept, period), fact in selected.items()}
    instants = instant_facts(facts, unit)

    series: dict[str, list[MetricValue]] = {}
    for metric in REPORTED_METRICS:
        source = instants if metric.instant else by_end
        values = []
        for period in periods:
            fact = next(
                (source[(c, period.end)] for c in metric.concepts if (c, period.end) in source),
                None,
            )
            values.append(_reported(metric, period, fact, unit, source_url))
        series[metric.id] = values
    _derive(series, periods)
    notes = [RESTATEMENT_NOTE, *_concept_change_notes(series["revenue"])]
    return Financials(unit, periods, series, notes)


def _latest_reported(values: list[MetricValue]) -> MetricValue | None:
    """The latest value with status "ok"; else the latest one; None if there are no periods."""
    usable = [v for v in values if v.status == "ok"]
    if usable:
        return usable[-1]
    return values[-1] if values else None


def overview(companyfacts: Mapping, source_url: str, years: int | None = None) -> Overview:
    """Build the overview from a Company Facts document.

    `source_url` is the SEC URL of that document (recorded in every value's provenance).
    `years` keeps only the latest N annual periods in the chart (None = all available);
    key figures always use the latest usable value.
    """
    result = build_financials(companyfacts, source_url)
    if result.currency is None:
        return Overview(notes=result.notes)
    figures = [_latest_reported(result.series[metric_id]) for metric_id in KEY_FIGURES]
    chart = [
        OverviewChartRow(fiscal_year_label=p.label, period_end=p.end, revenue=r, net_income=n)
        for p, r, n in zip(
            result.periods, result.series["revenue"], result.series["net_income"], strict=True
        )
    ]
    if years is not None:
        chart = chart[-years:]
    return Overview(key_figures=[f for f in figures if f], chart=chart, notes=[RESTATEMENT_NOTE])
