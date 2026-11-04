"""Edge cases of the ratios (M2-E8 to M2-E10). All inputs are SYNTHETIC, invented for tests."""

import pytest

from app.logic import metrics
from app.models.common import MetricValue


def mv(metric_id: str, value: float | None, unit: str = "USD") -> MetricValue:
    missing = value is None
    return MetricValue(
        metric_id=metric_id,
        period_start="2025-01-01",
        period_end="2025-12-31",
        fiscal_year_label="FY2025",
        value=value,
        unit=unit,
        kind="reported",
        status="missing" if missing else "ok",
        reason="no fact" if missing else None,
    )


def assert_unavailable(result: MetricValue, reason: str) -> None:
    assert (result.status, result.value, result.reason) == ("unavailable", None, reason)


@pytest.mark.parametrize("metric_id", ["operating_margin", "net_margin", "fcf_margin"])
def test_m2_e8_revenue_zero_is_unavailable(metric_id: str) -> None:
    result = metrics.margin(metric_id, mv("x", 5), "x", mv("revenue", 0))
    assert_unavailable(result, "denominator is zero")


def test_negative_revenue_is_unavailable() -> None:
    result = metrics.margin("net_margin", mv("net_income", 5), "net income", mv("revenue", -1))
    assert_unavailable(result, "revenue ≤ 0")


def test_m2_e8_equity_zero_is_unavailable() -> None:
    result = metrics.debt_to_equity(mv("debt", 300), mv("equity", 0))
    assert_unavailable(result, "denominator is zero")


def test_m2_e8_average_assets_zero_is_unavailable() -> None:
    result = metrics.return_on("roa", mv("net_income", 5), mv("assets", 100), mv("assets", -100))
    assert_unavailable(result, "denominator is zero")


def test_m2_e9_negative_equity_is_not_meaningful_and_lists_the_inputs() -> None:
    debt, equity = mv("debt", 300), mv("equity", -100)
    leverage = metrics.debt_to_equity(debt, equity)
    assert (leverage.status, leverage.value) == ("not_meaningful", None)
    assert leverage.reason == "n/m (negative equity)"
    assert [(i.metric_id, i.value) for i in leverage.inputs] == [("debt", 300), ("equity", -100)]
    roe = metrics.return_on("roe", mv("net_income", 150), equity, mv("equity", -100))
    assert (roe.status, roe.value, roe.reason) == (
        "not_meaningful",
        None,
        "n/m (negative equity)",
    )


@pytest.mark.parametrize("prior", [-20, 0])
def test_m2_e10_growth_from_a_prior_value_at_or_below_zero(prior: float) -> None:
    result = metrics.revenue_growth(mv("revenue", 30), mv("revenue", prior))
    assert (result.status, result.value) == ("not_meaningful", None)
    assert result.reason == "n/m: prior value ≤ 0"


def test_growth_with_no_prior_period() -> None:
    assert_unavailable(metrics.revenue_growth(mv("revenue", 30), None), "prior year missing")


def test_debt_with_no_component_is_unavailable_never_zero() -> None:
    result = metrics.debt(
        [
            mv("debt_long_term_noncurrent", None),
            mv("debt_long_term_current", None),
            mv("debt_short_term", None),
        ]
    )
    assert_unavailable(result, "no debt concept reported")


def test_a_reported_zero_debt_component_counts_as_reported() -> None:
    result = metrics.debt(
        [
            mv("debt_long_term_noncurrent", 0),
            mv("debt_long_term_current", None),
            mv("debt_short_term", None),
        ]
    )
    assert (result.status, result.value) == ("ok", 0)


def test_debt_to_equity_keeps_the_debt_reason() -> None:
    debt = metrics.debt([mv("a", None)])
    assert_unavailable(metrics.debt_to_equity(debt, mv("equity", 10)), "no debt concept reported")


def test_roe_without_net_income_or_ending_equity_is_unavailable() -> None:
    assert_unavailable(
        metrics.return_on("roe", mv("net_income", None), mv("equity", 5), None),
        "net income missing",
    )
    assert_unavailable(
        metrics.return_on("roe", mv("net_income", 5), mv("equity", None), mv("equity", 5)),
        "ending equity missing",
    )


def test_fcf_and_working_capital_need_both_inputs_and_keep_negatives() -> None:
    assert_unavailable(metrics.fcf(mv("ocf", 1), mv("capex", None)), "capex missing")
    assert metrics.fcf(mv("ocf", 1), mv("capex", 5)).value == -4
    capital = metrics.working_capital(mv("ca", 1), mv("cl", 5))
    assert capital.value == -4
    assert_unavailable(
        metrics.working_capital(mv("ca", None), mv("cl", 5)), "current assets missing"
    )


def test_debt_without_any_long_term_component_is_unavailable_not_zero() -> None:
    """Found on live data: a reported short-term 0 must not read as "this company has no debt"."""
    result = metrics.debt(
        [
            mv("debt_long_term_noncurrent", None),
            mv("debt_long_term_current", None),
            mv("debt_short_term", 0),
        ]
    )
    assert_unavailable(result, "no long-term debt concept reported")
    assert_unavailable(
        metrics.debt_to_equity(result, mv("equity", 100)), "no long-term debt concept reported"
    )
