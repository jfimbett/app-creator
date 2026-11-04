"""XBRL concept names used by SEC Analytics (us-gaap taxonomy).

These are tag names from SEC Company Facts (`facts.us-gaap.<concept>`). The fixture capture keeps
exactly `CAPTURE_CONCEPTS`, so M2 can map further metrics without recapturing.

Mapping checked against the fixtures on 2026-11-04 (annual 10-K facts per concept; see the decision
log in milestones/architecture.md). A list is a priority order for one period, never a sum:

- Interest expense: Apple has `InterestExpense` to FY2023 and nothing after it; Microsoft and
  Alphabet move to `InterestExpenseNonoperating`. `InterestExpenseDebt` (Apple to FY2021) is a
  narrower last resort.
- D&A: Apple has these concepts; Microsoft and Alphabet report none of them, so D&A and EBITDA show
  as missing and unavailable for those two, rather than taken from another concept unchecked.
"""

from __future__ import annotations

from dataclasses import dataclass

TAXONOMY = "us-gaap"

# Revenue: per period, the first concept present in this order wins; concepts are never summed.
REVENUE_CONCEPTS: tuple[str, ...] = (
    "Revenues",
    "RevenueFromContractWithCustomerExcludingAssessedTax",
    "SalesRevenueNet",
    "RevenueFromContractWithCustomerIncludingAssessedTax",
)

NET_INCOME_CONCEPT = "NetIncomeLoss"

CAPTURE_CONCEPTS: tuple[str, ...] = (
    *REVENUE_CONCEPTS,
    "OperatingIncomeLoss",
    NET_INCOME_CONCEPT,
    "IncomeTaxExpenseBenefit",
    "InterestExpense",
    "InterestExpenseNonoperating",
    "InterestExpenseDebt",
    "DepreciationDepletionAndAmortization",
    "DepreciationAndAmortization",
    "DepreciationAmortizationAndAccretionNet",
    "NetCashProvidedByUsedInOperatingActivities",
    "PaymentsToAcquirePropertyPlantAndEquipment",
    "Assets",
    "AssetsCurrent",
    "Liabilities",
    "LiabilitiesCurrent",
    "StockholdersEquity",
    "LongTermDebtNoncurrent",
    "LongTermDebtCurrent",
    "CommercialPaper",
    "ShortTermBorrowings",
)

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
# PaymentsToAcquireProductiveAssets is outside CAPTURE_CONCEPTS, so it never appears in the
# recorded fixtures. Checked on live data 2026-11-04: NVIDIA tags its capex this way. It can include
# intangible assets, which is why it comes second; the concept used is always shown.
CAPEX_CONCEPTS: tuple[str, ...] = (
    "PaymentsToAcquirePropertyPlantAndEquipment",
    "PaymentsToAcquireProductiveAssets",
)
ALL_CONCEPTS: tuple[str, ...] = (*CAPTURE_CONCEPTS, "PaymentsToAcquireProductiveAssets")


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
    ReportedMetric(
        "interest_expense",
        "Interest expense",
        INTEREST_CONCEPTS,
        "no mapped interest expense concept",
    ),
    ReportedMetric(
        "d_and_a", "Depreciation and amortization (D&A)", D_AND_A_CONCEPTS, "no mapped D&A concept"
    ),
    _one(
        "operating_cash_flow", "Operating cash flow", "NetCashProvidedByUsedInOperatingActivities"
    ),
    ReportedMetric(
        "capex", "Capital expenditure (capex)", CAPEX_CONCEPTS, "no mapped capex concept"
    ),
    _one("assets", "Total assets", "Assets", instant=True),
    _one("assets_current", "Current assets", "AssetsCurrent", instant=True),
    _one("liabilities", "Total liabilities", "Liabilities", instant=True),
    _one("liabilities_current", "Current liabilities", "LiabilitiesCurrent", instant=True),
    _one("equity", "Stockholders' equity", "StockholdersEquity", instant=True),
    _one(
        "debt_long_term_noncurrent",
        "Long-term debt, noncurrent",
        "LongTermDebtNoncurrent",
        instant=True,
    ),
    _one("debt_long_term_current", "Long-term debt, current", "LongTermDebtCurrent", instant=True),
    ReportedMetric(
        "debt_short_term",
        "Short-term debt",
        SHORT_TERM_DEBT_CONCEPTS,
        "no short-term debt concept reported",
        instant=True,
    ),
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
        {
            "id": m.id,
            "label": m.label,
            "unit_kind": "currency",
            "kind": "reported",
            "formula": None,
            "concepts": list(m.concepts),
        }
        for m in REPORTED_METRICS
        if m.id not in _COMPONENTS
    ]
    derived = [
        {
            "id": metric_id,
            "label": label,
            "unit_kind": unit_kind,
            "kind": "derived",
            "formula": FORMULAS[metric_id],
            "concepts": [],
        }
        for metric_id, label, unit_kind in _DERIVED
    ]
    return reported + derived


CATALOG_BY_ID: dict[str, dict] = {item["id"]: item for item in catalog()}
