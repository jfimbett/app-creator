"""Checking the AI answer's source references (M5). Pure function.

A reference `[F<n>]` or `[P<n>]` is valid only when that id was supplied in this request. Valid
ones become source chips; others are listed as "Reference not in the supplied sources". A valid
chip shows that the cited source exists and was supplied; it does not prove the sentence citing
it is true. The answer itself is returned as text, and numbers are never parsed from it.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from typing import Literal

from app.logic.retrieval import Fact, Passage

NOT_SUPPLIED = "Reference not in the supplied sources"
NO_VALID_SOURCES = "No valid sources cited"
# A bracket holding one or more ids: "[F2]", "[F2, P1]", "[F3; F2]"; also fullwidth 【F4】.
_GROUP = re.compile(r"[\[【]\s*([FP]\d+(?:\s*[,;]\s*[FP]\d+)*)\s*[\]】]")
_ID = re.compile(r"[FP]\d+")
_WELL_FORMED = re.compile(r"[FP][1-9]\d{0,2}")


@dataclass(frozen=True)
class Chip:
    source_id: str
    valid: bool
    kind: Literal["fact", "passage"]
    label: str
    period: str
    date: date | None
    link: str


@dataclass(frozen=True)
class CitationResult:
    citations: list[Chip]
    invalid_references: list[str]
    note: str | None


def _fact_chip(fact: Fact) -> Chip:
    filing = f" · {fact.form} {fact.accession}" if fact.accession else ""
    start = fact.period_start.isoformat() if fact.period_start else "?"
    return Chip(
        source_id=fact.source_id,
        valid=True,
        kind="fact",
        label=f"{fact.basis} · {fact.fiscal_year_label}{filing}",
        period=f"{start} – {fact.period_end.isoformat()}",
        date=fact.filed,
        link=f"/companies/{fact.cik}",
    )


def _passage_chip(passage: Passage) -> Chip:
    return Chip(
        source_id=passage.source_id,
        valid=True,
        kind="passage",
        label=f"{passage.form} {passage.accession} · {passage.section}",
        period=f"blocks {passage.block_start}–{passage.block_end}",
        date=passage.filing_date,
        link=f"/companies/{passage.cik}/filings/{passage.accession}#block-{passage.block_start}",
    )


def validate(
    answer: str, facts: list[Fact] | tuple[Fact, ...], passages: list[Passage] | tuple[Passage, ...]
) -> CitationResult:
    """Chips for supplied ids in order of first mention; other ids as invalid references."""
    supplied = {f.source_id: _fact_chip(f) for f in facts}
    supplied.update({p.source_id: _passage_chip(p) for p in passages})
    citations: list[Chip] = []
    invalid: list[str] = []
    ids = [i for group in _GROUP.findall(answer) for i in _ID.findall(group)]
    for source_id in ids:
        if _WELL_FORMED.fullmatch(source_id) and source_id in supplied:
            if all(c.source_id != source_id for c in citations):
                citations.append(supplied[source_id])
        elif source_id not in invalid:
            invalid.append(source_id)
    return CitationResult(citations, invalid, None if citations else NO_VALID_SOURCES)
