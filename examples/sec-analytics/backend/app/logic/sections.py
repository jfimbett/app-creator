"""Find the "Item" sections of a 10-K or 10-Q in its text blocks (brief §7, M3-AC4, AC7, E3).

Deterministic pattern rules on the text, so the result can be imperfect and is always labelled so.
1. A candidate is a short block (at most 200 characters) that starts "Item <number>", whose number
   is a real item of that form, and whose title does not start in lower case ("Item 1 of this
   report..." is a sentence). Table rows are not candidates: contents lists are often tables.
   A bare "Item 2" line that repeats, or sits right above the real heading, is a page header.
2. Contents skip: three or more candidates with under 300 characters between neighbours form a
   cluster. A first cluster whose items mostly recur later is a table of contents and is dropped.
   A cluster ends when an item repeats or a contents table ends, so the body's "Item 1" is kept.
   Later clusters are kept: real short sections ("Item 3 ... None.") look just like that.
3. For each item the first remaining candidate wins; document order is kept.
4. Fewer than 3 sections means no section list at all, with the note saying so. No best guess.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass
from typing import Literal

from app.logic.sanitize import Block

DETECTED_NOTE = "Sections detected automatically; may be imperfect"
NOT_DETECTED_NOTE = "Section boundaries not detected; showing full text"
MIN_SECTIONS = 3
MAX_HEADING_CHARS = 200
CLUSTER_GAP_CHARS = 300
CLUSTER_SIZE = 3
RUNNING_HEADER_REPEATS = 3

TEN_K_ITEMS = frozenset({
    "1", "1a", "1b", "1c", "2", "3", "4", "5", "6", "7", "7a", "8", "9", "9a", "9b", "9c",
    "10", "11", "12", "13", "14", "15", "16",
})
TEN_Q_ITEMS = {
    1: frozenset({"1", "2", "3", "4"}),
    2: frozenset({"1", "1a", "2", "3", "4", "5", "6"}),
}
_ROMAN = {"i": 1, "1": 1, "ii": 2, "2": 2}

_ITEM = re.compile(
    r"^\s*(?:part\s+(?P<part>ii|i|1|2)\s*[,.:\-–—]*\s*)?"
    r"item\s+(?P<number>\d{1,2})(?P<letter>[a-c](?![a-z]))?\s*[.:\-–—]*\s*(?P<title>.*)$",
    re.IGNORECASE,
)
_PART = re.compile(r"^\s*part\s+(?P<part>ii|i|1|2)\b(?!\s*,?\s*item)", re.IGNORECASE)


@dataclass(frozen=True)
class Section:
    id: str
    item: str
    title: str
    block_start: int


@dataclass(frozen=True)
class SectionResult:
    status: Literal["detected", "not_detected"]
    note: str
    sections: list[Section]
    section_of_block: list[str | None]
    heading_blocks: frozenset[int]


@dataclass
class _Candidate:
    index: int
    number: str
    part: int | None
    title: str
    key: str = ""


def _is_ten_q(form: str) -> bool:
    return form.startswith("10-Q")


def _candidates(blocks: list[Block], ten_q: bool) -> list[_Candidate]:
    """Item headings in document order, each with its Part (10-Q) and an assigned key."""
    found: list[_Candidate] = []
    part: int | None = None
    for index, block in enumerate(blocks):
        if len(block.text) > MAX_HEADING_CHARS:
            continue
        part_heading = _PART.match(block.text)
        if part_heading:
            part = _ROMAN[part_heading["part"].lower()]
        match = _ITEM.match(block.text)
        if not match:
            continue
        if match["part"]:
            part = _ROMAN[match["part"].lower()]
        number = match["number"] + (match["letter"] or "").lower()
        title = match["title"].strip()
        if title[:1].islower() or title[:1] in {",", ";", "("}:
            continue  # a sentence ("Item 1 of this report...") or a running header ("Item 3, 4")
        if not ten_q and number not in TEN_K_ITEMS:
            continue
        if ten_q and number not in TEN_Q_ITEMS[1] | TEN_Q_ITEMS[2]:
            continue
        # Table rows stay here so that they count in a contents cluster; they never become headings.
        found.append(_Candidate(index, number, part if ten_q else None, title))
    return _without_running_headers(found, blocks)


def _without_running_headers(found: list[_Candidate], blocks: list[Block]) -> list[_Candidate]:
    """Drop bare "Item 2" lines that are page headers, not headings (Microsoft's filings do this).

    A bare item line is a header when the same line repeats, or when the real heading follows it.
    """
    bare = Counter(blocks[c.index].text.lower() for c in found if not c.title)
    kept = []
    for candidate in found:
        following = blocks[candidate.index + 1].text if candidate.index + 1 < len(blocks) else ""
        if not candidate.title and (
            bare[blocks[candidate.index].text.lower()] >= RUNNING_HEADER_REPEATS
            or _ITEM.match(following)
            or _PART.match(following)
        ):
            continue
        kept.append(candidate)
    return kept


def _chars_between(blocks: list[Block], first: int, second: int) -> int:
    return sum(len(block.text) for block in blocks[first + 1 : second])


def _clusters(candidates: list[_Candidate], blocks: list[Block]) -> list[list[_Candidate]]:
    """Runs of close neighbours. A repeated item ends a run: the contents list is over."""
    runs: list[list[_Candidate]] = []
    current: list[_Candidate] = []
    seen: set[tuple[int | None, str]] = set()
    for candidate in candidates:
        key = (candidate.part, candidate.number)
        close = bool(current) and _chars_between(
            blocks, current[-1].index, candidate.index
        ) < CLUSTER_GAP_CHARS
        same_kind = bool(current) and (
            blocks[current[-1].index].kind == "table_row") == (
            blocks[candidate.index].kind == "table_row"
        )
        if close and same_kind and key not in seen:
            current.append(candidate)
        else:
            if current:
                runs.append(current)
            current = [candidate]
            seen = set()
        seen.add(key)
    if current:
        runs.append(current)
    return runs


def _drop_leading_contents(
    candidates: list[_Candidate], blocks: list[Block]
) -> list[_Candidate]:
    """Remove contents lists: table rows always, and the first cluster if its items recur later.

    Most items of a real contents list appear again in the body. If they do not, the cluster is
    the body itself, written very briefly, and is kept.
    """
    kept: list[_Candidate] = []
    runs = _clusters(candidates, blocks)
    leading = True
    for position, run in enumerate(runs):
        rows = [c for c in run if blocks[c.index].kind != "table_row"]
        if leading and len(run) >= CLUSTER_SIZE:
            later = {(c.part, c.number) for other in runs[position + 1 :] for c in other}
            recurring = sum(1 for c in run if (c.part, c.number) in later)
            if recurring * 2 >= len(run):
                leading = False
                continue
        if rows:
            leading = False
        kept.extend(rows)
    return kept


def _item_label(number: str) -> str:
    match = re.fullmatch(r"(\d+)([a-c]?)", number)
    return f"Item {match[1]}{match[2].upper()}"


def _title(candidate: _Candidate, blocks: list[Block]) -> str:
    """The heading's own title, or the next block if that is short ("Item 1." / "Business")."""
    if candidate.title:
        return candidate.title
    following = blocks[candidate.index + 1 :][:1]
    if following and len(following[0].text) <= MAX_HEADING_CHARS:
        return following[0].text
    return ""


def _accept(candidates: list[_Candidate], blocks: list[Block], ten_q: bool) -> list[Section]:
    sections: list[Section] = []
    seen: set[str] = set()
    current_part = 1
    for candidate in candidates:
        if ten_q:
            part = candidate.part or current_part
            if f"part{part}-item{candidate.number}" in seen or (
                candidate.number not in TEN_Q_ITEMS[part]
            ):
                part = 2  # no "Part II" heading was found, but this item can only be there
            if candidate.number not in TEN_Q_ITEMS[part]:
                continue
            section_id = f"part{part}-item{candidate.number}"
            roman = "I" * part
            label = f"Part {roman}, {_item_label(candidate.number)}"
            current_part = part
        else:
            section_id = f"item{candidate.number}"
            label = _item_label(candidate.number)
        if section_id in seen:
            continue
        seen.add(section_id)
        sections.append(Section(section_id, label, _title(candidate, blocks), candidate.index))
    return sections


def detect_sections(blocks: list[Block], form: str) -> SectionResult:
    """Sections of a document, or the labelled fallback when too few are found."""
    ten_q = _is_ten_q(form)
    sections = _accept(_drop_leading_contents(_candidates(blocks, ten_q), blocks), blocks, ten_q)
    if len(sections) < MIN_SECTIONS:
        return SectionResult(
            "not_detected", NOT_DETECTED_NOTE, [], [None] * len(blocks), frozenset()
        )
    section_of_block: list[str | None] = [None] * len(blocks)
    for position, section in enumerate(sections):
        end = sections[position + 1].block_start if position + 1 < len(sections) else len(blocks)
        section_of_block[section.block_start : end] = [section.id] * (end - section.block_start)
    return SectionResult(
        "detected", DETECTED_NOTE, sections, section_of_block,
        frozenset(section.block_start for section in sections),
    )
