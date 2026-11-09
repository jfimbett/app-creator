"""CSV export of a comparison (M4-AC6, M4-AC7, M4-E2). Offline, synthetic companies."""

import csv
import io

from app.logic import compare as cmp
from app.logic.csv_export import HEADER, to_csv
from tests.test_compare import company

EXPECTED_HEADER = (
    "company,ticker,cik,fiscal_year_label,fiscal_year_end,period_start,period_end,metric,value,"
    "unit,kind,indexed,source_concept,accession,data_source"
)


def parsed(text: str) -> list[list[str]]:
    return list(csv.reader(io.StringIO(text, newline="")))


def result(*tickers, metrics=("revenue", "net_margin"), index=False):
    return cmp.compare([company(t) for t in tickers], list(metrics), 10, index)


def test_m4_ac6_exact_header_and_one_line_per_row_in_order() -> None:
    shown = result("SMPL", "XMPL")
    text = to_csv(shown)
    assert text.split("\r\n")[0] == EXPECTED_HEADER
    assert ",".join(HEADER) == EXPECTED_HEADER
    lines = parsed(text)
    assert len(lines) == 1 + len(shown.rows)
    keys = [(line[2], line[7], line[3]) for line in lines[1:]]
    assert keys == [(r.cik, r.metric_id, r.fiscal_year_label) for r in shown.rows]
    assert text.endswith("\r\n")


def test_values_are_full_precision_in_whole_units_with_their_unit() -> None:
    lines = parsed(to_csv(result("XMPL", "SMPL")))
    first = dict(zip(HEADER, lines[1], strict=True))
    assert first["company"] == "Example Co"
    assert (first["value"], first["unit"], first["kind"]) == ("800", "USD", "reported")
    assert (first["fiscal_year_end"], first["period_start"], first["period_end"]) == (
        "2024-12-31", "2024-01-01", "2024-12-31",
    )
    assert (first["source_concept"], first["accession"]) == ("Revenues", "0000000901-24-000001")
    assert first["indexed"] == "false" and first["data_source"] == "SYNTHETIC TEST DATA"
    margin = next(dict(zip(HEADER, line, strict=True)) for line in lines[1:]
                  if line[7] == "net_margin")
    assert (margin["value"], margin["unit"]) == ("0.1", "ratio")


def test_indexed_rows_say_index_and_true() -> None:
    lines = parsed(to_csv(result("XMPL", "SMPL", metrics=("revenue",), index=True)))
    rows = [dict(zip(HEADER, line, strict=True)) for line in lines[1:]]
    assert [(r["value"], r["unit"], r["indexed"]) for r in rows[:2]] == [
        ("100", "index", "true"), ("125", "index", "true"),
    ]


def test_m4_ac7_missing_value_is_an_empty_cell_and_the_row_is_kept() -> None:
    shown = result("XMPL", "SMPL", metrics=("net_margin",))
    lines = parsed(to_csv(shown))
    assert len(lines) == 1 + len(shown.rows)
    missing = next(line for line in lines[1:] if line[2] == "0000000902" and line[3] == "FY2025")
    assert missing[HEADER.index("value")] == ""


def test_m4_e2_text_cells_that_look_like_formulas_are_prefixed() -> None:
    lines = parsed(to_csv(result("FRML", "XMPL")))
    first = lines[1]
    assert first[0] == "'=HYPERLINK(\"http://example.invalid\")"
    for raw in ("=1+1", "+1", "-1", "@SUM(A1)", "\tx", "\rx"):
        assert parsed(to_csv(_renamed(raw)))[1][0] == "'" + raw


def test_negative_numbers_are_not_prefixed() -> None:
    lines = parsed(to_csv(result("FRML", "XMPL", metrics=("net_margin",))))
    assert lines[1][HEADER.index("value")] == "-0.5"


def test_commas_and_quotes_are_quoted_and_round_trip() -> None:
    text = to_csv(_renamed('Comma, "Quoted" Inc'))
    assert '"Comma, ""Quoted"" Inc"' in text
    assert parsed(text)[1][0] == 'Comma, "Quoted" Inc'


def _renamed(name: str):
    first = company("XMPL")
    renamed = cmp.CompanyInput(
        cik=first.cik, ticker=first.ticker, name=name, currency=first.currency,
        series=first.series, data_source=first.data_source,
    )
    return cmp.compare([renamed, company("SMPL")], ["revenue"], 10, False)


def test_guard_sees_through_leading_space_line_feed_and_fullwidth_signs() -> None:
    # Security review 2026-11-09: spreadsheets may trim leading whitespace or fold fullwidth signs.
    for raw in (" =1+1", " =1", "\n=1", "＝1+1", "＋1", "－1", "＠1"):
        assert parsed(to_csv(_renamed(raw)))[1][0] == "'" + raw, repr(raw)
    assert parsed(to_csv(_renamed(" Plain Co")))[1][0] == " Plain Co"


def test_embedded_line_breaks_stay_inside_one_quoted_cell() -> None:
    name = 'Line\r\n=HYPERLINK("http://example.invalid")'
    lines = parsed(to_csv(_renamed(name)))
    assert lines[1][0] == name
    assert all(len(line) == len(HEADER) for line in lines)


def test_numbers_are_plain_decimals_and_non_finite_values_are_empty() -> None:
    from app.logic.csv_export import _number

    assert _number(1e-05) == "0.00001"
    assert _number(0.276035) == "0.276035"
    assert _number(478834000000.0) == "478834000000"
    assert _number(-2.5) == "-2.5"
    assert _number(float("nan")) == "" and _number(float("inf")) == ""
