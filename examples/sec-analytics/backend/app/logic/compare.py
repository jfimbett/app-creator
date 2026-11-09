"""Comparing 2–4 companies (M4). Pure functions: no network, files or clock.

Rules (milestones/architecture.md "Comparison", examples/sec-analytics/CLAUDE.md):

- Each company keeps its own fiscal years, labelled `FY<year of end date>`, and every row
  carries its own period end. Nothing is aligned to calendar years; differing year-ends give a
  warning.
- Each company keeps its own reporting currency. Nothing is converted; differing currencies give
  a warning.
- Indexing (`Index = 100 at first common fiscal year`) applies only to absolute currency
  metrics. The base is the earliest fiscal year label, within each company's window, at which
  every company has a value for every selected absolute metric. Each company is divided by its
  own base value. A base at or below zero would give a misleading index, so that company's
  indexed values are unavailable, with the reason.
- Rows come in a fixed order: companies as given, then metrics as given, then fiscal year
  ascending. The table and the CSV both use it.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from app.models.common import MetricValue
from app.models.compare import (
    CompareCompany,
    CompareRow,
    CompareWarning,
    IndexBase,
)

COMPARE_METRICS = (
    "revenue",
    "revenue_growth",
    "operating_margin",
    "net_margin",
    "operating_cash_flow",
    "fcf",
    "fcf_margin",
    "debt_to_equity",
)
# Absolute amounts in the reporting currency: the only metrics that are indexed.
MONEY_METRICS = frozenset({"revenue", "operating_cash_flow", "fcf"})
DEFAULT_METRICS = ("revenue", "net_margin")
MIN_COMPANIES, MAX_COMPANIES = 2, 4
MIN_METRICS, MAX_METRICS = 1, 6

INDEX_UNIT = "index"
RATIO_UNIT = "ratio"
NOT_ALIGNED = "Fiscal years are not aligned"
NO_COMMON_YEAR = "No common fiscal year to index from"


@dataclass(frozen=True)
class CompanyInput:
    """One company's annual series (earliest first) as built by `logic/statements.py`."""

    cik: str
    ticker: str
    name: str
    currency: str | None
    series: Mapping[str, list[MetricValue]]
    data_source: str


@dataclass(frozen=True)
class CompareResult:
    companies: list[CompareCompany]
    metrics: list[str]
    rows: list[CompareRow]
    index_base: IndexBase | None
    warnings: list[CompareWarning]


def _window(company: CompanyInput, metric_id: str, years: int) -> list[MetricValue]:
    return list(company.series.get(metric_id, []))[-years:]


def _fiscal_year_end(company: CompanyInput, years: int) -> str | None:
    """MM-DD of the latest period end in the window, or None when the company has no periods."""
    ends = [v.period_end for values in company.series.values() for v in values[-years:]]
    return max(ends).strftime("%m-%d") if ends else None


def _has_value(value: MetricValue) -> bool:
    return value.status == "ok" and value.value is not None


def _plain_number(number: float) -> str:
    return str(int(number)) if float(number).is_integer() else repr(float(number))


def _row(company: CompanyInput, value: MetricValue) -> CompareRow:
    money = value.metric_id in MONEY_METRICS
    provenance = value.provenance
    return CompareRow(
        cik=company.cik,
        metric_id=value.metric_id,
        fiscal_year_label=value.fiscal_year_label,
        period_start=value.period_start,
        period_end=value.period_end,
        value=value.value if _has_value(value) else None,
        unit=(value.unit or company.currency or "") if money else RATIO_UNIT,
        kind=value.kind,
        status=value.status,
        reason=value.reason,
        indexed=False,
        source_concept=provenance.concept if provenance else None,
        accession=provenance.accession if provenance else None,
        data_source=company.data_source,
    )


def _common_base_label(
    companies: list[CompanyInput], metrics: list[str], years: int
) -> str | None:
    """The earliest label at which every company has a value for every selected money metric."""
    shared: set[str] | None = None
    for company in companies:
        labels: set[str] | None = None
        for metric_id in metrics:
            present = {v.fiscal_year_label for v in _window(company, metric_id, years)
                       if _has_value(v)}
            labels = present if labels is None else labels & present
        labels = labels or set()
        shared = labels if shared is None else shared & labels
    return min(shared) if shared else None


def _indexed(row: CompareRow, base: CompareRow) -> CompareRow:
    """The row as index points against its company's own base row."""
    if base.value is None or base.value <= 0:
        shown = _plain_number(base.value) if base.value is not None else "missing"
        return row.model_copy(update={
            "value": None, "unit": INDEX_UNIT, "kind": "derived", "indexed": True,
            "status": "unavailable",
            "reason": f"index base {base.fiscal_year_label} is ≤ 0 ({shown} {base.unit})",
        })
    value = row.value / base.value * 100 if row.value is not None else None
    return row.model_copy(update={
        "value": value, "unit": INDEX_UNIT, "kind": "derived", "indexed": True,
    })


def _alignment_and_currency_warnings(
    companies: list[CompareCompany], metrics: list[str]
) -> list[CompareWarning]:
    warnings: list[CompareWarning] = []
    year_ends = {c.fiscal_year_end for c in companies if c.fiscal_year_end}
    if len(year_ends) > 1:
        warnings.append(CompareWarning(code="fiscal_years_not_aligned", message=NOT_ALIGNED))
    currencies = list(dict.fromkeys(c.currency for c in companies if c.currency))
    if len(currencies) > 1 and any(m in MONEY_METRICS for m in metrics):
        warnings.append(CompareWarning(
            code="currencies_differ",
            message=f"Different reporting currencies ({', '.join(currencies)}): not converted",
        ))
    return warnings


def compare(
    companies: list[CompanyInput], metrics: list[str], years: int, index: bool
) -> CompareResult:
    """The comparison table: rows in fixed order, warnings, and the index base when indexing."""
    info = [
        CompareCompany(
            cik=c.cik, ticker=c.ticker, name=c.name,
            fiscal_year_end=_fiscal_year_end(c, years), currency=c.currency,
        )
        for c in companies
    ]
    warnings = _alignment_and_currency_warnings(info, metrics)

    money = [m for m in metrics if m in MONEY_METRICS]
    base_label = _common_base_label(companies, money, years) if index and money else None
    if index and money and base_label is None:
        warnings.append(CompareWarning(code="no_common_fiscal_year", message=NO_COMMON_YEAR))

    rows: list[CompareRow] = []
    base_ends = {}
    unavailable: list[str] = []
    for company in companies:
        for metric_id in metrics:
            metric_rows = [_row(company, v) for v in _window(company, metric_id, years)]
            if base_label is not None and metric_id in MONEY_METRICS:
                base = next(r for r in metric_rows if r.fiscal_year_label == base_label)
                base_ends[company.cik] = base.period_end
                metric_rows = [_indexed(r, base) for r in metric_rows]
                if base.value is None or base.value <= 0:
                    unavailable.append(f"{company.ticker or company.cik} {metric_id}")
            rows.extend(metric_rows)

    if unavailable:
        warnings.append(CompareWarning(
            code="index_base_unavailable",
            message="Index not available where the base value is ≤ 0: " + ", ".join(unavailable),
        ))
    index_base = (
        IndexBase(
            fiscal_year_by_cik={c.cik: base_label for c in companies},
            period_end_by_cik=base_ends,
        )
        if base_label is not None
        else None
    )
    return CompareResult(info, list(metrics), rows, index_base, warnings)
