"""Comparison logic (M4): row order, fiscal year-ends, currencies, indexing (CALC11, FX16). Offline.

Synthetic companies come from tests/synthetic/compare/companies.json. Expected values are worked by
hand in milestones/acceptance.md (CALC11, FX16), never taken from the code's output.
"""

import json
from datetime import date
from pathlib import Path

import pytest

from app.data.fixtures import FixtureStore
from app.logic import compare as cmp
from app.logic.statements import build_financials
from app.models.common import MetricValue, Provenance
from app.settings import Settings

SYNTHETIC = json.loads(
    (Path(__file__).parent / "synthetic" / "compare" / "companies.json").read_text("utf-8")
)
BY_TICKER = {c["ticker"]: c for c in SYNTHETIC["companies"]}
LABEL = "SYNTHETIC TEST DATA"
MONEY = {"revenue", "fcf"}


def _value(company: dict, period: dict, metric_id: str) -> MetricValue:
    raw = period.get(metric_id)
    end = date.fromisoformat(period["end"])
    reported = metric_id == "revenue"
    provenance = None
    if reported and raw is not None:
        provenance = Provenance(
            concept="Revenues", taxonomy="us-gaap", unit=company["currency"],
            start=date.fromisoformat(period["start"]), end=end, form="10-K",
            accession=f"{company['cik']}-{end.year % 100:02d}-000001", filed=end,
            fy=end.year, fp="FY", source_url="https://data.sec.gov/invalid",
        )
    return MetricValue(
        metric_id=metric_id,
        period_start=date.fromisoformat(period["start"]),
        period_end=end,
        fiscal_year_label=f"FY{end.year}",
        value=raw,
        unit=company["currency"] if metric_id in MONEY else "percent",
        kind="reported" if reported else "derived",
        status="ok" if raw is not None else "missing",
        reason=None if raw is not None else "no fact for this period",
        provenance=provenance,
    )


def company(ticker: str) -> cmp.CompanyInput:
    raw = BY_TICKER[ticker]
    series = {
        metric_id: [_value(raw, p, metric_id) for p in raw["periods"]]
        for metric_id in ("revenue", "net_margin", "fcf")
    }
    return cmp.CompanyInput(
        cik=raw["cik"], ticker=raw["ticker"], name=raw["name"], currency=raw["currency"],
        series=series, data_source=LABEL,
    )


def rows_for(result, ticker, metric_id):
    cik = BY_TICKER[ticker]["cik"]
    return [r for r in result.rows if r.cik == cik and r.metric_id == metric_id]


# ------------------------------------------------------------------ order and shape


def test_rows_are_companies_then_metrics_then_years_ascending() -> None:
    result = cmp.compare(
        [company("SMPL"), company("XMPL")], ["net_margin", "revenue"], years=10, index=False
    )
    keys = [(r.cik, r.metric_id, r.fiscal_year_label) for r in result.rows]
    assert keys == [
        ("0000000902", "net_margin", "FY2024"), ("0000000902", "net_margin", "FY2025"),
        ("0000000902", "revenue", "FY2024"), ("0000000902", "revenue", "FY2025"),
        ("0000000901", "net_margin", "FY2024"), ("0000000901", "net_margin", "FY2025"),
        ("0000000901", "revenue", "FY2024"), ("0000000901", "revenue", "FY2025"),
    ]
    assert result.metrics == ["net_margin", "revenue"]
    assert [c.ticker for c in result.companies] == ["SMPL", "XMPL"]


def test_units_are_the_currency_or_ratio_and_values_are_not_rounded() -> None:
    result = cmp.compare([company("XMPL"), company("EURO")], ["revenue", "net_margin"], 10, False)
    revenue = rows_for(result, "EURO", "revenue")
    assert [(r.value, r.unit) for r in revenue] == [(300, "EUR"), (330, "EUR")]
    margin = rows_for(result, "XMPL", "net_margin")
    assert [(r.value, r.unit) for r in margin] == [(0.10, "ratio"), (0.12, "ratio")]


def test_missing_value_stays_a_row_with_null_and_its_reason() -> None:
    result = cmp.compare([company("XMPL"), company("SMPL")], ["net_margin"], 10, False)
    fy2025 = rows_for(result, "SMPL", "net_margin")[1]
    assert fy2025.value is None
    assert fy2025.status == "missing"
    assert fy2025.reason == "no fact for this period"


def test_provenance_and_data_source_are_carried() -> None:
    result = cmp.compare([company("XMPL"), company("SMPL")], ["revenue", "net_margin"], 10, False)
    revenue = rows_for(result, "XMPL", "revenue")[0]
    assert (revenue.source_concept, revenue.accession) == ("Revenues", "0000000901-24-000001")
    assert revenue.kind == "reported" and revenue.data_source == LABEL
    margin = rows_for(result, "XMPL", "net_margin")[0]
    assert margin.kind == "derived" and margin.source_concept is None


def test_years_keeps_the_latest_periods_of_each_company() -> None:
    result = cmp.compare([company("XMPL"), company("SMPL")], ["revenue"], years=1, index=False)
    assert [r.fiscal_year_label for r in result.rows] == ["FY2025", "FY2025"]


# ------------------------------------------------------------------ year-ends and currencies


def test_m4_ac3_different_year_ends_warn_and_keep_each_period_end() -> None:
    result = cmp.compare([company("XMPL"), company("SMPL")], ["revenue"], 10, False)
    assert {c.ticker: c.fiscal_year_end for c in result.companies} == {
        "XMPL": "12-31", "SMPL": "06-30",
    }
    assert [w.code for w in result.warnings] == ["fiscal_years_not_aligned"]
    assert result.warnings[0].message == "Fiscal years are not aligned"
    ends = [r.period_end for r in rows_for(result, "SMPL", "revenue")]
    assert ends == [date(2024, 6, 30), date(2025, 6, 30)]


def test_same_year_ends_give_no_alignment_warning() -> None:
    result = cmp.compare([company("XMPL"), company("FRML")], ["revenue"], 10, False)
    assert result.warnings == []


def test_m4_ac4_currencies_differ_warns_and_keeps_own_units_and_ratios() -> None:
    result = cmp.compare([company("XMPL"), company("EURO")], ["revenue", "net_margin"], 10, False)
    warning = next(w for w in result.warnings if w.code == "currencies_differ")
    assert warning.message == "Different reporting currencies (USD, EUR): not converted"
    assert {r.unit for r in rows_for(result, "XMPL", "revenue")} == {"USD"}
    assert {r.unit for r in rows_for(result, "EURO", "revenue")} == {"EUR"}
    assert all(r.value is not None for r in rows_for(result, "EURO", "net_margin"))


def test_currencies_differ_only_matters_for_money_metrics() -> None:
    result = cmp.compare([company("XMPL"), company("EURO")], ["net_margin"], 10, False)
    assert "currencies_differ" not in [w.code for w in result.warnings]


# ------------------------------------------------------------------ indexing


def test_calc11_m4_ac5_index_each_company_on_its_own_base_period() -> None:
    result = cmp.compare([company("XMPL"), company("SMPL")], ["revenue"], 10, index=True)
    example = rows_for(result, "XMPL", "revenue")
    sample = rows_for(result, "SMPL", "revenue")
    assert [r.value for r in example] == [pytest.approx(100.0, abs=0.05),
                                          pytest.approx(125.0, abs=0.05)]
    assert [r.value for r in sample] == [pytest.approx(100.0, abs=0.05),
                                         pytest.approx(80.0, abs=0.05)]
    assert all(r.indexed and r.unit == "index" for r in example + sample)
    assert result.index_base.fiscal_year_by_cik == {"0000000901": "FY2024", "0000000902": "FY2024"}
    assert result.index_base.period_end_by_cik == {
        "0000000901": date(2024, 12, 31), "0000000902": date(2024, 6, 30),
    }


def test_ratios_are_never_indexed() -> None:
    result = cmp.compare([company("XMPL"), company("SMPL")], ["net_margin", "revenue"], 10, True)
    margins = rows_for(result, "XMPL", "net_margin")
    assert [(r.value, r.unit, r.indexed) for r in margins] == [(0.10, "ratio", False),
                                                               (0.12, "ratio", False)]


def test_m4_e1_no_common_fiscal_year_means_no_index() -> None:
    result = cmp.compare([company("XMPL"), company("GAPC")], ["revenue"], 10, index=True)
    assert result.index_base is None
    codes = [w.code for w in result.warnings]
    assert "no_common_fiscal_year" in codes
    message = next(w.message for w in result.warnings if w.code == "no_common_fiscal_year")
    assert message == "No common fiscal year to index from"
    assert not any(r.indexed for r in result.rows)
    assert [r.value for r in rows_for(result, "XMPL", "revenue")] == [800, 1000]


def test_base_at_or_below_zero_makes_that_company_unavailable() -> None:
    # Sample Ltd FCF at the base year FY2024 is -10: an index from it would mislead.
    result = cmp.compare([company("XMPL"), company("SMPL")], ["fcf"], 10, index=True)
    sample = rows_for(result, "SMPL", "fcf")
    assert all(r.value is None and r.status == "unavailable" and r.indexed for r in sample)
    assert sample[0].reason == "index base FY2024 is ≤ 0 (-10 USD)"
    assert [r.value for r in rows_for(result, "XMPL", "fcf")] == [100.0, 140.0]
    assert "index_base_unavailable" in [w.code for w in result.warnings]


def test_index_without_an_absolute_metric_has_no_base() -> None:
    result = cmp.compare([company("XMPL"), company("SMPL")], ["net_margin"], 10, index=True)
    assert result.index_base is None
    assert not any(r.indexed for r in result.rows)


def test_index_off_returns_absolute_values() -> None:
    result = cmp.compare([company("XMPL"), company("SMPL")], ["revenue"], 10, index=False)
    assert result.index_base is None
    assert [r.value for r in rows_for(result, "XMPL", "revenue")] == [800, 1000]


# ------------------------------------------------------------------ fixture known answer FX16


def _fixture_company(cik: str) -> cmp.CompanyInput:
    store = FixtureStore(Settings(data_mode="fixtures").fixtures_dir)
    facts = store.companyfacts(cik)
    financials = build_financials(facts, f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json")
    profile = store.submissions(cik)
    return cmp.CompanyInput(
        cik=cik, ticker=profile["tickers"][0], name=profile["name"],
        currency=financials.currency, series=financials.series, data_source="RECORDED SEC DEMO",
    )


def test_fx16_apple_and_microsoft_revenue_index() -> None:
    result = cmp.compare(
        [_fixture_company("0000320193"), _fixture_company("0000789019")], ["revenue"], 10, True
    )
    assert result.index_base.fiscal_year_by_cik == {"0000320193": "FY2017", "0000789019": "FY2017"}
    assert result.index_base.period_end_by_cik == {
        "0000320193": date(2017, 9, 30), "0000789019": date(2017, 6, 30),
    }
    by_key = {(r.cik, r.fiscal_year_label): r.value for r in result.rows}
    assert by_key[("0000320193", "FY2017")] == pytest.approx(100.0, abs=0.01)
    assert by_key[("0000789019", "FY2017")] == pytest.approx(100.0, abs=0.01)
    assert by_key[("0000320193", "FY2026")] == pytest.approx(208.88, abs=0.01)
    assert by_key[("0000789019", "FY2026")] == pytest.approx(343.62, abs=0.01)
    assert "fiscal_years_not_aligned" in [w.code for w in result.warnings]


def test_index_available_says_whether_the_toggle_can_be_used() -> None:
    # The toggle is disabled without a common fiscal year (M4-E1) or without a money metric,
    # also while indexing is off, so the screen never has to work this out itself.
    assert cmp.compare([company("XMPL"), company("SMPL")], ["revenue"], 10, False).index_available
    assert not cmp.compare([company("XMPL"), company("GAPC")], ["revenue"], 10, False
                           ).index_available
    assert not cmp.compare([company("XMPL"), company("SMPL")], ["net_margin"], 10, False
                           ).index_available


# ------------------------------------------------------------------ test review 2026-11-09


def test_base_is_the_first_label_where_every_company_has_a_value() -> None:
    # Late Start has no FY2024 revenue, so the common base is FY2025, not the window's first label.
    result = cmp.compare([company("XMPL"), company("LATE")], ["revenue"], 10, index=True)
    assert result.index_base.fiscal_year_by_cik == {"0000000901": "FY2025", "0000000906": "FY2025"}
    example = rows_for(result, "XMPL", "revenue")
    assert [r.value for r in example] == [80.0, 100.0]  # 800 / 1,000 and 1,000 / 1,000, x 100
    late = rows_for(result, "LATE", "revenue")
    assert (late[0].value, late[0].indexed, late[1].value) == (None, True, 100.0)


def test_several_money_metrics_share_one_base_label() -> None:
    # Partial FCF has revenue in FY2024 but FCF only from FY2025: both metrics use base FY2025.
    result = cmp.compare([company("XMPL"), company("PART")], ["revenue", "fcf"], 10, index=True)
    assert set(result.index_base.fiscal_year_by_cik.values()) == {"FY2025"}
    revenue = rows_for(result, "PART", "revenue")
    assert [r.value for r in revenue] == [80.0, 100.0]  # 400 / 500 and 500 / 500, x 100
    assert [r.value for r in rows_for(result, "XMPL", "fcf")] == [pytest.approx(50 / 70 * 100),
                                                                  100.0]


def test_a_zero_base_is_unavailable_not_a_division_error() -> None:
    result = cmp.compare([company("XMPL"), company("ZERO")], ["fcf"], 10, index=True)
    zero = rows_for(result, "ZERO", "fcf")
    assert all(r.value is None and r.status == "unavailable" for r in zero)
    assert zero[0].reason == "index base FY2024 is ≤ 0 (0 USD)"
