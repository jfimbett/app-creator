"""CSV export of a comparison (M4, Q33). Pure function: the same result the table shows.

- One line per comparison row, in the result's row order, under a fixed header.
- `value` is the full-precision number in whole currency units, index points or a decimal ratio
  (never the scaled display value), and an empty cell when there is no value. Never 0 for missing.
- Formula-injection guard: a text cell that starts with `=`, `+`, `-`, `@`, tab, carriage return
  or line feed (also after leading whitespace, or as a fullwidth sign) gets a leading `'`, so a
  spreadsheet shows it as text instead of running it. Numbers are not text cells, so a negative
  value stays a number.
- Python's `csv` module does the quoting (RFC 4180), with `\\r\\n` line ends.
"""

from __future__ import annotations

import csv
import io
import math
import unicodedata
from decimal import Decimal

from app.logic.compare import CompareResult

HEADER = (
    "company", "ticker", "cik", "fiscal_year_label", "fiscal_year_end", "period_start",
    "period_end", "metric", "value", "unit", "kind", "indexed", "source_concept", "accession",
    "data_source",
)
_FORMULA_STARTS = ("=", "+", "-", "@", "\t", "\r", "\n")


def _looks_like_formula(text: str) -> bool:
    """True when a spreadsheet could run the cell: a formula sign first, also after leading
    whitespace (some spreadsheets trim it) or written as a fullwidth sign (some fold "＝" to "=").
    Security review 2026-11-09."""
    if text.startswith(_FORMULA_STARTS):
        return True
    trimmed = text.lstrip()
    return bool(trimmed) and unicodedata.normalize("NFKC", trimmed[0]).startswith(_FORMULA_STARTS)


def _text(value: object) -> str:
    text = "" if value is None else str(value)
    return "'" + text if _looks_like_formula(text) else text


def _number(value: float | None) -> str:
    """The shortest exact decimal, never scientific notation ("0.00001", not "1e-05"); an empty
    cell for anything that is not a finite number (test review 2026-11-09)."""
    if value is None or not math.isfinite(value):
        return ""
    if float(value).is_integer():
        return str(int(value))
    return format(Decimal(repr(float(value))), "f")


def to_csv(result: CompareResult) -> str:
    """The comparison as CSV text: the header, then one line per row."""
    companies = {c.cik: c for c in result.companies}
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer, lineterminator="\r\n")
    writer.writerow(HEADER)
    for row in result.rows:
        company = companies[row.cik]
        writer.writerow([
            _text(company.name),
            _text(company.ticker),
            _text(row.cik),
            _text(row.fiscal_year_label),
            _text(row.period_end.isoformat()),
            _text(row.period_start.isoformat() if row.period_start else None),
            _text(row.period_end.isoformat()),
            _text(row.metric_id),
            _number(row.value),
            _text(row.unit),
            _text(row.kind),
            "true" if row.indexed else "false",
            _text(row.source_concept),
            _text(row.accession),
            _text(row.data_source),
        ])
    return buffer.getvalue()
