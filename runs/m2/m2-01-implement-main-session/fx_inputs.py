#!/usr/bin/env python3
"""Quote the raw fixture facts behind the FX5+ known answers. Does not import any app code.

Picks latest filed, then higher accession, among 10-K/10-K/A rows for the exact dates. Run from the repo root.
"""
import json

C = {
    "AAPL": ("0000320193", "2025-09-28", "2026-09-26", "2025-09-27"),
    "MSFT": ("0000789019", "2025-07-01", "2026-06-30", "2025-06-30"),
}
DUR = ["RevenueFromContractWithCustomerExcludingAssessedTax", "NetIncomeLoss",
       "NetCashProvidedByUsedInOperatingActivities", "PaymentsToAcquirePropertyPlantAndEquipment",
       "OperatingIncomeLoss", "IncomeTaxExpenseBenefit", "InterestExpense", "InterestExpenseNonoperating"]
INST = ["StockholdersEquity", "Assets", "LongTermDebtNoncurrent", "LongTermDebtCurrent", "CommercialPaper",
        "ShortTermBorrowings", "AssetsCurrent", "LiabilitiesCurrent"]


def best(rows, start, end):
    hits = [r for r in rows if r["form"] in ("10-K", "10-K/A") and r["end"] == end and r.get("start") == start]
    return max(hits, key=lambda r: (r["filed"], r["accn"])) if hits else None


for name, (cik, start, end, prior_end) in C.items():
    gaap = json.load(open(f"examples/sec-analytics/fixtures/companyfacts/CIK{cik}.json"))["facts"]["us-gaap"]
    print(f"== {name} {start}..{end}")
    for c in DUR:
        r = best(gaap.get(c, {}).get("units", {}).get("USD", []), start, end)
        print(" ", c, "ABSENT" if r is None else (r["val"], r["accn"], r["filed"], r["form"]))
    for c in INST:
        for e in (end, prior_end):
            r = best(gaap.get(c, {}).get("units", {}).get("USD", []), None, e)
            print(" ", c, e, "ABSENT" if r is None else (r["val"], r["accn"], r["filed"], r["form"]))
    rows = gaap["RevenueFromContractWithCustomerExcludingAssessedTax"]["units"]["USD"]
    prior = [r for r in rows if r["form"] in ("10-K", "10-K/A") and r["end"] == prior_end and r.get("start")]
    print("  prior revenue rows", [(r["start"], r["val"], r["accn"], r["filed"]) for r in prior][:4])
    for c in ("InterestExpense",):
        ends = sorted({r["end"] for r in gaap.get(c, {}).get("units", {}).get("USD", []) if r["form"] == "10-K"})
        print("  last InterestExpense end", ends[-1:] )
