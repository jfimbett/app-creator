"""Derived metrics and ratios (brief §7). Pure functions over `MetricValue` inputs.

Every result keeps its formula and inputs. When a number would be wrong or misleading it is not
computed:

- `unavailable`: an input is missing, the units differ, or a denominator is zero.
- `not_meaningful`: the arithmetic works but does not measure what the label says (negative
  equity, or growth from a prior value at or below zero). Shown as n/m with a reason, never as a
  number.

Negative equity: with equity below zero, ROE and debt-to-equity do not measure return or leverage
in the usual way, so they are not shown as numbers; the tooltip lists the raw inputs.

Values are never replaced by 0. Ratios are decimals (0.25 means 25%); the UI formats them.
"""

from __future__ import annotations

from app.models.common import MetricValue

PERCENT = "percent"
RATIO = "ratio"
PRIOR_MISSING = "prior year missing"
PRIOR_NOT_POSITIVE = "n/m: prior value ≤ 0"
ZERO_DENOMINATOR = "denominator is zero"
REVENUE_NOT_POSITIVE = "revenue ≤ 0"
UNITS_DIFFER = "units differ"
NEGATIVE_EQUITY = "n/m (negative equity)"
NO_DEBT_CONCEPT = "no debt concept reported"
ENDING_BALANCE_NOTE = "ending balance (prior year unavailable)"

FORMULAS = {
    "revenue_growth": "(revenue − prior revenue) ÷ prior revenue",
    "operating_margin": "operating income ÷ revenue",
    "net_margin": "net income ÷ revenue",
    "fcf_margin": "FCF ÷ revenue",
    "fcf": "operating cash flow − capex",
    "ebit": "net income + income tax expense + interest expense",
    "ebitda": "EBIT + D&A",
    "working_capital": "current assets − current liabilities",
    "debt": "long-term debt (noncurrent) + long-term debt (current) + short-term debt, as reported",
    "debt_to_equity": "debt ÷ equity",
    "roe": "net income ÷ average(beginning, ending) equity",
    "roa": "net income ÷ average(beginning, ending) total assets",
}


def _ok(metric: MetricValue | None) -> bool:
    """True when the metric has a usable number."""
    return metric is not None and metric.status == "ok" and metric.value is not None


def _result(
    metric_id: str,
    base: MetricValue,
    unit: str,
    inputs: list[MetricValue],
    value: float | None = None,
    status: str = "ok",
    reason: str | None = None,
    note: str | None = None,
) -> MetricValue:
    """A derived MetricValue for `base`'s period, carrying its formula and inputs."""
    return MetricValue(
        metric_id=metric_id,
        period_start=base.period_start,
        period_end=base.period_end,
        fiscal_year_label=base.fiscal_year_label,
        value=value if status == "ok" else None,
        unit=unit,
        kind="derived",
        status=status,
        reason=reason,
        formula=FORMULAS[metric_id],
        inputs=inputs,
        note=note,
    )


def _unavailable(
    metric_id: str, base: MetricValue, unit: str, inputs: list[MetricValue], reason: str
) -> MetricValue:
    return _result(metric_id, base, unit, inputs, status="unavailable", reason=reason)


def _first_gap(inputs: list[tuple[str, MetricValue | None]]) -> str | None:
    """A reason naming the first missing input, or None when all inputs have numbers."""
    for name, metric in inputs:
        if not _ok(metric):
            return f"{name} missing"
    return None


def revenue_growth(current: MetricValue, prior: MetricValue | None) -> MetricValue:
    """(current − prior) ÷ prior. `prior` must be the immediately preceding annual period."""
    inputs = [m for m in (current, prior) if m is not None]
    if not _ok(current):
        return _unavailable("revenue_growth", current, PERCENT, inputs, "revenue missing")
    if not _ok(prior):
        return _unavailable("revenue_growth", current, PERCENT, inputs, PRIOR_MISSING)
    if current.unit != prior.unit:
        return _unavailable("revenue_growth", current, PERCENT, inputs, UNITS_DIFFER)
    if prior.value <= 0:
        return _result(
            "revenue_growth",
            current,
            PERCENT,
            inputs,
            status="not_meaningful",
            reason=PRIOR_NOT_POSITIVE,
        )
    value = (current.value - prior.value) / prior.value
    return _result("revenue_growth", current, PERCENT, inputs, value)


def margin(metric_id: str, numerator: MetricValue, name: str, revenue: MetricValue) -> MetricValue:
    """Numerator ÷ revenue for operating, net and FCF margin."""
    inputs = [numerator, revenue]
    gap = _first_gap([(name, numerator), ("revenue", revenue)])
    if gap:
        return _unavailable(metric_id, numerator, PERCENT, inputs, gap)
    if numerator.unit != revenue.unit:
        return _unavailable(metric_id, numerator, PERCENT, inputs, UNITS_DIFFER)
    if revenue.value == 0:
        return _unavailable(metric_id, numerator, PERCENT, inputs, ZERO_DENOMINATOR)
    if revenue.value < 0:
        return _unavailable(metric_id, numerator, PERCENT, inputs, REVENUE_NOT_POSITIVE)
    return _result(metric_id, numerator, PERCENT, inputs, numerator.value / revenue.value)


def fcf(operating_cash_flow: MetricValue, capex: MetricValue) -> MetricValue:
    """Free cash flow = operating cash flow − capex (capex is reported as a positive payment)."""
    inputs = [operating_cash_flow, capex]
    gap = _first_gap([("operating cash flow", operating_cash_flow), ("capex", capex)])
    if gap:
        return _unavailable("fcf", operating_cash_flow, operating_cash_flow.unit, inputs, gap)
    if operating_cash_flow.unit != capex.unit:
        return _unavailable(
            "fcf", operating_cash_flow, operating_cash_flow.unit, inputs, UNITS_DIFFER
        )
    value = operating_cash_flow.value - capex.value
    return _result("fcf", operating_cash_flow, operating_cash_flow.unit, inputs, value)


def ebit(net_income: MetricValue, income_tax: MetricValue, interest: MetricValue) -> MetricValue:
    """EBIT = net income + income tax + interest. Never replaced by operating income."""
    inputs = [net_income, income_tax, interest]
    gap = _first_gap(
        [("net income", net_income), ("income tax", income_tax), ("interest expense", interest)]
    )
    if gap:
        return _unavailable("ebit", net_income, net_income.unit, inputs, gap)
    if len({m.unit for m in inputs}) > 1:
        return _unavailable("ebit", net_income, net_income.unit, inputs, UNITS_DIFFER)
    value = net_income.value + income_tax.value + interest.value
    return _result("ebit", net_income, net_income.unit, inputs, value)


def ebitda(ebit_value: MetricValue, d_and_a: MetricValue) -> MetricValue:
    """EBITDA = EBIT + depreciation and amortization."""
    inputs = [ebit_value, d_and_a]
    gap = _first_gap([("EBIT", ebit_value), ("D&A", d_and_a)])
    if gap:
        return _unavailable("ebitda", ebit_value, ebit_value.unit, inputs, gap)
    if ebit_value.unit != d_and_a.unit:
        return _unavailable("ebitda", ebit_value, ebit_value.unit, inputs, UNITS_DIFFER)
    return _result("ebitda", ebit_value, ebit_value.unit, inputs, ebit_value.value + d_and_a.value)


def working_capital(current_assets: MetricValue, current_liabilities: MetricValue) -> MetricValue:
    """Current assets − current liabilities at fiscal year-end; negative results are kept."""
    inputs = [current_assets, current_liabilities]
    unit = current_assets.unit
    gap = _first_gap(
        [("current assets", current_assets), ("current liabilities", current_liabilities)]
    )
    if gap:
        return _unavailable("working_capital", current_assets, unit, inputs, gap)
    if unit != current_liabilities.unit:
        return _unavailable("working_capital", current_assets, unit, inputs, UNITS_DIFFER)
    value = current_assets.value - current_liabilities.value
    return _result("working_capital", current_assets, unit, inputs, value)


def debt(components: list[MetricValue]) -> MetricValue:
    """Sum of the debt components reported at that date; none means unavailable, never 0."""
    base = components[0]
    reported = [c for c in components if _ok(c)]
    if not reported:
        return _unavailable("debt", base, base.unit, components, NO_DEBT_CONCEPT)
    if len({c.unit for c in reported}) > 1:
        return _unavailable("debt", base, base.unit, components, UNITS_DIFFER)
    absent = [c.metric_id for c in components if not _ok(c)]
    note = f"Not reported at this date: {', '.join(absent)}" if absent else None
    total = sum(c.value for c in reported)
    return _result("debt", base, reported[0].unit, components, total, note=note)


def debt_to_equity(debt_value: MetricValue, equity: MetricValue) -> MetricValue:
    """Debt ÷ equity. Zero equity is unavailable; negative equity is n/m with the inputs listed."""
    inputs = [debt_value, equity]
    if not _ok(debt_value):
        reason = debt_value.reason or "debt missing"
        return _unavailable("debt_to_equity", equity, RATIO, inputs, reason)
    if not _ok(equity):
        return _unavailable("debt_to_equity", equity, RATIO, inputs, "equity missing")
    if debt_value.unit != equity.unit:
        return _unavailable("debt_to_equity", equity, RATIO, inputs, UNITS_DIFFER)
    if equity.value == 0:
        return _unavailable("debt_to_equity", equity, RATIO, inputs, ZERO_DENOMINATOR)
    if equity.value < 0:
        return _result(
            "debt_to_equity", equity, RATIO, inputs, status="not_meaningful", reason=NEGATIVE_EQUITY
        )
    return _result("debt_to_equity", equity, RATIO, inputs, debt_value.value / equity.value)


def return_on(
    metric_id: str,
    net_income: MetricValue,
    ending: MetricValue,
    beginning: MetricValue | None,
) -> MetricValue:
    """ROE or ROA: net income ÷ average(beginning, ending) balance.

    With no beginning balance, the ending balance is used and labelled. An average below zero is
    n/m.
    """
    name = "equity" if metric_id == "roe" else "total assets"
    inputs = [m for m in (net_income, ending, beginning) if m is not None]
    gap = _first_gap([("net income", net_income), (f"ending {name}", ending)])
    if gap:
        return _unavailable(metric_id, net_income, PERCENT, inputs, gap)
    if net_income.unit != ending.unit:
        return _unavailable(metric_id, net_income, PERCENT, inputs, UNITS_DIFFER)
    if _ok(beginning):
        if beginning.unit != ending.unit:
            return _unavailable(metric_id, net_income, PERCENT, inputs, UNITS_DIFFER)
        denominator, note = (beginning.value + ending.value) / 2, None
    else:
        denominator, note = ending.value, ENDING_BALANCE_NOTE
    if denominator == 0:
        return _unavailable(metric_id, net_income, PERCENT, inputs, ZERO_DENOMINATOR)
    if denominator < 0:
        reason = NEGATIVE_EQUITY if metric_id == "roe" else "n/m: average assets below zero"
        return _result(
            metric_id, net_income, PERCENT, inputs, status="not_meaningful", reason=reason
        )
    return _result(
        metric_id, net_income, PERCENT, inputs, net_income.value / denominator, note=note
    )
