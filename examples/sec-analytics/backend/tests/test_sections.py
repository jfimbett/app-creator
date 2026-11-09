"""Item heading detection and its fallback (M3-AC4, AC7, E3). Offline.

The recorded-document tests read authentic filings. All other inputs are synthetic.
"""

import gzip
from pathlib import Path

import pytest

from app.logic.sanitize import Block, html_to_blocks
from app.logic.sections import DETECTED_NOTE, NOT_DETECTED_NOTE, detect_sections

DOCS = Path(__file__).parent / "synthetic" / "filings"
FIXTURES = Path(__file__).resolve().parents[2] / "fixtures" / "filings"


def synthetic(name):
    return html_to_blocks((DOCS / name).read_bytes()).blocks


def recorded(path):
    return html_to_blocks(gzip.decompress((FIXTURES / path).read_bytes())).blocks


def test_e3_section_starts_at_the_body_heading_not_the_contents_entry() -> None:
    blocks = synthetic("toc_and_body.html")
    found = detect_sections(blocks, "10-K")
    assert found.status == "detected" and found.note == DETECTED_NOTE
    by_id = {section.id: section for section in found.sections}
    assert list(by_id) == ["item1", "item1a", "item1b", "item7", "item8"]
    first_contents_entry = next(i for i, b in enumerate(blocks) if b.text.startswith("Item 7"))
    assert by_id["item7"].block_start > first_contents_entry
    assert blocks[by_id["item7"].block_start + 1].text.startswith("BODY-SEVEN")
    assert blocks[by_id["item1"].block_start + 1].text.startswith("BODY-ONE")
    assert by_id["item7"].title == "Management's Discussion and Analysis"
    assert by_id["item7"].item == "Item 7"


def test_blocks_are_assigned_to_their_sections_and_headings_marked() -> None:
    blocks = synthetic("toc_and_body.html")
    found = detect_sections(blocks, "10-K")
    start = next(s.block_start for s in found.sections if s.id == "item7")
    assert found.section_of_block[start] == "item7"
    assert found.section_of_block[start + 1] == "item7"
    assert found.section_of_block[0] is None
    assert start in found.heading_blocks


def test_a_sentence_that_starts_with_item_is_not_a_heading() -> None:
    blocks = synthetic("toc_and_body.html")
    found = detect_sections(blocks, "10-K")
    start = next(s.block_start for s in found.sections if s.id == "item1b")
    assert blocks[start].text.startswith("Item 1B.")


def test_ten_q_uses_part_ids_and_skips_contents_table_rows() -> None:
    found = detect_sections(synthetic("ten_q.html"), "10-Q")
    assert [s.id for s in found.sections] == [
        "part1-item1", "part1-item2", "part2-item1", "part2-item1a",
    ]
    assert found.sections[2].item == "Part II, Item 1"
    assert found.sections[2].title == "Legal Proceedings"


def test_ten_q_without_a_part_two_heading_still_reaches_part_two() -> None:
    blocks = [Block("text", t) for t in (
        "Item 1. Financial Statements", "x " * 200, "Item 2. Discussion", "x " * 200,
        "Item 1. Legal Proceedings", "x " * 200, "Item 1A. Risk Factors", "x " * 200,
    )]
    assert [s.id for s in detect_sections(blocks, "10-Q").sections] == [
        "part1-item1", "part1-item2", "part2-item1", "part2-item1a",
    ]


def test_ac7_no_item_headings_means_the_labelled_fallback() -> None:
    found = detect_sections(synthetic("no_items.html"), "10-K")
    assert found.status == "not_detected"
    assert found.note == "Section boundaries not detected; showing full text"
    assert found.note == NOT_DETECTED_NOTE
    assert found.sections == []
    assert set(found.section_of_block) == {None}


def test_fewer_than_three_headings_is_not_a_best_guess() -> None:
    blocks = [Block("text", "Item 1. Business"), Block("text", "x " * 300),
              Block("text", "Item 7. Discussion"), Block("text", "x " * 300)]
    assert detect_sections(blocks, "10-K").status == "not_detected"


def test_short_real_sections_after_the_contents_are_kept() -> None:
    long = Block("text", "x " * 300)
    blocks = [
        Block("text", "Item 1. Business"), long,
        Block("text", "Item 1B. Unresolved Staff Comments"), Block("text", "None."),
        Block("text", "Item 2. Properties"), Block("text", "None."),
        Block("text", "Item 3. Legal Proceedings"), Block("text", "None."),
        Block("text", "Item 4. Mine Safety Disclosures"), Block("text", "None."),
        Block("text", "Item 7. Discussion"), long,
    ]
    assert [s.id for s in detect_sections(blocks, "10-K").sections] == [
        "item1", "item1b", "item2", "item3", "item4", "item7",
    ]


def test_unknown_item_numbers_are_ignored() -> None:
    long = Block("text", "x " * 300)
    blocks = [Block("text", "Item 1. Business"), long, Block("text", "Item 405. Rules"), long,
              Block("text", "Item 7. Discussion"), long, Block("text", "Item 8. Statements"), long]
    assert [s.id for s in detect_sections(blocks, "10-K").sections] == ["item1", "item7", "item8"]


def test_title_on_the_next_block_is_used_when_the_heading_has_none() -> None:
    long = Block("text", "x " * 300)
    blocks = [Block("text", "Item 1."), Block("text", "Business"), long,
              Block("text", "Item 7."), Block("text", "Discussion"), long,
              Block("text", "Item 8."), Block("text", "Statements"), long]
    assert [s.title for s in detect_sections(blocks, "10-K").sections] == [
        "Business", "Discussion", "Statements",
    ]


@pytest.mark.parametrize(
    "path",
    [
        "0000320193/0000320193-26-000026/aapl-20260926.htm.gz",
        "0000789019/0001193125-26-323660/msft-20260630.htm.gz",
        "0001652044/0001652044-26-000018/goog-20251231.htm.gz",
    ],
    ids=["apple", "microsoft", "alphabet"],
)
def test_recorded_10k_detects_the_main_items_in_order_past_the_contents(path) -> None:
    blocks = recorded(path)
    found = detect_sections(blocks, "10-K")
    assert found.status == "detected"
    ids = [section.id for section in found.sections]
    for needed in ("item1", "item1a", "item7", "item8"):
        assert needed in ids
    starts = [section.block_start for section in found.sections]
    assert starts == sorted(starts)
    by_id = {section.id: section for section in found.sections}
    # A real Item 7 has a long body before the next heading; a contents entry does not.
    item7_next = starts[ids.index("item7") + 1]
    body = sum(len(b.text) for b in blocks[by_id["item7"].block_start + 1 : item7_next])
    assert body > 5_000


@pytest.mark.parametrize(
    "path",
    [
        "0000320193/0000320193-26-000020/aapl-20260627.htm.gz",
        "0000789019/0001193125-26-436133/msft-20260930.htm.gz",
        "0001652044/0001652044-26-000084/goog-20260930.htm.gz",
    ],
    ids=["apple", "microsoft", "alphabet"],
)
def test_recorded_10q_detects_part_one_and_part_two(path) -> None:
    found = detect_sections(recorded(path), "10-Q")
    ids = [section.id for section in found.sections]
    assert found.status == "detected"
    assert "part1-item1" in ids and "part1-item2" in ids and "part2-item1" in ids


def test_running_page_headers_are_not_sections() -> None:
    long = Block("text", "x " * 300)
    blocks = [
        Block("text", "Item 1"), Block("text", "ITEM 1. BUSINESS"), long,
        Block("text", "Item 1"), long, Block("text", "Item 1"), long,
        Block("text", "Item 3, 4"), Block("text", "ITEM 3. LEGAL"), long,
        Block("text", "ITEM 7. DISCUSSION"), long,
    ]
    found = detect_sections(blocks, "10-K").sections
    assert [(s.id, s.title) for s in found] == [
        ("item1", "BUSINESS"), ("item3", "LEGAL"), ("item7", "DISCUSSION"),
    ]


def test_recorded_microsoft_10q_keeps_part_order_despite_its_running_headers() -> None:
    # Authentic document: each page starts with "PART I" / "Item 1". Expected list: the filing's
    # own INDEX (Part I items 1-4; Part II items 1, 1A, 2, 5, 6), read from the raw HTML
    # on 2026-11-09 with a tag-stripping regex, not with app code.
    path = "0000789019/0001193125-26-436133/msft-20260930.htm.gz"
    found = detect_sections(recorded(path), "10-Q").sections
    assert [s.id for s in found] == [
        "part1-item1", "part1-item2", "part1-item3", "part1-item4", "part2-item1", "part2-item1a",
        "part2-item2", "part2-item5", "part2-item6",
    ]
    assert found[0].title == "FINANCIAL STATEMENTS"


def test_recorded_microsoft_10k_titles_are_real_titles() -> None:
    found = detect_sections(
        recorded("0000789019/0001193125-26-323660/msft-20260630.htm.gz"), "10-K"
    ).sections
    assert all(s.title and not s.title.upper().startswith("ITEM") for s in found)
    assert next(s for s in found if s.id == "item7").title.upper().startswith("MANAGEMENT")
