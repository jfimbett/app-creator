"""Period, duplicate, concept and unit rules on full statements (M2-E1 to M2-E7, M2-E11).

All facts here are SYNTHETIC: invented for tests, not SEC data.
"""

import pytest

from app.logic import metrics
from app.logic.statements import build_financials, overview
from app.models.common import MetricValue

URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK0000000002.json"
REV = "Revenues"
EXCL = "RevenueFromContractWithCustomerExcludingAssessedTax"
NI = "NetIncomeLoss"


def fact(start, end, val, *, form="10-K", filed="2026-02-01", accn="0000000002-26-000001", fy=2025):
    row = {"end": end, "val": val, "form": form, "filed": filed, "accn": accn, "fy": fy, "fp": "FY"}
    if start:
        row["start"] = start
    return row


def doc(**concepts) -> dict:
    """Company Facts shape from `Concept=[rows]` (USD) or `Concept={"unit": [rows]}`."""
    tagged = {}
    for concept, rows in concepts.items():
        units = rows if isinstance(rows, dict) else {"USD": rows}
        tagged[concept] = {"units": units}
    return {"facts": {"us-gaap": tagged}}


FY23, FY24, FY25 = (
    ("2023-01-01", "2023-12-31"),
    ("2024-01-01", "2024-12-31"),
    ("2025-01-01", "2025-12-31"),
)


def _by_year(financials, metric_id):
    return {v.fiscal_year_label: v for v in financials.series[metric_id]}


def test_m2_e1_missing_revenue_tag_stays_missing_and_blocks_ratios() -> None:
    result = build_financials(
        doc(
            Revenues=[fact(*FY23, 100), fact(*FY25, 300)],
            NetIncomeLoss=[fact(*FY23, 10), fact(*FY24, 20), fact(*FY25, 30)],
        ),
        URL,
    )
    revenue = _by_year(result, "revenue")["FY2024"]
    assert (revenue.status, revenue.value) == ("missing", None)
    assert revenue.reason == "no mapped revenue concept"
    margin = _by_year(result, "net_margin")["FY2024"]
    assert (margin.status, margin.value) == ("unavailable", None)
    assert margin.reason == "revenue missing"
    assert _by_year(result, "revenue_growth")["FY2024"].status == "unavailable"
    after_gap = _by_year(result, "revenue_growth")["FY2025"]
    assert (after_gap.status, after_gap.reason) == ("unavailable", "prior year missing")


def test_m2_e2_each_year_uses_its_own_concept_never_a_sum_and_is_flagged() -> None:
    result = build_financials(
        doc(
            RevenueFromContractWithCustomerExcludingAssessedTax=[fact(*FY23, 100)],
            Revenues=[fact(*FY24, 200)],
            NetIncomeLoss=[fact(*FY23, 1), fact(*FY24, 2)],
        ),
        URL,
    )
    revenue = _by_year(result, "revenue")
    assert (revenue["FY2023"].value, revenue["FY2023"].provenance.concept) == (100, EXCL)
    assert (revenue["FY2024"].value, revenue["FY2024"].provenance.concept) == (200, REV)
    assert result.notes[1] == (
        f"Revenue concept changes between years: FY2023: {EXCL} → FY2024: {REV}"
    )


def test_a_period_with_both_concepts_uses_the_priority_and_never_sums() -> None:
    result = build_financials(
        doc(
            Revenues=[fact(*FY25, 500)],
            RevenueFromContractWithCustomerExcludingAssessedTax=[fact(*FY25, 480)],
        ),
        URL,
    )
    value = result.series["revenue"][-1]
    assert (value.value, value.provenance.concept) == (500, REV)


def test_m2_e3_later_amendment_wins_and_is_not_summed() -> None:
    result = build_financials(
        doc(
            Revenues=[
                fact(*FY24, 1000, filed="2024-11-01", accn="0000000002-24-000001"),
                fact(*FY24, 1010, form="10-K/A", filed="2025-02-01", accn="0000000002-25-000001"),
            ]
        ),
        URL,
    )
    value = result.series["revenue"][0]
    assert value.value == 1010
    assert (value.provenance.form, value.provenance.accession) == ("10-K/A", "0000000002-25-000001")
    assert "Values may reflect later restatements; not point-in-time." in result.notes


@pytest.mark.parametrize("swap", [False, True])
def test_m2_e4_same_date_tie_keeps_the_higher_accession_on_every_run(swap: bool) -> None:
    rows = [
        fact(*FY24, 7, accn="0000000002-24-000101", filed="2024-11-01"),
        fact(*FY24, 9, accn="0000000002-24-000099", filed="2024-11-01"),
    ]
    result = build_financials(doc(Revenues=rows[::-1] if swap else rows), URL)
    assert result.series["revenue"][0].value == 7


def test_m2_e5_comparative_is_placed_by_dates_not_fy() -> None:
    result = build_financials(
        doc(Revenues=[fact(*FY23, 111, fy=2025), fact(*FY25, 333, fy=2025)]), URL
    )
    revenue = _by_year(result, "revenue")
    assert (revenue["FY2023"].value, revenue["FY2025"].value) == (111, 333)
    assert revenue["FY2023"].provenance.fy == 2025


@pytest.mark.parametrize(
    ("end", "kept"),
    [
        ("2024-12-30", True),  # 364 days
        ("2025-01-06", True),  # 371 days
        ("2024-12-16", True),  # 350 days
        ("2025-01-15", True),  # 380 days
        ("2024-12-15", False),  # 349 days
        ("2025-01-16", False),  # 381 days
        ("2024-04-01", False),  # 91 days, a quarter
        ("2024-09-30", False),  # 273 days, year to date
    ],
)
def test_m2_e6_annual_durations(end: str, kept: bool) -> None:
    result = build_financials(doc(Revenues=[fact("2024-01-01", end, 5)]), URL)
    assert bool(result.periods) is kept


def test_a_10q_of_annual_length_is_ignored() -> None:
    result = build_financials(doc(Revenues=[fact(*FY24, 5, form="10-Q")]), URL)
    assert result.periods == []


def test_m2_e7_only_the_reporting_currency_is_used() -> None:
    result = build_financials(
        doc(
            Revenues={"USD": [fact(*FY23, 10), fact(*FY24, 20)], "EUR": [fact(*FY24, 999)]},
            NetIncomeLoss={"EUR": [fact(*FY24, 888)]},
        ),
        URL,
    )
    assert result.currency == "USD"
    assert _by_year(result, "revenue")["FY2024"].value == 20
    net = _by_year(result, "net_income")["FY2024"]
    assert (net.status, net.value) == ("missing", None)


def _mv(metric_id: str, value: float, unit: str) -> MetricValue:
    return MetricValue(
        metric_id=metric_id, period_start=None, period_end="2025-12-31",
        fiscal_year_label="FY2025", value=value, unit=unit, kind="reported", status="ok",
    )  # fmt: skip


def test_m2_e7_a_ratio_of_incompatible_units_is_unavailable() -> None:
    result = metrics.margin("net_margin", _mv("net_income", 5, "USD"), "net income",
                            _mv("revenue", 10, "shares"))  # fmt: skip
    assert (result.status, result.value, result.reason) == ("unavailable", None, "units differ")


def test_m2_e11_instant_two_days_after_year_end_is_not_used() -> None:
    result = build_financials(
        doc(
            Revenues=[fact(*FY25, 100)],
            Assets=[fact(None, "2026-01-02", 500)],
            StockholdersEquity=[fact(None, "2025-12-31", 200)],
        ),
        URL,
    )
    assets = result.series["assets"][0]
    assert (assets.status, assets.value) == ("missing", None)
    assert result.series["equity"][0].value == 200


def test_a_duration_fact_is_never_used_as_an_instant() -> None:
    result = build_financials(doc(Revenues=[fact(*FY25, 100)], Assets=[fact(*FY25, 500)]), URL)
    assert result.series["assets"][0].status == "missing"


def test_growth_is_not_computed_across_a_skipped_year() -> None:
    result = build_financials(doc(Revenues=[fact(*FY23, 100), fact(*FY25, 300)]), URL)
    growth = _by_year(result, "revenue_growth")["FY2025"]
    assert (growth.status, growth.reason) == ("unavailable", "prior year missing")


def test_two_periods_sharing_an_end_keep_the_latest_filed() -> None:
    result = build_financials(
        doc(
            Revenues=[
                fact("2024-01-01", "2024-12-31", 10, filed="2025-01-01"),
                fact("2024-01-03", "2024-12-31", 11, filed="2026-01-01"),
            ]
        ),
        URL,
    )
    assert len(result.periods) == 1
    assert result.periods[0].start.isoformat() == "2024-01-03"


def test_no_revenue_at_all_gives_no_periods_and_a_note() -> None:
    result = build_financials(doc(NetIncomeLoss=[fact(*FY25, 1)]), URL)
    assert (result.currency, result.periods) == (None, [])
    assert result.notes == ["No annual 10-K revenue in a currency unit was found."]


def test_capex_uses_the_alternate_concept_when_the_first_is_absent() -> None:
    """Found on live data: NVIDIA tags capex as PaymentsToAcquireProductiveAssets."""
    result = build_financials(
        doc(
            Revenues=[fact(*FY25, 100)],
            NetCashProvidedByUsedInOperatingActivities=[fact(*FY25, 40)],
            PaymentsToAcquireProductiveAssets=[fact(*FY25, 15)],
        ),
        URL,
    )
    capex = result.series["capex"][0]
    assert (capex.value, capex.provenance.concept) == (15, "PaymentsToAcquireProductiveAssets")
    assert result.series["fcf"][0].value == 25


def test_ppe_capex_wins_when_both_concepts_exist_and_they_are_never_summed() -> None:
    result = build_financials(
        doc(
            Revenues=[fact(*FY25, 100)],
            PaymentsToAcquirePropertyPlantAndEquipment=[fact(*FY25, 10)],
            PaymentsToAcquireProductiveAssets=[fact(*FY25, 15)],
        ),
        URL,
    )
    assert result.series["capex"][0].value == 10


def test_a_calculated_key_figure_is_never_taken_from_an_old_year() -> None:
    """Found on live data: FCF from FY2012 was shown beside FY2026 figures."""
    result = overview(
        doc(
            Revenues=[fact(*FY24, 100), fact(*FY25, 110)],
            NetIncomeLoss=[fact(*FY24, 10), fact(*FY25, 11)],
            NetCashProvidedByUsedInOperatingActivities=[fact(*FY24, 40)],
            PaymentsToAcquirePropertyPlantAndEquipment=[fact(*FY24, 15)],
        ),
        URL,
    )
    figures = {f.metric_id: f for f in result.key_figures}
    assert figures["fcf"].fiscal_year_label == "FY2025"
    assert (figures["fcf"].status, figures["fcf"].value) == ("unavailable", None)
    assert figures["operating_cash_flow"].fiscal_year_label == "FY2025"
    assert figures["operating_cash_flow"].status == "missing"
    assert figures["net_margin"].fiscal_year_label == "FY2025"
