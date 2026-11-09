"""CSV export of a comparison (M4, Q33). Pure function: the same result the table shows.

- One line per comparison row, in the result's row order, under a fixed header.
- `value` is the full-precision number in whole currency units, index points or a decimal ratio
  (never the scaled display value), and an empty cell when there is no value. Never 0 for missing.
- Formula-injection guard: a text cell that starts with `=`, `+`, `-`, `@`, tab or carriage return
  gets a leading `'`, so a spreadsheet shows it as text instead of running it. Numbers are not text
  cells, so a negative value stays a number.
- Python's `csv` module does the quoting (RFC 4180), with `\\r\\n` line ends.
"""

from __future__ import annotations

import csv
import io

from app.logic.compare import CompareResult

HEADER = (
    "company", "ticker", "cik", "fiscal_year_label", "fiscal_year_end", "period_start",
    "period_end", "metric", "value", "unit", "kind", "indexed", "source_concept", "accession",
    "data_source",
)
_FORMULA_STARTS = ("=", "+", "-", "@", "\t", "\r")


def _text(value: object) -> str:
    text = "" if value is None else str(value)
    return "'" + text if text.startswith(_FORMULA_STARTS) else text


def _number(value: float | None) -> str:
    if value is None:
        return ""
    return str(int(value)) if float(value).is_integer() else repr(float(value))


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
