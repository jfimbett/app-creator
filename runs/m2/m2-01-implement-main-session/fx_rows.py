#!/usr/bin/env python3
"""Add the FX5+ known answers to milestones/acceptance.md. Arithmetic only; imports no app code.

Inputs (USD) are the facts quoted by fx_inputs.py from the fixture JSON. Run once from the repo root.
"""
A, M = "`0000320193-26-000026`", "`0001193125-26-323660`"
a = dict(rev=478834000000, prev=416161000000, ni=132175000000, ocf=145097000000, capex=9041000000,
         ltn=68208000000, ltc=9906000000, cp=1997000000, eq=112093000000, eq0=73733000000,
         assets=404548000000, assets0=359241000000)
m = dict(rev=331839000000, prev=281724000000, ni=133749000000, ocf=182935000000, capex=115948000000,
         ltn=31067000000, ltc=9227000000, eq=442387000000, eq0=343479000000, tax=32185000000,
         intx=3051000000, assets=758376000000, assets0=619003000000)
adebt = a["ltn"] + a["ltc"] + a["cp"]
mdebt = m["ltn"] + m["ltc"]
aeq, meq = (a["eq"] + a["eq0"]) / 2, (m["eq"] + m["eq0"]) / 2
aas, mas = (a["assets"] + a["assets0"]) / 2, (m["assets"] + m["assets0"]) / 2
AP = "2025-09-28 → 2026-09-26"
MP = "2025-07-01 → 2026-06-30"
rows = [
 ("FX5", "Apple net margin, FY2026", f"`NetIncomeLoss` USD {AP} · 10-K · {A} · `val` 132175000000; revenue as FX1",
  "132,175,000,000 ÷ 478,834,000,000", a["ni"] / a["rev"]),
 ("FX6", "Apple FCF, FY2026", f"`NetCashProvidedByUsedInOperatingActivities` USD {AP} · 10-K · {A} · `val` 145097000000; `PaymentsToAcquirePropertyPlantAndEquipment` · same · `val` 9041000000",
  "145,097,000,000 − 9,041,000,000", a["ocf"] - a["capex"]),
 ("FX7", "Apple debt-to-equity, FY2026", f"at 2026-09-26, 10-K, {A}: `LongTermDebtNoncurrent` 68208000000; `LongTermDebtCurrent` 9906000000; `CommercialPaper` 1997000000; `StockholdersEquity` 112093000000",
  "debt = 68,208,000,000 + 9,906,000,000 + 1,997,000,000 = 80,111,000,000; ÷ 112,093,000,000", adebt / a["eq"]),
 ("FX8", "Apple ROE, FY2026", f"`StockholdersEquity` 2026-09-26 112093000000 and 2025-09-27 73733000000, both {A}; net income as FX2",
  "average = (112,093,000,000 + 73,733,000,000) ÷ 2 = 92,913,000,000; 132,175,000,000 ÷ 92,913,000,000", a["ni"] / aeq),
 ("FX9", "Apple revenue growth, FY2026", f"FX1; prior `RevenueFromContractWithCustomerExcludingAssessedTax` USD 2024-09-29 → 2025-09-27 · 10-K · {A} · `val` 416161000000",
  "(478,834,000,000 − 416,161,000,000) ÷ 416,161,000,000", (a["rev"] - a["prev"]) / a["prev"]),
 ("FX10", "Microsoft net margin, FY2026", f"`NetIncomeLoss` USD {MP} · 10-K · {M} · `val` 133749000000; revenue as FX3",
  "133,749,000,000 ÷ 331,839,000,000", m["ni"] / m["rev"]),
 ("FX11", "Microsoft FCF, FY2026", f"`NetCashProvidedByUsedInOperatingActivities` USD {MP} · 10-K · {M} · `val` 182935000000; `PaymentsToAcquirePropertyPlantAndEquipment` · same · `val` 115948000000",
  "182,935,000,000 − 115,948,000,000", m["ocf"] - m["capex"]),
 ("FX12", "Microsoft debt-to-equity, FY2026", f"at 2026-06-30, 10-K, {M}: `LongTermDebtNoncurrent` 31067000000; `LongTermDebtCurrent` 9227000000; `StockholdersEquity` 442387000000; no `CommercialPaper` or `ShortTermBorrowings` fact for that date",
  "debt = 31,067,000,000 + 9,227,000,000 = 40,294,000,000; ÷ 442,387,000,000", mdebt / m["eq"]),
 ("FX13", "Microsoft ROE, FY2026", f"`StockholdersEquity` 2026-06-30 442387000000 ({M}) and 2025-06-30 343479000000; net income as FX4",
  "average = (442,387,000,000 + 343,479,000,000) ÷ 2 = 392,933,000,000; 133,749,000,000 ÷ 392,933,000,000", m["ni"] / meq),
 ("FX14", "Microsoft EBIT, FY2026", f"net income as FX4; `IncomeTaxExpenseBenefit` USD {MP} · {M} · `val` 32185000000; `InterestExpense` absent for this period, so the alternate `InterestExpenseNonoperating` · same · `val` 3051000000",
  "133,749,000,000 + 32,185,000,000 + 3,051,000,000", m["ni"] + m["tax"] + m["intx"]),
 ("FX15", "Apple ROA, FY2026", f"`Assets` 2026-09-26 404548000000 and 2025-09-27 359241000000, both {A}; net income as FX2",
  "average = (404,548,000,000 + 359,241,000,000) ÷ 2 = 381,894,500,000; 132,175,000,000 ÷ 381,894,500,000", a["ni"] / aas),
]
lines = []
for fid, name, quoted, work, val in rows:
    if float(val).is_integer() and abs(val) > 1000:
        shown, tol = f"{int(val):,} USD", "exact"
    else:
        shown, tol = f"{val:.6f}", "± 0.000001"
    lines.append(f"| {fid} | {name} | {quoted} | {work} | {shown} | {tol} | open |")
extra = """
Inputs for FX5–FX15 were read from the fixture JSON by a script that imports no app code
(`runs/m2/m2-01-implement-main-session/fx_inputs.py`), and the arithmetic was done separately
(`fx_rows.py` in the same folder).

**Unavailable by design, from the same fixtures:**

- Apple EBIT and EBITDA, FY2026: no `InterestExpense` fact after FY2023, and the alternates are absent for FY2026, so both are
  `unavailable`. Operating income (158,063 USD millions) is never substituted.
- Microsoft and Alphabet EBITDA, all years: none of the captured D&A concepts appears in their annual 10-K facts, so EBITDA and
  D&A are `unavailable` / `MISSING`. A recapture with another concept would need its own follow-up step.
"""
p = "milestones/acceptance.md"
s = open(p).read()
marker = "\n\nAnnual periods in the snapshot (10-K/10-K/A"
assert marker in s and "| FX5 |" not in s
s = s.replace(marker, "\n" + "\n".join(lines) + "\n" + extra + "\nAnnual periods in the snapshot (10-K/10-K/A", 1)
open(p, "w").write(s)
print("\n".join(l[:6] + " ... " + l.split("|")[5] for l in lines))
