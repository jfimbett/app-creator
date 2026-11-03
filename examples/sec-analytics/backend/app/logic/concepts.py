"""XBRL concept names used by SEC Analytics (us-gaap taxonomy).

These are tag names from SEC Company Facts (`facts.us-gaap.<concept>`). The fixture capture keeps
exactly `CAPTURE_CONCEPTS`, so M2 can map further metrics without recapturing.
"""

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
