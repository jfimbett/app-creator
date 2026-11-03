"""Annual period selection and the duplicate policy (brief §7 "Periods", §9 `test_periods.py`).

SYNTHETIC: invented for tests, not SEC data. Every fact below is made up and only shaped like
SEC Company Facts (`facts.us-gaap.<concept>.units.<unit>[...]`); values and accessions are fake.
"""

from datetime import date, timedelta

import pytest

from app.logic import periods
from app.logic.periods import (
    REVENUE_MISSING_REASON,
    Period,
    annual_facts,
    annual_periods,
    choose_fact,
    fiscal_year_label,
    instant_at,
    is_annual_duration,
    is_instant,
    parse_facts,
    pick_first,
    reporting_currency,
)

SYNTHETIC_MARKER = "SYNTHETIC: invented for tests, not SEC data"
REV = "Revenues"
REV_ASC606 = "RevenueFromContractWithCustomerExcludingAssessedTax"
NI = "NetIncomeLoss"
CONCEPTS = (REV, REV_ASC606, "SalesRevenueNet", NI, "Assets")
REVENUE_PRIORITY = (REV, REV_ASC606, "SalesRevenueNet")

FY2023 = Period(date(2022, 10, 1), date(2023, 9, 30))  # 364 days
FY2024 = Period(date(2023, 10, 1), date(2024, 9, 28))  # 363 days
FY2025 = Period(date(2024, 9, 29), date(2025, 9, 27))  # 363 days


def fact(
    val: float,
    *,
    period: Period | None = None,
    start: str | None = None,
    end: str | None = None,
    form: str = "10-K",
    filed: str = "2025-11-01",
    accn: str = "0000000001-25-000001",
    fy: int = 2025,
    fp: str = "FY",
) -> dict:
    """One synthetic fact row in Company Facts shape."""
    if period is not None:
        start, end = period.start.isoformat(), period.end.isoformat()
    row = {"end": end, "val": val, "accn": accn, "fy": fy, "fp": fp, "form": form, "filed": filed}
    if start is not None:
        row["start"] = start
    return row


def companyfacts(concepts: dict[str, dict[str, list[dict]]]) -> dict:
    """A synthetic Company Facts document: {concept: {unit: [fact rows]}}."""
    return {
        "_synthetic": SYNTHETIC_MARKER,
        "cik": 1,
        "entityName": "Synthetic Test Co",
        "facts": {
            "us-gaap": {
                name: {"label": name, "description": "synthetic", "units": units}
                for name, units in concepts.items()
            }
        },
    }


def selected(concepts: dict[str, dict[str, list[dict]]], unit: str = "USD"):
    """Parse a synthetic document and run the annual selection for `unit`."""
    return annual_facts(parse_facts(companyfacts(concepts), CONCEPTS), unit)


# --- duration vs instant -------------------------------------------------------------------


@pytest.mark.parametrize("days", [364, 371, 350, 380])
def test_annual_length_durations_are_annual(days: int) -> None:
    start = date(2023, 1, 1)
    end = start + timedelta(days=days)
    doc = companyfacts({REV: {"USD": [fact(1, start=str(start), end=str(end))]}})
    [f] = parse_facts(doc, CONCEPTS)
    assert is_annual_duration(f)


@pytest.mark.parametrize("days", [349, 381, 91, 273])
def test_other_durations_are_not_annual(days: int) -> None:
    start = date(2023, 1, 1)
    end = start + timedelta(days=days)
    doc = companyfacts({REV: {"USD": [fact(1, start=str(start), end=str(end))]}})
    [f] = parse_facts(doc, CONCEPTS)
    assert not is_annual_duration(f)
    assert annual_facts([f], "USD") == {}


def test_instant_fact_is_not_a_duration() -> None:
    [f] = parse_facts(companyfacts({"Assets": {"USD": [fact(500, end="2024-09-28")]}}), CONCEPTS)
    assert is_instant(f)
    assert f.start is None
    assert not is_annual_duration(f)
    assert annual_facts([f], "USD") == {}


def test_instant_matches_annual_period_end_exactly() -> None:
    facts = parse_facts(
        companyfacts(
            {
                "Assets": {
                    "USD": [
                        fact(500, end="2024-09-28", filed="2024-11-01"),
                        fact(
                            510, end="2024-09-28", filed="2025-11-01", accn="0000000001-25-000002"
                        ),
                        fact(400, end="2024-06-29", form="10-Q"),
                        fact(450, end="2024-09-27"),
                    ]
                }
            }
        ),
        CONCEPTS,
    )
    chosen = instant_at(facts, "Assets", "USD", FY2024.end)
    assert chosen is not None and chosen.val == 510  # latest filed wins, never 500 + 510
    assert instant_at(facts, "Assets", "USD", date(2024, 6, 29)) is None  # 10-Q only
    assert instant_at(facts, "Assets", "EUR", FY2024.end) is None


# --- forms --------------------------------------------------------------------------------


def test_ten_q_fact_of_annual_length_is_ignored() -> None:
    sel = selected({REV: {"USD": [fact(999, period=FY2024, form="10-Q", filed="2025-12-01")]}})
    assert sel == {}


def test_ten_q_filed_later_does_not_replace_the_ten_k_value() -> None:
    sel = selected(
        {
            REV: {
                "USD": [
                    fact(1_000, period=FY2024, form="10-K", filed="2024-11-01"),
                    fact(999, period=FY2024, form="10-Q", filed="2025-02-01"),
                ]
            }
        }
    )
    assert sel[(REV, FY2024)].val == 1_000


def test_quarterly_and_ytd_facts_are_excluded_from_the_annual_series() -> None:
    sel = selected(
        {
            REV: {
                "USD": [
                    fact(100, start="2024-07-01", end="2024-09-28"),  # quarter inside a 10-K
                    fact(300, start="2023-10-01", end="2024-06-29"),  # 9-month YTD
                    fact(400, period=FY2024),
                ]
            }
        }
    )
    assert list(sel) == [(REV, FY2024)]
    assert sel[(REV, FY2024)].val == 400


# --- duplicates and restatements ----------------------------------------------------------


def test_restated_value_in_ten_k_a_replaces_original_and_is_never_summed() -> None:
    sel = selected(
        {
            REV: {
                "USD": [
                    fact(1_000, period=FY2024, form="10-K", filed="2024-11-01",
                         accn="0000000001-24-000050"),
                    fact(1_010, period=FY2024, form="10-K/A", filed="2025-02-01",
                         accn="0000000001-25-000010"),
                ]
            }
        }
    )
    chosen = sel[(REV, FY2024)]
    assert chosen.val == 1_010
    assert chosen.val != 2_010
    assert chosen.form == "10-K/A"
    assert chosen.accn == "0000000001-25-000010"
    assert chosen.filed == date(2025, 2, 1)


@pytest.mark.parametrize("order", [(0, 1), (1, 0)])
def test_same_filed_date_keeps_higher_accession_on_every_run(order: tuple[int, int]) -> None:
    rows = [
        fact(7, period=FY2024, filed="2024-11-01", accn="0000000001-24-000101"),
        fact(8, period=FY2024, filed="2024-11-01", accn="0000000001-24-000099"),
    ]
    for _ in range(3):
        sel = selected({REV: {"USD": [rows[i] for i in order]}})
        assert sel[(REV, FY2024)].accn == "0000000001-24-000101"
        assert sel[(REV, FY2024)].val == 7


def test_choose_fact_prefers_latest_filed_over_higher_accession() -> None:
    facts = parse_facts(
        companyfacts(
            {
                REV: {
                    "USD": [
                        fact(1, period=FY2024, filed="2025-01-01", accn="0000000001-24-000001"),
                        fact(2, period=FY2024, filed="2024-12-31", accn="0000000001-24-999999"),
                    ]
                }
            }
        ),
        CONCEPTS,
    )
    assert choose_fact(facts).val == 1


# --- periods by start/end, never by fy ----------------------------------------------------


def test_comparative_in_later_ten_k_lands_in_its_own_period_not_the_filing_fy() -> None:
    sel = selected(
        {
            REV: {
                "USD": [
                    # One FY2025 10-K (fy 2025) repeats two earlier years as comparatives.
                    fact(300, period=FY2025, fy=2025, filed="2025-11-01"),
                    fact(200, period=FY2024, fy=2025, filed="2025-11-01"),
                    fact(100, period=FY2023, fy=2025, filed="2025-11-01"),
                ]
            }
        }
    )
    assert annual_periods(sel) == [FY2023, FY2024, FY2025]
    assert sel[(REV, FY2023)].val == 100
    assert sel[(REV, FY2023)].fy == 2025  # provenance keeps the filing's fy as reported
    assert FY2023.label == "FY2023"
    assert fiscal_year_label(FY2023.end) == "FY2023"


def test_two_periods_with_the_same_fy_are_not_merged() -> None:
    sel = selected(
        {
            REV: {
                "USD": [
                    fact(200, period=FY2024, fy=2024, filed="2024-11-01"),
                    fact(100, period=FY2023, fy=2024, filed="2024-11-01"),
                ]
            }
        }
    )
    assert annual_periods(sel) == [FY2023, FY2024]
    assert {f.val for f in sel.values()} == {100, 200}


def test_fiscal_year_label_uses_year_of_end_date() -> None:
    assert fiscal_year_label(date(2024, 6, 30)) == "FY2024"
    assert Period(date(2023, 7, 1), date(2024, 6, 30)).label == "FY2024"


# --- revenue concept priority -------------------------------------------------------------


def test_each_year_uses_its_own_revenue_concept_never_a_sum() -> None:
    sel = selected(
        {
            REV_ASC606: {"USD": [fact(900, period=FY2023)]},
            REV: {"USD": [fact(1_000, period=FY2024)]},
        }
    )
    y2023 = pick_first(sel, REVENUE_PRIORITY, FY2023, REVENUE_MISSING_REASON)
    y2024 = pick_first(sel, REVENUE_PRIORITY, FY2024, REVENUE_MISSING_REASON)
    assert (y2023.value, y2023.fact.concept) == (900, REV_ASC606)
    assert (y2024.value, y2024.fact.concept) == (1_000, REV)
    assert y2023.status == y2024.status == "ok"


def test_first_concept_in_priority_wins_when_both_present() -> None:
    sel = selected(
        {
            REV: {"USD": [fact(1_000, period=FY2024)]},
            REV_ASC606: {"USD": [fact(950, period=FY2024)]},
        }
    )
    chosen = pick_first(sel, REVENUE_PRIORITY, FY2024, REVENUE_MISSING_REASON)
    assert chosen.value == 1_000
    assert chosen.fact.concept == REV


def test_year_without_revenue_concept_is_missing_not_zero() -> None:
    sel = selected(
        {
            REV: {"USD": [fact(1_000, period=FY2024)]},
            NI: {"USD": [fact(50, period=FY2023), fact(60, period=FY2024)]},
        }
    )
    assert annual_periods(sel) == [FY2023, FY2024]
    missing = pick_first(sel, REVENUE_PRIORITY, FY2023, REVENUE_MISSING_REASON)
    assert missing.value is None
    assert missing.status == "missing"
    assert missing.reason == "no mapped revenue concept"
    assert missing.fact is None
    assert missing.period == FY2023


def test_zero_reported_value_stays_zero_and_ok() -> None:
    sel = selected({NI: {"USD": [fact(0, period=FY2024)]}})
    chosen = pick_first(sel, (NI,), FY2024, "no NetIncomeLoss fact")
    assert chosen.value == 0
    assert chosen.status == "ok"


# --- units --------------------------------------------------------------------------------


def test_only_reporting_currency_is_used_next_to_eur() -> None:
    doc = companyfacts(
        {
            REV: {
                "USD": [fact(1_000, period=FY2023), fact(1_100, period=FY2024)],
                "EUR": [fact(920, period=FY2024)],
            }
        }
    )
    facts = parse_facts(doc, CONCEPTS)
    unit = reporting_currency(facts, REVENUE_PRIORITY)
    assert unit == "USD"
    sel = annual_facts(facts, unit)
    assert {f.unit for f in sel.values()} == {"USD"}
    assert sel[(REV, FY2024)].val == 1_100


def test_reporting_currency_ignores_non_currency_units_and_annual_filter() -> None:
    doc = companyfacts(
        {
            REV: {
                "USD": [fact(1, period=FY2024)],
                "EUR": [
                    fact(1, start="2024-01-01", end="2024-03-31", form="10-Q"),
                    fact(2, start="2024-04-01", end="2024-06-30", form="10-Q"),
                ],
                "USD/shares": [fact(3, period=FY2023), fact(4, period=FY2025)],
            }
        }
    )
    assert reporting_currency(parse_facts(doc, CONCEPTS), REVENUE_PRIORITY) == "USD"


def test_reporting_currency_is_none_without_annual_revenue() -> None:
    assert reporting_currency([], REVENUE_PRIORITY) is None


# --- parsing ------------------------------------------------------------------------------


def test_parse_keeps_provenance_fields_and_only_requested_concepts() -> None:
    doc = companyfacts(
        {
            REV: {"USD": [fact(1_000, period=FY2024, accn="0000000001-24-000101", fy=2024)]},
            "SomethingElse": {"USD": [fact(5, period=FY2024)]},
        }
    )
    [f] = parse_facts(doc, CONCEPTS)
    assert f.concept == REV
    assert f.taxonomy == "us-gaap"
    assert f.unit == "USD"
    assert (f.start, f.end) == (FY2024.start, FY2024.end)
    assert (f.form, f.accn, f.filed, f.fy, f.fp) == (
        "10-K",
        "0000000001-24-000101",
        date(2025, 11, 1),
        2024,
        "FY",
    )


def test_parse_handles_absent_concepts_and_taxonomy() -> None:
    assert parse_facts({"facts": {}}, CONCEPTS) == []
    assert parse_facts(companyfacts({}), CONCEPTS) == []


def test_module_is_pure() -> None:
    source = open(periods.__file__, encoding="utf-8").read()
    for forbidden in ("import httpx", "open(", "datetime.now", "date.today", "import os"):
        assert forbidden not in source
