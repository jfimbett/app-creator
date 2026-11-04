#!/usr/bin/env python3
"""Concept catalog, period helpers and small clean-ups for M2. Run from the repo root."""
BE = "examples/sec-analytics/backend/app/"

s = open(BE + "logic/concepts.py").read()
s = s.replace('''exactly `CAPTURE_CONCEPTS`, so M2 can map further metrics without recapturing.
"""
''', '''exactly `CAPTURE_CONCEPTS`, so M2 can map further metrics without recapturing.

Mapping checked against the fixtures on 2026-11-04 (annual 10-K facts per concept; see the decision
log in milestones/architecture.md). A list is a priority order for one period, never a sum:

- Interest expense: Apple has `InterestExpense` to FY2023 and nothing after it; Microsoft and Alphabet
  move to `InterestExpenseNonoperating`. `InterestExpenseDebt` (Apple to FY2021) is a narrower last resort.
- D&A: Apple has these concepts; Microsoft and Alphabet report none of them, so D&A and EBITDA show
  as missing and unavailable for those two, rather than taken from another concept unchecked.
"""

from __future__ import annotations

from dataclasses import dataclass
''')
s += '''
INTEREST_CONCEPTS: tuple[str, ...] = (
    "InterestExpense",
    "InterestExpenseNonoperating",
    "InterestExpenseDebt",
)
D_AND_A_CONCEPTS: tuple[str, ...] = (
    "DepreciationDepletionAndAmortization",
    "DepreciationAndAmortization",
    "DepreciationAmortizationAndAccretionNet",
)
SHORT_TERM_DEBT_CONCEPTS: tuple[str, ...] = ("CommercialPaper", "ShortTermBorrowings")
ALL_CONCEPTS = CAPTURE_CONCEPTS


@dataclass(frozen=True)
class ReportedMetric:
    """A line taken directly from SEC facts: the first concept present for a period wins."""

    id: str
    label: str
    concepts: tuple[str, ...]
    missing_reason: str
    instant: bool = False


def _one(metric_id: str, label: str, concept: str, instant: bool = False) -> ReportedMetric:
    return ReportedMetric(metric_id, label, (concept,), f"no {concept} fact", instant)


REPORTED_METRICS: tuple[ReportedMetric, ...] = (
    ReportedMetric("revenue", "Revenue", REVENUE_CONCEPTS, "no mapped revenue concept"),
    _one("operating_income", "Operating income", "OperatingIncomeLoss"),
    _one("net_income", "Net income", NET_INCOME_CONCEPT),
    _one("income_tax", "Income tax expense", "IncomeTaxExpenseBenefit"),
    ReportedMetric("interest_expense", "Interest expense", INTEREST_CONCEPTS,
                   "no mapped interest expense concept"),
    ReportedMetric("d_and_a", "Depreciation and amortization (D&A)", D_AND_A_CONCEPTS,
                   "no mapped D&A concept"),
    _one("operating_cash_flow", "Operating cash flow", "NetCashProvidedByUsedInOperatingActivities"),
    _one("capex", "Capital expenditure (capex)", "PaymentsToAcquirePropertyPlantAndEquipment"),
    _one("assets", "Total assets", "Assets", instant=True),
    _one("assets_current", "Current assets", "AssetsCurrent", instant=True),
    _one("liabilities", "Total liabilities", "Liabilities", instant=True),
    _one("liabilities_current", "Current liabilities", "LiabilitiesCurrent", instant=True),
    _one("equity", "Stockholders' equity", "StockholdersEquity", instant=True),
    _one("debt_long_term_noncurrent", "Long-term debt, noncurrent", "LongTermDebtNoncurrent",
         instant=True),
    _one("debt_long_term_current", "Long-term debt, current", "LongTermDebtCurrent", instant=True),
    ReportedMetric("debt_short_term", "Short-term debt", SHORT_TERM_DEBT_CONCEPTS,
                   "no short-term debt concept reported", instant=True),
)

# Derived metrics: id, label, unit kind. Formulas live in logic/metrics.py.
_DERIVED: tuple[tuple[str, str, str], ...] = (
    ("revenue_growth", "Revenue growth", "percent"),
    ("operating_margin", "Operating margin", "percent"),
    ("net_margin", "Net margin", "percent"),
    ("fcf_margin", "FCF margin", "percent"),
    ("fcf", "Free cash flow (FCF)", "currency"),
    ("ebit", "EBIT", "currency"),
    ("ebitda", "EBITDA", "currency"),
    ("working_capital", "Working capital", "currency"),
    ("debt", "Total debt", "currency"),
    ("debt_to_equity", "Debt-to-equity", "ratio"),
    ("roe", "Return on equity (ROE)", "percent"),
    ("roa", "Return on assets (ROA)", "percent"),
)
# Shown only as debt components inside the balance summary, not offered in the explorer.
_COMPONENTS = {"debt_long_term_noncurrent", "debt_long_term_current", "debt_short_term"}

LABELS: dict[str, str] = {
    **{m.id: m.label for m in REPORTED_METRICS},
    **{metric_id: label for metric_id, label, _ in _DERIVED},
}


def catalog() -> list[dict]:
    """The explorer's metrics: id, label, unit kind, kind, formula and SEC concepts."""
    from app.logic.metrics import FORMULAS  # local import: metrics has no need of this module

    reported = [
        {"id": m.id, "label": m.label, "unit_kind": "currency", "kind": "reported",
         "formula": None, "concepts": list(m.concepts)}
        for m in REPORTED_METRICS
        if m.id not in _COMPONENTS
    ]
    derived = [
        {"id": metric_id, "label": label, "unit_kind": unit_kind, "kind": "derived",
         "formula": FORMULAS[metric_id], "concepts": []}
        for metric_id, label, unit_kind in _DERIVED
    ]
    return reported + derived


CATALOG_BY_ID: dict[str, dict] = {item["id"]: item for item in catalog()}
'''
open(BE + "logic/concepts.py", "w").write(s)

s = open(BE + "logic/periods.py").read()
s = s.replace('"""Annual period selection and the duplicate policy (first version, M1).',
              '"""Annual period selection and the duplicate and restatement policy.')
s = s.replace('''- Missing values stay missing (`None`, status "missing", with a reason), never 0.
"""''', '''- Instants belong to a period only when dated exactly its end date; same duplicate policy.
- Periods shown are the distinct (start, end) pairs of revenue and net income facts. When two pairs
  share an end date, the one from the latest filed fact (tie: higher accession) is kept.
- Restatements: the latest filing wins, so history can differ from what was first reported.
  The views say so: "Values may reflect later restatements; not point-in-time."
- Missing values stay missing (`None`, status "missing", with a reason), never 0.
"""''')
s = s.replace('''def pick_first(
    selected''', '''def select_periods(
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
    selected''')
open(BE + "logic/periods.py", "w").write(s)

s = open(BE + "data/source.py").read()
old = '''        if self._client is None:
            try:
                validate_user_agent(self._user_agent())
            except SecContactNotConfigured:
                raise
            return
'''
assert old in s
s = s.replace(old, '''        if self._client is None:
            validate_user_agent(self._user_agent())
''')
s = s.replace("from app.clients.sec import SecClient, SecContactNotConfigured, SecNotFound, validate_user_agent\n",
              "from app.clients.sec import SecClient, SecNotFound, validate_user_agent\n")
open(BE + "data/source.py", "w").write(s)
print("ok")
