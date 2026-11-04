#!/usr/bin/env python3
"""Mapping check required by the M2 brief §6: which concepts appear in annual 10-K facts, and when.

Reads the fixture JSON directly (no app code). Duration concepts count 350-380 day facts; instant
concepts count facts with no start. Run from the repository root.
"""
import json
from datetime import date

CONCEPTS = [
    "Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax", "SalesRevenueNet",
    "RevenueFromContractWithCustomerIncludingAssessedTax", "OperatingIncomeLoss", "NetIncomeLoss",
    "IncomeTaxExpenseBenefit", "InterestExpense", "InterestExpenseNonoperating", "InterestExpenseDebt",
    "DepreciationDepletionAndAmortization", "DepreciationAndAmortization",
    "DepreciationAmortizationAndAccretionNet", "NetCashProvidedByUsedInOperatingActivities",
    "PaymentsToAcquirePropertyPlantAndEquipment", "Assets", "AssetsCurrent", "Liabilities",
    "LiabilitiesCurrent", "StockholdersEquity", "LongTermDebtNoncurrent", "LongTermDebtCurrent",
    "CommercialPaper", "ShortTermBorrowings",
]
for cik, name in (("0000320193", "AAPL"), ("0000789019", "MSFT"), ("0001652044", "GOOGL")):
    gaap = json.load(open(f"examples/sec-analytics/fixtures/companyfacts/CIK{cik}.json"))["facts"]["us-gaap"]
    print(f"== {name}")
    for concept in CONCEPTS:
        units = gaap.get(concept, {}).get("units", {})
        ends = set()
        for unit, rows in units.items():
            for r in rows:
                if r.get("form") not in ("10-K", "10-K/A"):
                    continue
                if r.get("start"):
                    days = (date.fromisoformat(r["end"]) - date.fromisoformat(r["start"])).days
                    if 350 <= days <= 380:
                        ends.add(r["end"])
                else:
                    ends.add(r["end"])
        span = f"{min(ends)[:4]}..{max(ends)[:4]} ({len(ends)} dates)" if ends else "absent in annual 10-K facts"
        print(f"  {concept:58} {span} units={sorted(units)}")
