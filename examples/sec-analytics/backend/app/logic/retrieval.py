"""What the AI analyst is shown (M5): a bounded, deterministic selection of facts and passages.

Pure functions: no network, files or clock. Same input → same context.

- **Facts** are the app's own computed values (`MetricValue`, reported or derived, with
  provenance), never numbers re-derived here, from each company's latest five fiscal years.
  Only values with status "ok". Order: the metric
  priority list (or the comparison's metrics in their order), then newest fiscal year first,
  then company order. At most 60.
- **Passages** are sanitized filing blocks, grouped into chunks of at most 3,000 characters
  inside one section, ranked by how many of the question's words they contain (lower-case words,
  a fixed stop-word list; ties by block order). At most 8. No embeddings and no vector database.
- Ids `F1…` and `P1…` are assigned here, in this order, and are the only ids an answer may cite.
- The whole context (fact lines plus passage lines) stays within about 24,000 characters: facts
  first, then passages while they fit.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date

from app.logic.concepts import LABELS
from app.logic.sanitize import Block
from app.models.common import MetricValue

MAX_FACTS = 60
# The latest five fiscal years of each company, so the 60 facts cover about 12 metrics instead of
# 3 metrics over 20 years.
FACT_YEARS = 5
MAX_PASSAGES = 8
MAX_CONTEXT_CHARS = 24_000
MAX_PASSAGE_CHARS = 3_000
NO_SECTION = "no section detected"

FACT_PRIORITY = (
    "revenue",
    "net_income",
    "net_margin",
    "operating_income",
    "operating_margin",
    "operating_cash_flow",
    "capex",
    "fcf",
    "debt_to_equity",
    "roe",
    "roa",
    "assets",
    "liabilities",
    "equity",
    "revenue_growth",
)
STOPWORDS = frozenset(
    "a an and are as at be by can did do does for from has have how in is it its of on or "
    "so than that the their there these this to was were what when where which who why will "
    "with would about after before between during into over under per vs".split()
)
_WORD = re.compile(r"[a-z0-9]+")


@dataclass(frozen=True)
class Fact:
    source_id: str
    cik: str
    ticker: str
    metric_id: str
    label: str
    value_text: str
    fiscal_year_label: str
    period_start: date | None
    period_end: date
    basis: str
    form: str | None
    accession: str | None
    filed: date | None
    value: float | None = None

    def line(self) -> str:
        period = f"{self.fiscal_year_label} ({_day(self.period_start)} – {_day(self.period_end)})"
        filing = (
            f"{self.form} {self.accession} filed {_day(self.filed)}"
            if self.accession
            else "no filing reference"
        )
        return (
            f"[{self.source_id}] {self.ticker} · {self.label} · {self.value_text} · {period} · "
            f"{self.basis} · {filing}"
        )


@dataclass(frozen=True)
class Passage:
    source_id: str
    cik: str
    ticker: str
    form: str
    accession: str
    filing_date: date | None
    section: str
    block_start: int
    block_end: int
    text: str

    def header(self) -> str:
        return (
            f"[{self.source_id}] {self.ticker} {self.form} {self.accession} filed "
            f"{_day(self.filing_date)} · {self.section} · "
            f"blocks {self.block_start}–{self.block_end}"
        )

    def line(self) -> str:
        return f"{self.header()}\n{self.text}"


@dataclass(frozen=True)
class FactSource:
    """One company's annual series, as built by `logic/statements.py`."""

    cik: str
    ticker: str
    series: Mapping[str, list[MetricValue]]


@dataclass(frozen=True)
class DocumentInput:
    """One sanitized filing document with its detected sections."""

    cik: str
    ticker: str
    form: str
    accession: str
    filing_date: date | None
    blocks: list[Block]
    section_of_block: list[str | None]
    section_labels: Mapping[str, str]


@dataclass(frozen=True)
class Context:
    facts: tuple[Fact, ...]
    passages: tuple[Passage, ...]
    chars: int


def _day(value: date | None) -> str:
    return value.isoformat() if value else "unknown"


def _value_text(metric: MetricValue) -> str:
    value = metric.value
    if metric.unit == "percent":
        return f"{value * 100:.2f}%"
    if metric.unit == "ratio":
        return f"{value:.2f}×"
    amount = f"{int(value):,}" if float(value).is_integer() else f"{value:,.2f}"
    return f"{amount} {metric.unit}"


def _filing_of(metric: MetricValue) -> tuple[str | None, str | None, date | None]:
    """The form, accession and filing date of a value, or of the first input that has them."""
    if metric.provenance:
        return metric.provenance.form, metric.provenance.accession, metric.provenance.filed
    for item in metric.inputs:
        found = _filing_of(item)
        if found[1]:
            return found
    return None, None, None


def _fact(source: FactSource, metric: MetricValue) -> Fact:
    form, accession, filed = _filing_of(metric)
    basis = metric.provenance.concept if metric.provenance else (metric.formula or "")
    return Fact(
        source_id="",
        cik=source.cik,
        ticker=source.ticker,
        metric_id=metric.metric_id,
        label=LABELS.get(metric.metric_id, metric.metric_id),
        value_text=_value_text(metric),
        fiscal_year_label=metric.fiscal_year_label,
        period_start=metric.period_start,
        period_end=metric.period_end,
        basis=basis,
        form=form,
        accession=accession,
        filed=filed,
        value=metric.value,
    )


def select_facts(sources: list[FactSource], metric_ids: list[str] | None) -> list[Fact]:
    """Facts in priority order, newest year first, company order; at most 60, without ids yet."""
    order = metric_ids if metric_ids is not None else list(FACT_PRIORITY)
    facts: list[Fact] = []
    for metric_id in order:
        newest_first = [
            [
                v
                for v in reversed(list(source.series.get(metric_id, []))[-FACT_YEARS:])
                if v.status == "ok" and v.value is not None
            ]
            for source in sources
        ]
        for position in range(max((len(v) for v in newest_first), default=0)):
            for source, values in zip(sources, newest_first, strict=True):
                if position < len(values):
                    facts.append(_fact(source, values[position]))
                    if len(facts) == MAX_FACTS:
                        return facts
    return facts


def _chunks(document: DocumentInput) -> list[tuple[int, int, str, str]]:
    """(first block, last block, section label, text) pieces of at most 3,000 characters."""
    chunks: list[tuple[int, int, str, str]] = []
    start, parts, section = None, [], None

    def flush(end: int) -> None:
        nonlocal start, parts
        if start is not None and parts:
            label = document.section_labels.get(section, NO_SECTION) if section else NO_SECTION
            chunks.append((start, end, label, "\n".join(parts)))
        start, parts = None, []

    last = -1
    for index, block in enumerate(document.blocks):
        block_section = (
            document.section_of_block[index] if index < len(document.section_of_block) else None
        )
        text = block.text
        if start is not None and (
            block_section != section or len("\n".join(parts)) + 1 + len(text) > MAX_PASSAGE_CHARS
        ):
            flush(last)
        section = block_section
        while len(text) > MAX_PASSAGE_CHARS:  # one very long block becomes several pieces
            flush(last)
            label = document.section_labels.get(section, NO_SECTION) if section else NO_SECTION
            chunks.append((index, index, label, text[:MAX_PASSAGE_CHARS]))
            text = text[MAX_PASSAGE_CHARS:]
        if start is None:
            start = index
        parts.append(text)
        last = index
    flush(last)
    return chunks


def _terms(text: str) -> set[str]:
    return {w for w in _WORD.findall(text.lower()) if len(w) > 1 and w not in STOPWORDS}


def rank_chunks(document: DocumentInput, question: str) -> list[tuple[int, int, str, str]]:
    """Chunks that contain at least one question word, best first; ties by block order."""
    terms = _terms(question)
    if not terms:
        return []
    scored = []
    for chunk in _chunks(document):
        words = _WORD.findall(chunk[3].lower())
        present = terms.intersection(words)
        if present:
            occurrences = sum(1 for w in words if w in terms)
            scored.append(((-len(present), -occurrences, chunk[0]), chunk))
    return [chunk for _, chunk in sorted(scored, key=lambda item: item[0])]


def build_context(
    sources: list[FactSource],
    metric_ids: list[str] | None,
    document: DocumentInput | None,
    question: str,
) -> Context:
    """The facts and passages for one question, numbered and within the limits."""
    facts: list[Fact] = []
    chars = 0
    for fact in select_facts(sources, metric_ids):
        numbered = Fact(**{**fact.__dict__, "source_id": f"F{len(facts) + 1}"})
        if chars + len(numbered.line()) > MAX_CONTEXT_CHARS:
            break
        facts.append(numbered)
        chars += len(numbered.line())
    passages: list[Passage] = []
    if document is not None:
        for start, end, section, text in rank_chunks(document, question):
            if len(passages) == MAX_PASSAGES:
                break
            passage = Passage(
                source_id=f"P{len(passages) + 1}",
                cik=document.cik,
                ticker=document.ticker,
                form=document.form,
                accession=document.accession,
                filing_date=document.filing_date,
                section=section,
                block_start=start,
                block_end=end,
                text=text,
            )
            if chars + len(passage.line()) > MAX_CONTEXT_CHARS:
                continue
            passages.append(passage)
            chars += len(passage.line())
    return Context(tuple(facts), tuple(passages), chars)
