"""Citation validation (M5-E2): only ids supplied in this request become source chips. Offline."""

from datetime import date

from app.logic.citations import NO_VALID_SOURCES, NOT_SUPPLIED, validate
from app.logic.retrieval import Fact, Passage


def fact(n: int) -> Fact:
    return Fact(
        source_id=f"F{n}",
        cik="0000320193",
        ticker="AAPL",
        metric_id="net_margin",
        label="Net margin",
        value_text="27.60%",
        fiscal_year_label="FY2026",
        period_start=date(2025, 9, 28),
        period_end=date(2026, 9, 26),
        basis="NetIncomeLoss",
        form="10-K",
        accession="0000320193-26-000026",
        filed=date(2026, 11, 3),
    )


def passage(n: int) -> Passage:
    return Passage(
        source_id=f"P{n}",
        cik="0000320193",
        ticker="AAPL",
        form="10-K",
        accession="0000320193-26-000026",
        filing_date=date(2026, 11, 3),
        section="Item 7",
        block_start=100 + n,
        block_end=104 + n,
        text="text",
    )


FACTS = [fact(n) for n in range(1, 11)]
PASSAGES = [passage(n) for n in range(1, 4)]


def test_m5_e2_only_supplied_ids_become_chips() -> None:
    result = validate("Margin rose [F2]. Old data [F99]. See [P7] and again [F2].", FACTS, PASSAGES)
    assert [c.source_id for c in result.citations] == ["F2"]
    chip = result.citations[0]
    assert chip.valid and chip.kind == "fact"
    assert chip.label == "NetIncomeLoss · FY2026 · 10-K 0000320193-26-000026"
    assert chip.period == "2025-09-28 – 2026-09-26"
    assert chip.date == date(2026, 11, 3)
    assert chip.link == "/companies/0000320193"
    assert result.invalid_references == ["F99", "P7"]
    assert NOT_SUPPLIED == "Reference not in the supplied sources"
    assert result.note is None


def test_passage_chips_link_to_the_reader_block() -> None:
    result = validate("Supply risk [P1].", FACTS, PASSAGES)
    chip = result.citations[0]
    assert chip.kind == "passage"
    assert chip.label == "10-K 0000320193-26-000026 · Item 7"
    assert chip.period == "blocks 101–105"
    assert chip.link == "/companies/0000320193/filings/0000320193-26-000026#block-101"


def test_no_citation_at_all() -> None:
    result = validate("Net margin went up.", FACTS, PASSAGES)
    assert result.citations == [] and result.invalid_references == []
    assert result.note == NO_VALID_SOURCES == "No valid sources cited"


def test_only_invalid_citations_also_say_no_valid_sources() -> None:
    result = validate("Something [F42].", FACTS, PASSAGES)
    assert result.invalid_references == ["F42"]
    assert result.note == NO_VALID_SOURCES


def test_similar_looking_text_is_not_a_citation() -> None:
    result = validate("Fiscal [FY2026] and [F 2] and [f2] and [F0002].", FACTS, PASSAGES)
    assert result.citations == [] and result.invalid_references == []
