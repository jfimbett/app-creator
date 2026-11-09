"""Filing list rules: forms, amendments, latest, window, labels (M3-AC1, AC2, E1, E4). Offline."""

import json
from datetime import date, datetime, timezone
from pathlib import Path

import pytest

from app.logic import archive, filings
from app.models.common import SourceInfo

SYNTHETIC = json.loads(
    (Path(__file__).parent / "synthetic" / "filings" / "amended_submissions.json").read_text()
)
RECENT = SYNTHETIC["filings"]["recent"]
CIK = "0000000999"


def rows():
    return filings.merge_rows(filings.parse_rows(RECENT, CIK))


def source(mode, when=None):
    return SourceInfo(mode=mode, label="x", retrieved_at=when, snapshot_date=date(2026, 11, 3),
                      source_urls=[])


def test_only_the_four_forms_newest_first_with_amendment_flags() -> None:
    found = rows()
    assert [r.form for r in found] == ["10-Q/A", "10-K/A", "10-K", "10-Q", "10-Q", "10-K"]
    assert [r.is_amendment for r in found] == [True, True, False, False, False, False]
    assert found[0].filing_date == date(2026, 4, 20)


def test_e1_amendment_never_replaces_the_original_as_latest() -> None:
    latest = filings.select_latest(rows(), "label")
    assert latest.annual.form == "10-K"
    assert latest.annual.accession == "0000000999-26-000002"
    assert latest.annual_amended_by is None  # the 10-K/A here is for an earlier report date


def test_e1_amended_by_needs_the_same_report_date() -> None:
    original = next(r for r in rows() if r.accession == "0000000999-26-000001")
    assert original.form == "10-Q"
    assert filings.amended_by(original, rows()).accession == "0000000999-26-000005"
    latest = filings.select_latest(rows(), "label")
    assert latest.quarterly.accession == "0000000999-26-000001"
    assert latest.quarterly_amended_by.form == "10-Q/A"


def test_amended_by_a_later_10k_a_for_the_same_period() -> None:
    table = {
        "accessionNumber": ["0000000999-26-000009", "0000000999-26-000008"],
        "filingDate": ["2026-04-01", "2026-02-01"],
        "reportDate": ["2025-12-31", "2025-12-31"],
        "form": ["10-K/A", "10-K"],
        "primaryDocument": ["a.htm", "k.htm"],
    }
    found = filings.merge_rows(filings.parse_rows(table, CIK))
    latest = filings.select_latest(found, "label")
    assert latest.annual.form == "10-K"
    assert latest.annual_amended_by.accession == "0000000999-26-000009"
    assert filings.amends(found[0], found).accession == "0000000999-26-000008"
    assert filings.amends(found[1], found) is None


def test_only_an_amendment_means_no_latest_original() -> None:
    table = {"accessionNumber": ["0000000999-26-000009"], "filingDate": ["2026-04-01"],
             "reportDate": ["2025-12-31"], "form": ["10-K/A"], "primaryDocument": ["a.htm"]}
    latest = filings.select_latest(filings.parse_rows(table, CIK), "label")
    assert latest.annual is None


def test_row_without_primary_document_stays_listed_without_addresses() -> None:
    old = next(r for r in rows() if r.accession == "0000000999-14-000001")
    assert old.primary_document is None and old.document_url is None
    assert old.index_url.endswith("/999/000000099914000001/0000000999-14-000001-index.html")


@pytest.mark.parametrize("bad", ["../../x.htm", "a/b.htm", "..", "a b.htm", "a?b=1", ""])
def test_unsafe_primary_document_gets_no_address(bad) -> None:
    table = {"accessionNumber": ["0000000999-26-000009"], "filingDate": ["2026-04-01"],
             "reportDate": ["2025-12-31"], "form": ["10-K"], "primaryDocument": [bad]}
    assert filings.parse_rows(table, CIK)[0].document_url is None


def test_malformed_rows_are_skipped_and_never_repaired() -> None:
    table = {"accessionNumber": ["../../etc", "0000000999-26-000009"],
             "filingDate": ["2026-04-01", "not a date"],
             "reportDate": ["2025-12-31", "2025-12-31"], "form": ["10-K", "10-K"],
             "primaryDocument": ["a.htm", "a.htm"]}
    assert filings.parse_rows(table, CIK) == []


def test_ten_year_window() -> None:
    start = filings.window_start(date(2026, 11, 3), 10)
    assert start == date(2016, 11, 3)
    assert [r.accession for r in filings.in_window(rows(), start)][-1] == "0000000999-25-000009"
    assert filings.window_start(date(2024, 2, 29), 1) == date(2023, 2, 28)


def test_older_pages_only_when_the_recent_table_is_short() -> None:
    start = date(2016, 11, 3)
    files = [
        {"name": "p2.json", "filingFrom": "2000-01-01", "filingTo": "2012-01-01"},
        {"name": "p1.json", "filingFrom": "2012-01-02", "filingTo": "2020-01-01"},
    ]
    reaching = {"filingDate": ["2026-01-01", "2015-01-01"], "form": ["10-K", "8-K"]}
    short = {"filingDate": ["2026-01-01", "2021-01-01"], "form": ["10-K", "8-K"]}
    no_report = {"filingDate": ["2026-01-01", "2015-01-01"], "form": ["8-K", "8-K"]}
    assert filings.older_pages_needed(reaching, files, start) == []
    assert filings.older_pages_needed(short, files, start) == ["p1.json"]
    assert filings.older_pages_needed(no_report, files, start) == ["p1.json"]
    assert filings.older_pages_needed(short, "not a list", start) == []


def test_e4_latest_label_always_names_its_source() -> None:
    when = datetime(2026, 11, 4, 9, 30, tzinfo=timezone.utc)
    assert filings.latest_label(source("demo"), when) == "Latest in snapshot (as of 2026-11-04)"
    assert filings.latest_label(source("live", when), when) == (
        "Latest on EDGAR (retrieved 2026-11-04 09:30 UTC)"
    )
    assert filings.latest_label(source("cached", when), when) == (
        "Latest on EDGAR (cached, retrieved 2026-11-04)"
    )


def test_coverage_is_honest_about_limits() -> None:
    found = rows()
    demo = filings.coverage_of(found, filings.CoverageFacts(demo=True, pages_missing=False))
    assert demo.note == "History limited to the recorded snapshot" and demo.complete is False
    assert demo.to_date == date(2026, 4, 20)
    live = filings.coverage_of(found, filings.CoverageFacts(demo=False, pages_missing=False))
    assert live.note is None and live.complete is True
    missing = filings.coverage_of([], filings.CoverageFacts(demo=False, pages_missing=True))
    assert missing.complete is False and missing.from_date is None


def test_m3_ac6_archive_address_is_built_exactly() -> None:
    assert archive.document_url("0000320193", "0000320193-26-000026", "aapl-20260926.htm") == (
        "https://www.sec.gov/Archives/edgar/data/320193/000032019326000026/aapl-20260926.htm"
    )
    assert archive.index_url("320193", "0000320193-26-000026") == (
        "https://www.sec.gov/Archives/edgar/data/320193/000032019326000026/"
        "0000320193-26-000026-index.html"
    )


@pytest.mark.parametrize(
    "accession",
    ["../../etc", "0000320193-25-00007", "0000320193-26-0000261", "0000320193-26-000026\n", ""],
)
def test_e5_bad_accessions_are_rejected(accession) -> None:
    assert not archive.is_valid_accession(accession)
    with pytest.raises(archive.InvalidArchivePart):
        archive.document_url("320193", accession, "a.htm")


@pytest.mark.parametrize("name", ["a/b.htm", "..", ".", "../a.htm", "a\\b", "a b", "x" * 201])
def test_e5_bad_document_names_are_rejected(name) -> None:
    with pytest.raises(archive.InvalidArchivePart):
        archive.document_url("320193", "0000320193-26-000026", name)


def test_e1_pairing_never_crosses_forms() -> None:
    # Test review 2026-11-09: the 10-K/A for 2025-09-30 must not pair with the 10-Q of that date.
    ten_k_a = next(r for r in rows() if r.accession == "0000000999-26-000003")
    assert ten_k_a.form == "10-K/A"
    assert filings.amends(ten_k_a, rows()) is None
    table = {
        "accessionNumber": ["0000000999-26-000009", "0000000999-26-000008"],
        "filingDate": ["2026-04-01", "2026-02-01"],
        "reportDate": ["2025-12-31", "2025-12-31"],
        "form": ["10-K/A", "10-Q"],
        "primaryDocument": ["a.htm", "q.htm"],
    }
    found = filings.merge_rows(filings.parse_rows(table, CIK))
    ten_q = next(r for r in found if r.form == "10-Q")
    assert filings.amended_by(ten_q, found) is None
    assert filings.select_latest(found, "label").quarterly_amended_by is None


def test_window_includes_its_first_day_and_excludes_the_day_before() -> None:
    table = {
        "accessionNumber": ["0000000999-16-000002", "0000000999-16-000001"],
        "filingDate": ["2016-11-03", "2016-11-02"],
        "reportDate": ["2016-09-30", "2016-09-30"],
        "form": ["10-Q", "10-Q"],
        "primaryDocument": ["b.htm", "a.htm"],
    }
    found = filings.parse_rows(table, CIK)
    start = filings.window_start(date(2026, 11, 3), 10)
    assert [r.accession for r in filings.in_window(found, start)] == ["0000000999-16-000002"]
    assert filings.window_start(date(2026, 11, 3), 3) == date(2023, 11, 3)
