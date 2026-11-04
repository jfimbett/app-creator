"""A company's 10-K and 10-Q list from SEC submissions data (brief §3, §7; M3-AC1, AC2, E1, E4).

Pure functions: no network, no files. The rules:
- Only the forms 10-K, 10-K/A, 10-Q and 10-Q/A. A row with a malformed accession or date is
  skipped, never repaired. A row with no usable primary document stays listed, without addresses.
- "Latest" is the most recent ORIGINAL report by filing date. A later amendment never replaces it:
  it is reported separately as "amended by".
- An amendment belongs to an original when both have the same base form and the same report date.
- The wording of "latest" always says where it comes from. "Latest" alone is never produced.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Any

from app.logic.archive import (
    document_url,
    index_url,
    is_valid_accession,
    is_valid_primary_document,
)
from app.models.common import SourceInfo
from app.models.filings import Coverage, FilingMeta, LatestFilings

ANNUAL_FORM = "10-K"
QUARTERLY_FORM = "10-Q"
ALL_FORMS = ("10-K", "10-K/A", "10-Q", "10-Q/A")
MAX_YEARS = 10
SNAPSHOT_NOTE = "History limited to the recorded snapshot"
INCOMPLETE_NOTE = "SEC's older filing pages were not read, so earlier filings may be missing"


def _parse_date(value: Any) -> date | None:
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        return None


def _column(columns: dict[str, Any], name: str, length: int) -> list[Any]:
    column = columns.get(name)
    return column if isinstance(column, list) and len(column) == length else [None] * length


def parse_rows(columns: dict[str, Any], cik: str) -> list[FilingMeta]:
    """The 10-K/10-Q rows of one SEC filings table, in the order SEC lists them."""
    forms = columns.get("form") if isinstance(columns, dict) else None
    if not isinstance(forms, list):
        return []
    length = len(forms)
    accessions = _column(columns, "accessionNumber", length)
    filing_dates = _column(columns, "filingDate", length)
    report_dates = _column(columns, "reportDate", length)
    documents = _column(columns, "primaryDocument", length)
    rows = []
    for form, accession, filed, report, document in zip(
        forms, accessions, filing_dates, report_dates, documents, strict=True
    ):
        filing_date = _parse_date(filed)
        if form not in ALL_FORMS or not is_valid_accession(accession) or filing_date is None:
            continue
        usable = is_valid_primary_document(document)
        rows.append(
            FilingMeta(
                accession=accession,
                form=form,
                is_amendment=form.endswith("/A"),
                filing_date=filing_date,
                report_date=_parse_date(report),
                primary_document=document if usable else None,
                document_url=document_url(cik, accession, document) if usable else None,
                index_url=index_url(cik, accession),
            )
        )
    return rows


def merge_rows(*tables: list[FilingMeta]) -> list[FilingMeta]:
    """All rows, each accession once, newest first (on the same day, higher accession first)."""
    unique: dict[str, FilingMeta] = {}
    for table in tables:
        for row in table:
            unique.setdefault(row.accession, row)
    return sorted(unique.values(), key=lambda r: (r.filing_date, r.accession), reverse=True)


def window_start(reference: date, years: int) -> date:
    """The first day of a window of `years` years that ends on `reference`."""
    try:
        return reference.replace(year=reference.year - years)
    except ValueError:  # 29 February
        return reference.replace(year=reference.year - years, day=28)


def older_pages_needed(
    recent: dict[str, Any], files: Any, start: date
) -> list[str]:
    """Names of SEC's older submissions pages to read, newest first.

    Pages are needed only when the recent table does not reach back to `start`, or holds no 10-K or
    10-Q at all. A page entirely older than `start` is never needed, except that a company whose
    recent table holds no report may have its reports only there.
    """
    if not isinstance(files, list):
        return []
    dates = [d for d in (_parse_date(v) for v in (recent or {}).get("filingDate") or []) if d]
    forms = (recent or {}).get("form") or []
    reaches_back = bool(dates) and min(dates) <= start
    has_report = any(form in ALL_FORMS for form in forms)
    if reaches_back and has_report:
        return []
    pages = []
    for entry in files:
        if not isinstance(entry, dict) or not isinstance(entry.get("name"), str):
            continue
        filing_to = _parse_date(entry.get("filingTo"))
        if filing_to is None or filing_to >= start:
            pages.append((filing_to or date.max, entry["name"]))
    return [name for _, name in sorted(pages, reverse=True)]


def in_window(rows: list[FilingMeta], start: date) -> list[FilingMeta]:
    """The rows filed on or after `start`."""
    return [row for row in rows if row.filing_date >= start]


def amended_by(original: FilingMeta | None, rows: list[FilingMeta]) -> FilingMeta | None:
    """The most recent amendment of the same report, if there is one."""
    if original is None or original.report_date is None or original.is_amendment:
        return None
    wanted = f"{original.form}/A"
    matches = [
        row for row in rows
        if row.form == wanted
        and row.report_date == original.report_date
        and row.filing_date >= original.filing_date
    ]
    return max(matches, key=lambda r: (r.filing_date, r.accession), default=None)


def amends(amendment: FilingMeta, rows: list[FilingMeta]) -> FilingMeta | None:
    """The original report an amendment changes, when the list shows it."""
    if not amendment.is_amendment or amendment.report_date is None:
        return None
    base = amendment.form.removesuffix("/A")
    matches = [r for r in rows if r.form == base and r.report_date == amendment.report_date]
    return max(matches, key=lambda r: (r.filing_date, r.accession), default=None)


def _latest_original(rows: list[FilingMeta], form: str) -> FilingMeta | None:
    return max(
        (row for row in rows if row.form == form),
        key=lambda r: (r.filing_date, r.accession),
        default=None,
    )


def latest_label(source: SourceInfo, listed_at: datetime | date | None) -> str:
    """The heading of the latest panel. It always says where "latest" comes from."""
    if source.mode == "demo":
        day = listed_at.date() if isinstance(listed_at, datetime) else listed_at
        return f"Latest in snapshot (as of {(day or source.snapshot_date).isoformat()})"
    if source.mode == "cached":
        return f"Latest on EDGAR (cached, retrieved {source.retrieved_at:%Y-%m-%d})"
    return f"Latest on EDGAR (retrieved {source.retrieved_at:%Y-%m-%d %H:%M} UTC)"


def select_latest(rows: list[FilingMeta], label: str) -> LatestFilings:
    """The latest original 10-K and 10-Q, each with the amendment of it, if any."""
    annual = _latest_original(rows, ANNUAL_FORM)
    quarterly = _latest_original(rows, QUARTERLY_FORM)
    return LatestFilings(
        annual=annual,
        quarterly=quarterly,
        annual_amended_by=amended_by(annual, rows),
        quarterly_amended_by=amended_by(quarterly, rows),
        label=label,
    )


@dataclass(frozen=True)
class CoverageFacts:
    """What the data layer knows about how far back it read."""

    demo: bool
    pages_missing: bool


def coverage_of(shown: list[FilingMeta], facts: CoverageFacts) -> Coverage:
    """The range shown, and an honest note when it may not be the whole window."""
    note = SNAPSHOT_NOTE if facts.demo else (INCOMPLETE_NOTE if facts.pages_missing else None)
    return Coverage(
        from_date=min((row.filing_date for row in shown), default=None),
        to_date=max((row.filing_date for row in shown), default=None),
        complete=not (facts.demo or facts.pages_missing),
        note=note,
    )
