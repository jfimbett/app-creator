"""Bounded, deterministic retrieval of facts and passages (M5-AC5). Offline: recorded SEC data."""

import gzip
from datetime import date
from pathlib import Path

from app.data.fixtures import FixtureStore
from app.logic import retrieval
from app.logic.sanitize import Block, to_blocks
from app.logic.sections import detect_sections
from app.logic.statements import build_financials
from app.settings import Settings

FIXTURES = Path(__file__).resolve().parents[2] / "fixtures"
APPLE = "0000320193"
APPLE_10K = "0000320193-26-000026"


def apple_facts_source() -> retrieval.FactSource:
    store = FixtureStore(Settings(data_mode="fixtures").fixtures_dir)
    financials = build_financials(store.companyfacts(APPLE), "https://data.sec.gov/x")
    return retrieval.FactSource(cik=APPLE, ticker="AAPL", series=financials.series)


def apple_document() -> retrieval.DocumentInput:
    raw = gzip.decompress(
        (FIXTURES / "filings" / APPLE / APPLE_10K / "aapl-20260926.htm.gz").read_bytes()
    )
    document = to_blocks(raw, "aapl-20260926.htm")
    sections = detect_sections(document.blocks, "10-K")
    return retrieval.DocumentInput(
        cik=APPLE,
        ticker="AAPL",
        form="10-K",
        accession=APPLE_10K,
        filing_date=date(2026, 11, 3),
        blocks=document.blocks,
        section_of_block=sections.section_of_block,
        section_labels={s.id: s.item for s in sections.sections},
    )


def test_m5_ac5_limits_hold_on_a_large_real_scope() -> None:
    context = retrieval.build_context(
        [apple_facts_source()], None, apple_document(), "Why did net margin change?"
    )
    assert 0 < len(context.facts) <= 60
    assert 0 < len(context.passages) <= 8
    assert context.chars <= 24_000
    assert context.chars == sum(len(f.line()) for f in context.facts) + sum(
        len(p.line()) for p in context.passages
    )
    assert [f.source_id for f in context.facts] == [
        f"F{n}" for n in range(1, len(context.facts) + 1)
    ]
    assert [p.source_id for p in context.passages] == [
        f"P{n}" for n in range(1, len(context.passages) + 1)
    ]
    assert all(len(p.text) <= 3_000 for p in context.passages)


def test_facts_are_the_apps_own_values_in_priority_then_newest_order() -> None:
    source = apple_facts_source()
    facts = retrieval.build_context([source], None, None, "anything").facts
    assert [f.metric_id for f in facts[:3]] == ["revenue", "revenue", "revenue"]
    assert facts[0].fiscal_year_label == "FY2026" and facts[1].fiscal_year_label == "FY2025"
    by_key = {(v.metric_id, v.fiscal_year_label): v for vs in source.series.values() for v in vs}
    for fact in facts:
        computed = by_key[(fact.metric_id, fact.fiscal_year_label)]
        assert computed.status == "ok"
        assert fact.value == computed.value
    revenue = facts[0]
    assert revenue.value == 478834000000  # FX1 in milestones/acceptance.md
    assert revenue.value_text == "478,834,000,000 USD"
    assert revenue.basis == "RevenueFromContractWithCustomerExcludingAssessedTax"
    assert (revenue.form, revenue.accession) == ("10-K", APPLE_10K)
    margin = next(f for f in facts if f.metric_id == "net_margin")
    assert margin.value_text == "27.60%"  # FX5 0.276035
    assert margin.basis == "net income ÷ revenue" and margin.accession == APPLE_10K


def test_same_input_gives_the_same_context() -> None:
    first = retrieval.build_context(
        [apple_facts_source()], None, apple_document(), "supply chain risk"
    )
    second = retrieval.build_context(
        [apple_facts_source()], None, apple_document(), "supply chain risk"
    )
    assert first == second


def test_passages_are_ranked_by_question_terms() -> None:
    context = retrieval.build_context([], None, apple_document(), "iPhone supply chain risks")
    top = context.passages[0].text.lower()
    assert "supply" in top or "iphone" in top


def test_facts_come_from_the_latest_five_fiscal_years() -> None:
    facts = retrieval.build_context([apple_facts_source()], None, None, "x").facts
    assert {f.fiscal_year_label for f in facts} == {f"FY{y}" for y in range(2022, 2027)}
    assert len({f.metric_id for f in facts}) >= 10


def test_comparison_facts_cover_only_the_selected_metrics() -> None:
    source = apple_facts_source()
    facts = retrieval.build_context([source], ["revenue", "net_margin"], None, "x").facts
    assert {f.metric_id for f in facts} == {"revenue", "net_margin"}


def test_passage_budget_counts_the_facts_too() -> None:
    blocks = [
        Block("text", f"Block {n} about supply and revenue. " + "word " * 500) for n in range(40)
    ]
    document = retrieval.DocumentInput(
        cik=APPLE,
        ticker="AAPL",
        form="10-K",
        accession=APPLE_10K,
        filing_date=date(2026, 11, 3),
        blocks=blocks,
        section_of_block=[None] * 40,
        section_labels={},
    )
    context = retrieval.build_context([apple_facts_source()], None, document, "supply revenue")
    assert len(context.passages) <= 8
    assert context.chars <= 24_000
    assert all(p.section == "no section detected" for p in context.passages)
