"""Annual period selection and the duplicate and restatement policy.

Pure functions over SEC Company Facts data (no files, network or clock). The rules
(milestones/architecture.md "Financial data rules", brief §7):

- A period is identified by its `start`/`end` dates, never by `fy`/`fp`: those describe the
  filing that reported the value, and later 10-Ks repeat earlier years as comparatives.
- A *duration* fact has a `start`; an *instant* fact (a balance on one date) has only `end`.
- Annual = a duration of 350-380 days inclusive (`end - start`), so 52/53-week years count;
  quarterly and year-to-date durations are excluded.
- Only `10-K` and `10-K/A` facts feed annual series.
- Duplicates: per (concept, unit, start, end) keep the latest `filed`; on a tie the higher
  accession number. Values are never summed.
- Instants belong to a period only when dated exactly its end date; same duplicate policy.
- Periods shown are the distinct (start, end) pairs of revenue and net income facts. When two pairs
  share an end date, the one from the latest filed fact (tie: higher accession) is kept.
- Restatements: the latest filing wins, so history can differ from what was first reported.
  The views say so: "Values may reflect later restatements; not point-in-time."
- Missing values stay missing (`None`, status "missing", with a reason), never 0.
"""

from __future__ import annotations

import re
from collections import Counter
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import date

from app.logic.concepts import TAXONOMY

ANNUAL_MIN_DAYS = 350
ANNUAL_MAX_DAYS = 380
ANNUAL_FORMS = frozenset({"10-K", "10-K/A"})
REVENUE_MISSING_REASON = "no mapped revenue concept"

_CURRENCY = re.compile(r"[A-Z]{3}")  # ISO 4217 code, e.g. "USD"; excludes "USD/shares"


@dataclass(frozen=True, order=True)
class Period:
    """An annual period, identified only by its first and last day."""

    start: date
    end: date

    @property
    def label(self) -> str:
        """Fiscal year label, e.g. "FY2024" (always shown next to the end date)."""
        return fiscal_year_label(self.end)


@dataclass(frozen=True)
class Fact:
    """One SEC fact with everything needed for provenance."""

    concept: str
    taxonomy: str
    unit: str
    start: date | None
    end: date
    val: int | float
    form: str
    accn: str
    filed: date
    fy: int | None
    fp: str | None


@dataclass(frozen=True)
class AnnualValue:
    """A value for one period: the chosen fact, or missing with a reason."""

    period: Period
    fact: Fact | None
    reason: str | None = None

    @property
    def value(self) -> int | float | None:
        """The reported value, or None when missing (never 0 for missing)."""
        return None if self.fact is None else self.fact.val

    @property
    def status(self) -> str:
        """"ok" when a fact was found, else "missing"."""
        return "missing" if self.fact is None else "ok"


def fiscal_year_label(end: date) -> str:
    """Return `FY<year of the end date>`."""
    return f"FY{end.year}"


def parse_facts(
    companyfacts: Mapping, concepts: Iterable[str], taxonomy: str = TAXONOMY
) -> list[Fact]:
    """Read the facts of `concepts` from a Company Facts document.

    Absent concepts are skipped (not invented). Rows lacking a required field (`end`, `val`,
    `form`, `accn`, `filed`) are skipped because they cannot carry provenance.
    """
    tagged = companyfacts.get("facts", {}).get(taxonomy, {})
    facts: list[Fact] = []
    for concept in concepts:
        units = tagged.get(concept, {}).get("units", {})
        for unit, rows in units.items():
            facts.extend(_parse_row(concept, taxonomy, unit, row) for row in rows if _complete(row))
    return facts


def _complete(row: Mapping) -> bool:
    """True when a fact row has the fields needed for selection and provenance."""
    return all(row.get(key) is not None for key in ("end", "val", "form", "accn", "filed"))


def _parse_row(concept: str, taxonomy: str, unit: str, row: Mapping) -> Fact:
    """Turn one Company Facts row into a `Fact`."""
    start = row.get("start")
    return Fact(
        concept=concept,
        taxonomy=taxonomy,
        unit=unit,
        start=date.fromisoformat(start) if start else None,
        end=date.fromisoformat(row["end"]),
        val=row["val"],
        form=row["form"],
        accn=row["accn"],
        filed=date.fromisoformat(row["filed"]),
        fy=row.get("fy"),
        fp=row.get("fp"),
    )


def is_instant(fact: Fact) -> bool:
    """True for a point-in-time fact (no start date), e.g. total assets."""
    return fact.start is None


def is_annual_duration(fact: Fact) -> bool:
    """True when the fact covers 350-380 days inclusive (`end - start`)."""
    if fact.start is None:
        return False
    return ANNUAL_MIN_DAYS <= (fact.end - fact.start).days <= ANNUAL_MAX_DAYS


def _accession_key(accn: str) -> int:
    """Accession number as an integer, so "-24-000101" ranks above "-24-000099"."""
    digits = re.sub(r"\D", "", accn)
    return int(digits) if digits else -1


def choose_fact(candidates: Iterable[Fact]) -> Fact:
    """Pick one fact from duplicates: latest `filed`, then higher accession. Never sums."""
    return max(candidates, key=lambda f: (f.filed, _accession_key(f.accn)))


def annual_facts(facts: Iterable[Fact], unit: str) -> dict[tuple[str, Period], Fact]:
    """Select one fact per (concept, annual period) from 10-K/10-K/A durations in `unit`."""
    groups: dict[tuple[str, Period], list[Fact]] = {}
    for fact in facts:
        if fact.start is None or fact.unit != unit or fact.form not in ANNUAL_FORMS:
            continue
        if not is_annual_duration(fact):
            continue
        groups.setdefault((fact.concept, Period(fact.start, fact.end)), []).append(fact)
    return {key: choose_fact(group) for key, group in sorted(groups.items())}


def annual_periods(selected: Mapping[tuple[str, Period], Fact]) -> list[Period]:
    """All periods that have at least one selected fact, earliest first."""
    return sorted({period for _, period in selected})


def select_periods(
    selected: Mapping[tuple[str, Period], Fact], concepts: Iterable[str]
) -> list[Period]:
    """Annual periods from `concepts`' facts, one per end date, earliest first."""
    wanted = set(concepts)
    best: dict[date, tuple[Period, Fact]] = {}
    for (concept, period), fact in selected.items():
        if concept not in wanted:
            continue
        current = best.get(period.end)
        if current is None or choose_fact([current[1], fact]) is fact:
            best[period.end] = (period, fact)
    return [best[end][0] for end in sorted(best)]


def instant_facts(facts: Iterable[Fact], unit: str) -> dict[tuple[str, date], Fact]:
    """One 10-K/10-K/A instant fact per (concept, end date) in `unit`, duplicates resolved."""
    groups: dict[tuple[str, date], list[Fact]] = {}
    for fact in facts:
        if is_instant(fact) and fact.unit == unit and fact.form in ANNUAL_FORMS:
            groups.setdefault((fact.concept, fact.end), []).append(fact)
    return {key: choose_fact(group) for key, group in groups.items()}


def pick_first(
    selected: Mapping[tuple[str, Period], Fact],
    concepts: Iterable[str],
    period: Period,
    missing_reason: str,
) -> AnnualValue:
    """The first concept in priority order with a fact for `period`; else missing."""
    for concept in concepts:
        fact = selected.get((concept, period))
        if fact is not None:
            return AnnualValue(period=period, fact=fact)
    return AnnualValue(period=period, fact=None, reason=missing_reason)


def reporting_currency(facts: Iterable[Fact], revenue_concepts: Iterable[str]) -> str | None:
    """The ISO currency unit with the most annual 10-K revenue facts (ties: alphabetical)."""
    wanted = set(revenue_concepts)
    counts = Counter(
        f.unit
        for f in facts
        if f.concept in wanted
        and _CURRENCY.fullmatch(f.unit)
        and f.form in ANNUAL_FORMS
        and is_annual_duration(f)
    )
    if not counts:
        return None
    return min(counts, key=lambda unit: (-counts[unit], unit))


def instant_at(facts: Iterable[Fact], concept: str, unit: str, end: date) -> Fact | None:
    """The 10-K/10-K/A instant fact of `concept` dated exactly `end`, duplicates resolved."""
    matches = [
        f
        for f in facts
        if f.concept == concept
        and f.unit == unit
        and is_instant(f)
        and f.end == end
        and f.form in ANNUAL_FORMS
    ]
    return choose_fact(matches) if matches else None
