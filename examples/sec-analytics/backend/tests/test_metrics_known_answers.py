"""Ratio functions against hand-worked answers (M2-AC7).

CALC1-CALC10 use the SYNTHETIC Example Co inputs. FX5-FX15 use the authentic recorded fixtures.
Every expected value is copied from milestones/acceptance.md, never from this code's output.
"""

import copy
import json
from pathlib import Path

import pytest

from app.data.fixtures import FixtureStore, default_fixtures_dir
from app.logic.statements import build_financials

EXAMPLE = json.loads(
    (Path(__file__).parent / "synthetic" / "example_co.json").read_text(encoding="utf-8")
)
URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK0000000001.json"
APPLE, MICROSOFT, ALPHABET = "0000320193", "0000789019", "0001652044"
STORE = FixtureStore(default_fixtures_dir())
TOLERANCE = 0.000001


def _latest(document: dict, metric_id: str):
    return build_financials(document, URL).series[metric_id][-1]


@pytest.mark.parametrize(
    ("calc", "metric_id", "expected"),
    [
        ("CALC1", "revenue_growth", 0.25),
        ("CALC2", "operating_margin", 0.25),
        ("CALC3", "net_margin", 0.15),
        ("CALC4", "fcf", 180),
        ("CALC4", "fcf_margin", 0.18),
        ("CALC5", "ebit", 200),
        ("CALC5", "ebitda", 250),
        ("CALC6", "working_capital", 200),
        ("CALC7", "debt", 300),
        ("CALC7", "debt_to_equity", 0.5),
        ("CALC8", "roe", 0.30),
    ],
)
def test_calc_exact(calc: str, metric_id: str, expected: float) -> None:
    value = _latest(EXAMPLE, metric_id)
    assert (value.status, value.kind) == ("ok", "derived"), calc
    assert value.value == pytest.approx(expected, abs=1e-12), calc


def test_calc9_roa_uses_average_assets() -> None:
    assert _latest(EXAMPLE, "roa").value == pytest.approx(0.136364, abs=TOLERANCE)


def test_calc10_roe_falls_back_to_ending_equity_with_a_label() -> None:
    document = copy.deepcopy(EXAMPLE)
    rows = document["facts"]["us-gaap"]["StockholdersEquity"]["units"]["USD"]
    document["facts"]["us-gaap"]["StockholdersEquity"]["units"]["USD"] = rows[1:]
    roe = _latest(document, "roe")
    assert roe.value == pytest.approx(0.25, abs=1e-12)
    assert roe.note == "ending balance (prior year unavailable)"


def test_ebit_is_not_operating_income() -> None:
    assert _latest(EXAMPLE, "ebit").value == 200
    assert _latest(EXAMPLE, "operating_income").value == 250


def test_derived_values_carry_formula_and_inputs() -> None:
    value = _latest(EXAMPLE, "net_margin")
    assert value.formula == "net income ÷ revenue"
    assert [i.metric_id for i in value.inputs] == ["net_income", "revenue"]
    assert value.inputs[0].provenance.accession == "0000000001-26-000001"


def _fixture(cik: str, metric_id: str):
    return _latest(STORE.companyfacts(cik), metric_id)


@pytest.mark.parametrize(
    ("fx", "cik", "metric_id", "expected"),
    [
        ("FX5", APPLE, "net_margin", 0.276035),
        ("FX7", APPLE, "debt_to_equity", 0.714683),
        ("FX8", APPLE, "roe", 1.422567),
        ("FX9", APPLE, "revenue_growth", 0.150598),
        ("FX15", APPLE, "roa", 0.346103),
        ("FX10", MICROSOFT, "net_margin", 0.403054),
        ("FX12", MICROSOFT, "debt_to_equity", 0.091083),
        ("FX13", MICROSOFT, "roe", 0.340386),
    ],
)
def test_fixture_ratios(fx: str, cik: str, metric_id: str, expected: float) -> None:
    value = _fixture(cik, metric_id)
    assert value.status == "ok", fx
    assert value.value == pytest.approx(expected, abs=TOLERANCE), fx


@pytest.mark.parametrize(
    ("fx", "cik", "metric_id", "expected"),
    [
        ("FX6", APPLE, "fcf", 136_056_000_000),
        ("FX11", MICROSOFT, "fcf", 66_987_000_000),
        ("FX14", MICROSOFT, "ebit", 168_985_000_000),
        ("FX7", APPLE, "debt", 80_111_000_000),
        ("FX12", MICROSOFT, "debt", 40_294_000_000),
    ],
)
def test_fixture_amounts(fx: str, cik: str, metric_id: str, expected: int) -> None:
    value = _fixture(cik, metric_id)
    assert (value.status, value.value) == ("ok", expected), fx


def test_microsoft_interest_uses_the_alternate_concept() -> None:
    interest = _fixture(MICROSOFT, "interest_expense")
    assert interest.provenance.concept == "InterestExpenseNonoperating"
    assert interest.value == 3_051_000_000


def test_apple_ebit_is_unavailable_and_never_operating_income() -> None:
    ebit = _fixture(APPLE, "ebit")
    assert (ebit.status, ebit.value) == ("unavailable", None)
    assert "interest expense" in ebit.reason
    ebitda = _fixture(APPLE, "ebitda")
    assert (ebitda.status, ebitda.value) == ("unavailable", None)


@pytest.mark.parametrize("cik", [MICROSOFT, ALPHABET])
def test_no_mapped_d_and_a_leaves_ebitda_unavailable(cik: str) -> None:
    assert _fixture(cik, "d_and_a").status == "missing"
    assert _fixture(cik, "d_and_a").reason == "no mapped D&A concept"
    assert _fixture(cik, "ebitda").status == "unavailable"


def test_debt_lists_components_not_reported() -> None:
    debt = _fixture(MICROSOFT, "debt")
    assert debt.note == "Not reported at this date: debt_short_term"
