#!/usr/bin/env python3
"""Compare the running app's live values with the raw SEC Company Facts JSON. Imports no app code.

usage: live_crosscheck.py <base-url> <cik> ...  The raw document is the one the backend cached from SEC.
Only checks 10-K/10-K/A annual durations and exact-date instants, latest filed then higher accession.
"""
import hashlib
import json
import sys
import urllib.request
from datetime import date
from pathlib import Path

base, ciks = sys.argv[1], sys.argv[2:]
cache = Path("examples/sec-analytics/backend/.cache/sec")
DUR = {"operating_cash_flow": ["NetCashProvidedByUsedInOperatingActivities"], "net_income": ["NetIncomeLoss"],
       "capex": ["PaymentsToAcquirePropertyPlantAndEquipment", "PaymentsToAcquireProductiveAssets"],
       "operating_income": ["OperatingIncomeLoss"]}
INST = {"assets": ["Assets"], "equity": ["StockholdersEquity"], "liabilities": ["Liabilities"]}
bad = 0


def pick(gaap, concepts, end, instant):
    for concept in concepts:
        rows = []
        for r in gaap.get(concept, {}).get("units", {}).get("USD", []):
            if r["form"] not in ("10-K", "10-K/A") or r["end"] != end:
                continue
            if instant and "start" not in r:
                rows.append(r)
            if not instant and "start" in r:
                days = (date.fromisoformat(r["end"]) - date.fromisoformat(r["start"])).days
                if 350 <= days <= 380:
                    rows.append(r)
        if rows:
            return max(rows, key=lambda r: (r["filed"], int(r["accn"].replace("-", ""))))
    return None


for cik in ciks:
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
    fin = json.load(urllib.request.urlopen(f"{base}/api/companies/{cik}/financials?source=live", timeout=60))
    gaap = json.load(open(cache / f"{hashlib.sha256(url.encode()).hexdigest()}.json"))["body"]["facts"]["us-gaap"]
    print(cik, fin["source"]["label"], [p["fiscal_year_label"] for p in fin["periods"]][-1], len(fin["periods"]), "periods")
    lines = {line["metric_id"]: line for s in fin["statements"].values() for line in s}
    ratios = {line["metric_id"]: line for line in fin["ratios"]}
    for metric, concepts, instant in [*[(k, v, False) for k, v in DUR.items()], *[(k, v, True) for k, v in INST.items()]]:
        for mv in lines[metric]["values"]:
            raw = pick(gaap, concepts, mv["period_end"], instant)
            expected = None if raw is None else raw["val"]
            if mv["value"] != expected:
                bad += 1
                print("  MISMATCH", metric, mv["fiscal_year_label"], mv["value"], expected)
    latest = len(fin["periods"]) - 1
    cf = lines["operating_cash_flow"]["values"][latest]["value"]
    capex = lines["capex"]["values"][latest]["value"]
    fcf = lines["fcf"]["values"][latest]
    if cf is not None and capex is not None and fcf["value"] != cf - capex:
        bad += 1
        print("  MISMATCH fcf")
    rev = lines["revenue"]["values"][latest]["value"]
    ni = lines["net_income"]["values"][latest]["value"]
    nm = ratios["net_margin"]["values"][latest]["value"]
    if abs(nm - ni / rev) > 1e-9:
        bad += 1
        print("  MISMATCH net margin")
    print("  latest:", "revenue", rev, "net income", ni, "fcf", fcf["value"], "capex concept",
          (lines["capex"]["values"][latest]["provenance"] or {}).get("concept"),
          "D/E", ratios["debt_to_equity"]["values"][latest]["value"], ratios["debt_to_equity"]["values"][latest]["status"])
print("mismatches:", bad)
sys.exit(1 if bad else 0)
