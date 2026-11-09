"""Filing HTML becomes plain text blocks and nothing active survives (M3-E2). Offline."""

import time
from pathlib import Path

from app.logic.sanitize import MAX_BLOCKS, html_to_blocks, plain_text_to_blocks, to_blocks

DOCS = Path(__file__).parent / "synthetic" / "filings"
HOSTILE = html_to_blocks((DOCS / "hostile.html").read_bytes()).blocks
ALL_TEXT = "\n".join(block.text for block in HOSTILE)


def test_e2_no_markup_or_active_content_survives() -> None:
    for banned in ("<script", "onclick", "<iframe", "javascript:", "<style", "<form", "onerror",
                   "onload", "attacker.invalid", "alert("):
        assert banned not in ALL_TEXT


def test_e2_hidden_and_non_visible_text_is_removed() -> None:
    for hidden in ("HIDDEN-XBRL-FACT", "HIDDEN-XBRL-REFERENCE", "SCRIPT-TEXT", "NOSCRIPT-TEXT",
                   "TEMPLATE-TEXT", "IFRAME-TEXT", "OBJECT-TEXT", "SVG-TEXT", "INPUT-VALUE",
                   "BUTTON-TEXT", "TEXTAREA-TEXT", "INLINE-HIDDEN-TEXT", "HIDDEN-ATTRIBUTE-TEXT",
                   "COMMENT-TEXT", "head title text"):
        assert hidden not in ALL_TEXT


def test_visible_text_is_kept_with_whitespace_normalised() -> None:
    texts = [block.text for block in HOSTILE]
    assert "Visible heading" in texts
    assert "Visible paragraph with bold and a link." in texts
    assert "First item" in texts and "Second item" in texts
    assert "Last visible paragraph." in texts


def test_escaped_markup_stays_as_words_for_the_browser_to_show_as_text() -> None:
    assert "Escaped markup stays as words: <img src=x>." in [block.text for block in HOSTILE]


def test_invisible_and_direction_control_characters_are_removed() -> None:
    assert "Text with a zerowidth space and a bidi override." in [b.text for b in HOSTILE]


def test_heading_kind_comes_from_the_tag() -> None:
    assert next(b for b in HOSTILE if b.text == "Visible heading").kind == "heading"


def test_tables_become_rows_with_empty_cells_dropped_and_money_joined() -> None:
    rows = [block for block in HOSTILE if block.kind == "table_row"]
    assert [row.text for row in rows] == ["Revenue | $1,234 | (56) | 7.5%"]


def test_page_number_only_blocks_are_dropped() -> None:
    texts = [block.text for block in HOSTILE]
    assert "12" not in texts and "F-12" not in texts


def test_layout_table_with_long_cells_is_read_as_paragraphs() -> None:
    long = "Long sentence of body text. " * 40
    raw = f"<table><tr><td><p>{long}</p><p>Second paragraph.</p></td></tr></table>".encode()
    blocks = html_to_blocks(raw).blocks
    assert [b.kind for b in blocks] == ["text", "text"]
    assert blocks[1].text == "Second paragraph."


def test_nested_table_rows_are_not_repeated() -> None:
    raw = b"<table><tr><td>A</td><td><table><tr><td>B</td></tr></table></td></tr></table>"
    assert [b.text for b in html_to_blocks(raw).blocks] == ["A", "B"]


def test_table_with_an_unusual_structure_keeps_its_text() -> None:
    raw = b"<table>loose<tr><td>A</td></tr><font><tr><td>B</td></tr></font></table>"
    assert " ".join(b.text for b in html_to_blocks(raw).blocks) == "loose A B"


def test_very_deep_nesting_does_not_crash_or_stall() -> None:
    raw = (b"<div>" * 50_000) + b"deep text" + (b"</div>" * 50_000)
    started = time.monotonic()
    assert [b.text for b in html_to_blocks(raw).blocks] == ["deep text"]
    assert time.monotonic() - started < 10  # a quadratic walk takes minutes at this depth


def test_block_limit_cuts_and_says_so() -> None:
    raw = b"".join(b"<p>word</p>" for _ in range(MAX_BLOCKS + 5))
    result = html_to_blocks(raw)
    assert len(result.blocks) == MAX_BLOCKS and result.truncated is True
    assert html_to_blocks(b"<p>word</p>").truncated is False


def test_non_utf8_bytes_are_read() -> None:
    assert html_to_blocks("<p>Café résumé</p>".encode("cp1252")).blocks[0].text == (
        "Café résumé"
    )


def test_plain_text_filing_splits_on_blank_lines() -> None:
    blocks = plain_text_to_blocks(b"First   paragraph\nsame one\n\n\n<b>Second</b>\n\n 7 \n").blocks
    assert [b.text for b in blocks] == ["First paragraph same one", "<b>Second</b>"]


def test_format_chosen_by_name_and_html_sniffing() -> None:
    assert to_blocks(b"<html><p>a b</p></html>", "x.txt").blocks[0].text == "a b"
    assert to_blocks(b"<p>a b</p>", "x.htm").blocks[0].text == "a b"
    assert to_blocks(b"a <p> b", "x.txt").blocks[0].text == "a <p> b"


def test_deeply_nested_tables_do_not_stall() -> None:
    # Security review 2026-11-09: each table re-read everything below it (time grew with depth²).
    depth = 20_000
    raw = (b"<table><tr><td>" * depth) + b"inner text" + (b"</td></tr></table>" * depth)
    started = time.monotonic()
    assert [b.text for b in html_to_blocks(raw).blocks] == ["inner text"]
    assert time.monotonic() - started < 5


def test_nested_tables_without_closing_tags_do_not_stall() -> None:
    raw = (b"<table><tr><td>" * 20_000) + b"inner text"
    started = time.monotonic()
    assert [b.text for b in html_to_blocks(raw).blocks] == ["inner text"]
    assert time.monotonic() - started < 5
