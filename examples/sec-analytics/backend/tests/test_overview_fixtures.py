"""Overview against the hand-worked known answers FX1-FX4 (milestones/acceptance.md, M1-AC5).

Expected values, periods and accessions are copied from the FX rows, which were read by hand from
the AUTHENTIC fixture files (snapshot 2026-11-03), never from the app's output. A recapture changes
them: work the rows out again first.
"""

import json
from pathlib import Path

import pytest

from app.logic.statements import (
    NET_INCOME_MISSING_REASON,
    RESTATEMENT_NOTE,
    overview,
)

FIXTURES_DIR = Path(__file__).resolve().parents[2] / "fixtures"
APPLE, MICROSOFT, ALPHABET = "0000320193", "0000789019", "0001652044"


def _facts(cik: str) -> dict:
    path = FIXTURES_DIR / "companyfacts" / f"CIK{cik}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _url(cik: str) -> str:
    return f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"


# (cik, metric_id, concept, start, end, accession, filed, val, fy) from FX1-FX4.
KNOWN_ANSWERS = [
    pytest.param(APPLE, "revenue", "RevenueFromContractWithCustomerExcludingAssessedTax",
                 "2025-09-28", "2026-09-26", "0000320193-26-000026", "2026-11-03",
                 478834000000, 2026, id="FX1"),
    pytest.param(APPLE, "net_income", "NetIncomeLoss",
                 "2025-09-28", "2026-09-26", "0000320193-26-000026", "2026-11-03",
                 132175000000, 2026, id="FX2"),
    pytest.param(MICROSOFT, "revenue", "RevenueFromContractWithCustomerExcludingAssessedTax",
                 "2025-07-01", "2026-06-30", "0001193125-26-323660", "2026-07-29",
                 331839000000, 2026, id="FX3"),
    pytest.param(MICROSOFT, "net_income", "NetIncomeLoss",
                 "2025-07-01", "2026-06-30", "0001193125-26-323660", "2026-07-29",
                 133749000000, 2026, id="FX4"),
]


@pytest.mark.parametrize(
    ("cik", "metric_id", "concept", "start", "end", "accn", "filed", "val", "fy"), KNOWN_ANSWERS
)
def test_key_figure_equals_known_answer(cik, metric_id, concept, start, end, accn, filed, val,
                                        fy) -> None:
    result = overview(_facts(cik), _url(cik))
    figure = next(m for m in result.key_figures if m.metric_id == metric_id)
    assert figure.status == "ok"
    assert figure.kind == "reported"
    assert figure.value == val
    assert figure.unit == "USD"
    assert figure.fiscal_year_label == "FY2026"
    assert (figure.period_start.isoformat(), figure.period_end.isoformat()) == (start, end)
    prov = figure.provenance
    assert (prov.concept, prov.taxonomy, prov.unit) == (concept, "us-gaap", "USD")
    assert (prov.form, prov.accession, prov.filed.isoformat()) == ("10-K", accn, filed)
    assert (prov.fy, prov.fp) == (fy, "FY")
    assert prov.source_url == _url(cik)


@pytest.mark.parametrize(
    ("cik", "metric_id", "concept", "start", "end", "accn", "filed", "val", "fy"), KNOWN_ANSWERS
)
def test_latest_chart_row_equals_known_answer(cik, metric_id, concept, start, end, accn, filed,
                                              val, fy) -> None:
    row = overview(_facts(cik), _url(cik)).chart[-1]
    assert (row.fiscal_year_label, row.period_end.isoformat()) == ("FY2026", end)
    cell = getattr(row, metric_id)
    assert (cell.value, cell.provenance.accession, cell.provenance.concept) == (val, accn, concept)


def test_fx4_excludes_the_later_def_14a_fact() -> None:
    """FX4: the DEF 14A copy (filed later) is not a 10-K/10-K/A, so the 10-K stays the source."""
    row = overview(_facts(MICROSOFT), _url(MICROSOFT)).chart[-1]
    assert row.net_income.provenance.accession == "0001193125-26-323660"
    assert row.net_income.provenance.form == "10-K"


# Annual periods counted by hand (acceptance.md, below FX4): (count, earliest end, latest end).
PERIOD_COUNTS = [
    (APPLE, 20, "2007-09-29", "2026-09-26"),
    (MICROSOFT, 19, "2008-06-30", "2026-06-30"),
    (ALPHABET, 13, "2013-12-31", "2025-12-31"),
]


@pytest.mark.parametrize(("cik", "count", "earliest", "latest"), PERIOD_COUNTS)
def test_all_annual_periods_in_snapshot(cik, count, earliest, latest) -> None:
    chart = overview(_facts(cik), _url(cik)).chart
    assert len(chart) == count >= 5
    assert chart[0].period_end.isoformat() == earliest
    assert chart[-1].period_end.isoformat() == latest
    ends = [row.period_end for row in chart]
    assert ends == sorted(ends) and len(set(ends)) == len(ends)


@pytest.mark.parametrize("cik", [APPLE, MICROSOFT, ALPHABET])
def test_every_value_is_reported_with_provenance_or_missing(cik) -> None:
    for row in overview(_facts(cik), _url(cik)).chart:
        for cell in (row.revenue, row.net_income):
            assert cell.kind == "reported"
            assert cell.fiscal_year_label == row.fiscal_year_label
            if cell.status == "ok":
                assert cell.value is not None and cell.provenance is not None
            else:
                assert cell.value is None and cell.reason


def test_years_keeps_the_latest_periods() -> None:
    result = overview(_facts(APPLE), _url(APPLE), years=5)
    assert [r.fiscal_year_label for r in result.chart] == [
        "FY2022", "FY2023", "FY2024", "FY2025", "FY2026"
    ]
    assert result.key_figures[0].value == 478834000000


def test_notes_carry_the_restatement_warning() -> None:
    assert RESTATEMENT_NOTE == "Values may reflect later restatements; not point-in-time."
    assert RESTATEMENT_NOTE in overview(_facts(APPLE), _url(APPLE)).notes


# --- SYNTHETIC: invented for tests, not SEC data -------------------------------------------------


def _synthetic(concepts: dict) -> dict:
    """A Company Facts-shaped document with invented values (SYNTHETIC, not SEC data)."""
    return {"_synthetic": "SYNTHETIC: invented for tests, not SEC data", "cik": 1,
            "entityName": "Test Co", "facts": {"us-gaap": concepts}}


def _row(val, start, end, accn="0000000001-25-000001", filed="2025-11-01") -> dict:
    return {"start": start, "end": end, "val": val, "accn": accn, "fy": 2025, "fp": "FY",
            "form": "10-K", "filed": filed}


def test_missing_net_income_has_its_own_reason() -> None:
    doc = _synthetic({
        "Revenues": {"units": {"USD": [_row(100, "2023-01-01", "2023-12-31"),
                                       _row(120, "2024-01-01", "2024-12-31")]}},
        "NetIncomeLoss": {"units": {"USD": [_row(10, "2023-01-01", "2023-12-31")]}},
    })
    result = overview(doc, "https://data.sec.gov/api/xbrl/companyfacts/CIK0000000001.json")
    last = result.chart[-1]
    assert last.net_income.status == "missing"
    assert last.net_income.value is None
    assert last.net_income.reason == NET_INCOME_MISSING_REASON == "no NetIncomeLoss fact"
    # The key figure is the latest *reported* net income, never a missing year or a zero.
    net = next(m for m in result.key_figures if m.metric_id == "net_income")
    assert (net.value, net.fiscal_year_label) == (10, "FY2023")


def test_missing_revenue_stays_null() -> None:
    doc = _synthetic({
        "Revenues": {"units": {"USD": [_row(100, "2023-01-01", "2023-12-31")]}},
        "NetIncomeLoss": {"units": {"USD": [_row(-5, "2024-01-01", "2024-12-31")]}},
    })
    result = overview(doc, "https://data.sec.gov/api/xbrl/companyfacts/CIK0000000001.json")
    row = result.chart[-1]
    assert row.fiscal_year_label == "FY2024"
    assert (row.revenue.status, row.revenue.value) == ("missing", None)
    assert row.revenue.reason == "no mapped revenue concept"
    assert row.net_income.value == -5  # a reported loss stays negative
    revenue = next(m for m in result.key_figures if m.metric_id == "revenue")
    assert (revenue.value, revenue.fiscal_year_label) == (100, "FY2023")


def test_no_revenue_at_all_means_no_currency_and_no_chart() -> None:
    doc = _synthetic({
        "NetIncomeLoss": {"units": {"USD": [_row(-5, "2024-01-01", "2024-12-31")]}},
    })
    result = overview(doc, "https://data.sec.gov/api/xbrl/companyfacts/CIK0000000001.json")
    assert (result.chart, result.key_figures) == ([], [])
    assert result.notes


def test_no_annual_facts_gives_empty_overview() -> None:
    result = overview(_synthetic({}), "https://data.sec.gov/api/xbrl/companyfacts/CIK0000000001.json")
    assert result.chart == []
    assert result.key_figures == []
