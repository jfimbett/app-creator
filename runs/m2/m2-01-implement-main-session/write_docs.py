#!/usr/bin/env python3
"""M2 documents: settings, setup guide, policy, statuses, decisions and follow-ups. Run from the repo root.

Statuses marked passing are confirmed by the clean-worktree gate before any tag is created.
"""
import re


def sub(path, pairs):
    s = open(path).read()
    for old, new in pairs:
        assert old in s, (path, old[:70])
        s = s.replace(old, new, 1)
    open(path, "w").write(s)


sub(".env.example", [
    ('''# Where the backend reads its data. Only "fixtures" (recorded SEC data, offline) exists at milestone M1.
# DATA_MODE=fixtures
''', '''# Where the backend reads its data: "fixtures" (recorded SEC data, offline) or "live" (the Demo/Live selector is
# offered). The root commands set it: npm run demo uses fixtures, npm run dev uses live.
# DATA_MODE=fixtures
'''),
    ('''# Your app name and your own contact email, e.g. `<app name> <your contact email>`.
# Needed only to capture fixtures (and for live mode from M2). Never commit it.
# SEC_USER_AGENT=
''', '''# A descriptive name plus your own contact email: `<app name> <your contact email>`. SEC requires this to identify
# automated requests. Each student uses their own. Needed for live mode and fixture capture. Never commit it.
# SEC_USER_AGENT=

# Disk cache for SEC responses, kept 24 hours. Empty means examples/sec-analytics/backend/.cache/sec (git-ignored).
# SEC_CACHE_DIR=

# Requests per second to SEC from this running app. Default 1; values above 5 are refused. SEC's limit of 10 per
# second is for all machines together, so a class on one public IP address should use Demo.
# SEC_MAX_REQUESTS_PER_SECOND=1
'''),
])

open("docs/SETUP.md", "w").write("""# Setup

The commands below were run on macOS (Node 22.14, Python 3.10.16) on 2026-11-04. Windows is untested.

## Install and run (from the repository root)

```bash
npm ci           # once: the launcher's lockfile
npm run setup    # backend and frontend packages, project-local browser
npm run demo     # offline demo on recorded data: http://127.0.0.1:3000
npm run dev      # the same app with the Demo / Live selector
npm run verify   # every offline check
```

Ports 3000 and 8000 are refused if something else uses them. Choose others:

```bash
FRONTEND_PORT=3200 BACKEND_PORT=8200 npm run dev   # then open http://127.0.0.1:3200
```

## SEC Analytics: live SEC mode

`npm run demo` never contacts SEC. `npm run dev` offers a **Data source** selector in the header that starts on Demo.
Choosing **Live** sends requests to SEC through this app's backend; the browser only talks to your own machine.

**Set your contact first.** SEC asks automated clients to identify themselves. Create a `.env` file in the repository
root (it is git-ignored, so it is never committed) with one line:

```text
SEC_USER_AGENT=<a descriptive name> <your own contact email>
```

Each person uses their own email. Without this line, Live shows "Live SEC data is not configured" and Demo keeps working.
Restart `npm run dev` after changing the file.

**What the app does to be a good SEC citizen.** At most 1 request per second from one running app, one at a time, a 20-second
timeout, waiting when SEC asks with `Retry-After` (up to 30 seconds, two retries), and no retry after a refusal (403).
Answers are kept on disk for 24 hours (`examples/sec-analytics/backend/.cache/sec`, git-ignored) and labelled `CACHED`.
Identical requests made at the same moment share one call. Nothing is fetched in the background.

**In a classroom,** SEC's limit of 10 requests per second applies to everyone behind one public IP address. Use Demo, or
have one person use Live on a screen, rather than every student fetching at once.

**If Live fails,** the app says what happened and offers "Use recorded demo data". It never switches to demo data by itself.

**Check your live setup by hand** (3 requests; prints PASS or FAIL per check; never prints your contact):

```bash
cd examples/sec-analytics/backend
.venv/bin/python scripts/live_sec_smoke.py     # Windows (untested): .venv\\Scripts\\python scripts\\live_sec_smoke.py
```

A browser journey through live mode is also run by hand, with `npm run dev` already running:

```bash
cd examples/sec-analytics/frontend
BASE_URL=http://127.0.0.1:3000 PLAYWRIGHT_BROWSERS_PATH=../../../.cache/ms-playwright \\
  npx playwright test --config playwright.live.config.ts
```

## Troubleshooting

| What you see | What to do |
|---|---|
| "port is in use" | Something else holds it; the launcher never stops it. Set `FRONTEND_PORT` and `BACKEND_PORT`. |
| "Live SEC data is not configured" | Add `SEC_USER_AGENT` to the root `.env` as above, then restart. It needs a name and an email. |
| "SEC refused the request (403)" | Check your contact line. The app does not retry; try later. |
| "SEC is limiting requests" | Wait the time shown. On shared networks, use Demo. |
| "No annual 10-K revenue…" | The filer has no annual 10-K revenue in a currency, for example a foreign filer using form 20-F. |
| Python not found or too old | Install Python 3.10 to 3.13, or set `APP_PYTHON` to its full path in the root `.env`. |
""")


s = open("docs/README.md").read()
s = re.sub(r"- `SETUP\.md`:[^\n]*(\n  [^\n]*)*", "- [SETUP.md](SETUP.md): tested install and run commands, offline and live modes, the SEC contact, troubleshooting.", s, count=1)
open("docs/README.md", "w").write(s)

sub("examples/sec-analytics/CLAUDE.md", [
    ('''`/api/*`. All SEC traffic goes through `backend/app/clients/sec.py`. At M1 only the capture script uses it; the
   running app makes no SEC request.
''', '''`/api/*`. All SEC traffic goes through `backend/app/clients/sec.py`. The running app uses it only when a request
   says `source=live`, through `backend/app/data/source.py`, which also holds the disk cache (24 h) and single flight.
   A live failure is an error shown to the person, never replaced by fixtures.
'''),
    ('''5. **Concepts:** revenue uses, per period, the first present of `Revenues`,
   `RevenueFromContractWithCustomerExcludingAssessedTax`, `SalesRevenueNet`,
   `RevenueFromContractWithCustomerIncludingAssessedTax`; net income is `NetIncomeLoss`. The list lives in
   `backend/app/logic/concepts.py`; a new mapping is verified against the fixtures before use.
''', '''5. **Concepts:** every list in `backend/app/logic/concepts.py` is a priority order for one period: the first present
   wins, and alternates are never summed. Revenue: `Revenues`, `RevenueFromContractWithCustomerExcludingAssessedTax`,
   `SalesRevenueNet`, `RevenueFromContractWithCustomerIncludingAssessedTax`. Interest: `InterestExpense`,
   `InterestExpenseNonoperating`, `InterestExpenseDebt`. D&A: `DepreciationDepletionAndAmortization`,
   `DepreciationAndAmortization`, `DepreciationAmortizationAndAccretionNet`. Capex:
   `PaymentsToAcquirePropertyPlantAndEquipment`, `PaymentsToAcquireProductiveAssets`. Short-term debt: `CommercialPaper`,
   else `ShortTermBorrowings`. A new mapping is verified against the fixtures or a named live filing before use.
   **Checked 2026-11-04:** Microsoft and Alphabet report none of the D&A concepts, and Apple has no interest concept after
   FY2023, so those lines show as missing and EBITDA or EBIT as unavailable. `PaymentsToAcquireProductiveAssets` was checked on
   live NVIDIA data and is outside `CAPTURE_CONCEPTS`, so the fixtures do not contain it.
'''),
    ('''9. Labels: `FY<year of end date>`, always shown with the end date. Statement views carry "Values may reflect later
   restatements; not point-in-time."
''', '''9. Labels: `FY<year of end date>`, always shown with the end date. Statement views carry "Values may reflect later
   restatements; not point-in-time." and are titled as a normalized summary, not the complete filed statement.
10. **Formulas** are in `backend/app/logic/metrics.py`, and a value that would mislead is not computed. A prior year counts
    only if it ended about a year earlier. **Debt** sums the components reported at that date and is `unavailable` when no
    long-term component is reported, because a short-term line alone would understate debt, possibly as zero. **Negative
    equity:** ROE and debt-to-equity do not measure return or leverage in the usual way, so they show
    `n/m (negative equity)` with the inputs in the tooltip. EBIT is never replaced by operating income.
11. **Key figures** use the latest period, or say why not; only revenue and net income fall back to the latest reported
    value, dated. An old value next to the latest figures would look current.
'''),
])

s = open("examples/sec-analytics/README.md").read()
s = s.replace("At milestone M1 it runs offline only, on recorded SEC data.", "It runs on recorded SEC data offline, and on live SEC data when you choose.")
a = s.index("## What M1 does")
b = s.index("## Run it")
s = s[:a] + """## What it does

Search by name, ticker or CIK; a company profile; key figures; an annual revenue and net income chart; **normalized annual
summaries** of the income statement, balance sheet and cash flow; ratios; and a metric explorer. Hovering or focusing a value
shows the SEC fact it came from, or its formula and inputs. A value that is not available says so and why; it is never 0.

These summaries are built from SEC Company Facts. They are not the complete filed statements. Metric ids, concepts and
formulas are in `backend/app/logic/concepts.py` and `metrics.py`; the selection policy is in `logic/periods.py`.

**Demo and Live.** `npm run demo` is offline, on Apple, Microsoft and Alphabet only: any other company gives "No match in the
demo universe (3 companies)". `npm run dev` adds a Demo / Live selector that starts on Demo. Live search covers SEC filers
listed in the SEC ticker file, and other filers can be opened by CIK. It does not cover non-SEC companies. Setup, your contact
setting and the smoke check are in [docs/SETUP.md](../../docs/SETUP.md).

""" + s[b:]
s = s.replace("npm run demo     # offline demo on recorded data: http://127.0.0.1:3000\n", "npm run demo     # offline demo on recorded data: http://127.0.0.1:3000\nnpm run dev      # the same, with the Demo / Live selector\n")
s = s.replace("**Classroom note.** SEC's fair-access limit applies across everyone sharing one public address, so a class uses the\nrecorded data. Do not have every student recapture.", "**Classroom note.** SEC's fair-access limit applies across everyone sharing one public address, so a class uses Demo by\ndefault. Do not have every student recapture or use Live at once.")
open("examples/sec-analytics/README.md", "w").write(s)

ST = {
 "M2-AC1": "passing (test: tests/test_api_m2.py::test_m2_ac1_live_search_uses_the_ticker_file_and_is_labelled_live); live: e2e-live/live-sec.spec.ts, by hand 2026-11-04",
 "M2-AC2": "passing (test: tests/test_api_m2.py::test_m2_ac2_live_without_the_setting_names_it; e2e/m2-financials.spec.ts mocked backend)",
 "M2-AC3": "passing (test: tests/test_api_m2.py::test_m2_ac3_sec_failure_is_reported_and_never_replaced_by_demo_data; e2e mocked backend)",
 "M2-AC4": "passing (test: tests/test_api_m2.py::test_m2_ac4_financials_for_apple_in_demo; e2e/m2-financials.spec.ts)",
 "M2-AC5": "passing (e2e/m2-financials.spec.ts explorer tests); looked at 2026-11-04 by assistant",
 "M2-AC6": "passing (test: tests/test_api_m2.py::test_m2_ac6_reported_value_has_full_provenance; e2e/m2-financials.spec.ts tooltips)",
 "M2-AC7": "passing (test: tests/test_metrics_known_answers.py)",
 "M2-AC8": "passing (test: tests/test_api_m2.py::test_m2_ac8_period_without_revenue_over_a_mocked_sec; components/ValueCell.test.tsx)",
 "M2-AC9": "passing (test: tests/test_sec_client_m2.py::test_m2_ac9_five_identical_requests_make_one_sec_call_and_then_the_cache_answers)",
}
for i in range(1, 14):
    target = "tests/test_sec_client_m2.py" if i in (12, 13) else "tests/test_metrics_edges.py" if i in (8, 9, 10) else "tests/test_periods_m2.py"
    ST[f"M2-E{i}"] = f"passing (test: {target})"
for i in range(1, 11):
    ST[f"CALC{i}"] = "passing (test: tests/test_metrics_known_answers.py)"
for i in range(5, 16):
    ST[f"FX{i}"] = "passing (test: tests/test_metrics_known_answers.py)"
lines = open("milestones/acceptance.md").read().split("\n")
done = set()
for i, line in enumerate(lines):
    m = re.match(r"\| (M2-AC\d|M2-E\d+|CALC\d+|FX\d+) \|", line)
    if m and m.group(1) in ST and line.rstrip().endswith("| open |"):
        lines[i] = line.rstrip()[: -len("open |")] + ST[m.group(1)] + " |"
        done.add(m.group(1))
assert done == set(ST), set(ST) - done
s = "\n".join(lines)
s = s.replace("M1 criteria were updated on 2026-11-04; later milestones are `open`.", "M1 and M2 criteria were updated on 2026-11-04; later milestones are `open`.")
s = s.replace("The owner's own look is pending.\n", "The owner's own look is pending.\n\nM2 visual check, 2026-11-04, assistant: Apple page, income statement, ratios and explorer at 1440, 1366 and 390 px, and live NVIDIA at 1440 px. Three layout defects seen at those checks were fixed (see `milestones/plan.md`). The owner's own look is pending.\n", 1)
open("milestones/acceptance.md", "w").write(s)

s = open("milestones/plan.md").read()
s, n = re.subn(r"^(\| 2\.[1-6] \|.*\| )todo( \|)$", r"\1done (2026-11-04)\2", s, flags=re.M)
assert n == 6, n
s = s.replace("| 2026-11-04 | 1.5–1.6 |", "| 2026-11-04 | 2.1–2.6 | SEC adapters, cache, normalized statements, ratios, explorer, Demo/Live selector (runs/m2) | see the m2-01 record | independent reviews not run |\n| 2026-11-04 | 1.5–1.6 |", 1)
s = s.replace("- **N2** Resolved for the fixture capture (2026-11-03, owner's contact passed through the process environment only). Live checks in later\n  milestones still need the owner's `SEC_USER_AGENT`.",
 "- **N2** Resolved: on 2026-11-04 the owner asked for a root `.env` with their contact (git-ignored). Students use their own.")
s = s.replace("- The M1 concept mapping and fiscal-year labels are checked against the fixtures (FX1–FX4). Concepts added in slice 2.2 are not yet.\n",
 """- The concept mapping is checked against the fixtures (FX1–FX15) and, for capex, live NVIDIA data.
- **Found by testing real companies on live data, fixed with tests (2026-11-04):** debt-to-equity of 0.00× from a reported zero short-term
  line (NVIDIA FY2019); a key figure taken from 14 years earlier (NVIDIA FCF from FY2012); capex under an unmapped concept; a 500 error
  for a filer with no annual 10-K (TSMC, form 20-F). The fixtures could not have shown these.
- **Known mapping gaps, shown as missing or unavailable:** Microsoft and Alphabet D&A and EBITDA; Apple interest expense and EBIT after
  FY2023; a filer whose long-term debt uses other concepts, such as NVIDIA before FY2020; banks' working capital, capex and FCF.
- Companies with no annual 10-K revenue (foreign 20-F filers) get an explanation, not statements.
""")
s = s.replace("- M1 was reviewed only in the same session", "- M1 and M2 were reviewed only in the same session")
s = s.replace("replaced at the owner's request (2026-11-04).", "replaced at the owner's request (2026-11-04); M2 used adversarial live checks and read-only checks instead.")
open("milestones/plan.md", "w").write(s)

ROWS = [
 ("`[verify against fixtures]` for concepts resolved. Interest alternates: `InterestExpenseNonoperating`, then `InterestExpenseDebt`. D&A: the listed concepts only", "fixture check `runs/m2/m2-01-implement-main-session/fixture_concepts.py`: Microsoft and Alphabet report no listed D&A concept, Apple no interest concept after FY2023; shown as missing, never substituted", "brief §6"),
 ("`sec_refused` (502) added to the API; `sec_rate_limited` (503) when SEC keeps answering 429, or 503 with `Retry-After`; a bare 503 stays `sec_unavailable` (502)", "the brief's §7 and §9 treat 503 differently; this satisfies both and keeps an outage distinct from limiting", "routine choice; brief §5, §7, §9"),
 ("The SEC client stays synchronous, not async as the brief's table says; FastAPI runs the endpoints in a thread pool, and one lock plus a per-URL `Future` give one request in flight and single flight", "the behaviour is what the brief requires, and the tested M1 client is reused", "deviation, recorded; brief §5"),
 ("Capex alternate `PaymentsToAcquireProductiveAssets`, after PP&E", "real concept alternative: NVIDIA reports capex only this way. Verified on live data, not in the fixtures. May include intangibles, so the concept is always shown", "owner's M2 instruction (concept alternatives); deviation from brief §6's fixtures-only check"),
 ("Debt is `unavailable` (\"no long-term debt concept reported\") when only a short-term component is reported", "stricter than the brief's sum: a reported zero commercial paper line produced total debt 0 and D/E 0.00× for NVIDIA FY2019", "found on live data"),
 ("Derived key figures and cash flow use the latest period, or say why not; revenue and net income keep M1's latest reported value", "NVIDIA's FCF from FY2012 appeared beside FY2026 figures", "found on live data"),
 ("Non-revenue lines match a period by end date among annual durations, not by exact start date", "a filer can report one year with a slightly different start; `select_periods` already keeps one period per end date", "routine choice; brief §7"),
 ("Growth, ROE and ROA use a prior period only if it ended 350 to 380 days earlier", "with a year missing, a two-year change must not read as annual growth", "routine choice"),
 ("A missing prior year is `prior year missing` for the first period; the shown range does not limit the look-back", "the first shown year still has its real prior year", "routine choice"),
 ("Years selector is radio buttons; the statement tables open scrolled to the newest year", "a `<select>` is a second combobox on the page, and the newest year was off-screen", "routine choice"),
 ("A live-mode CIK not in the ticker file returns one result, \"Not in the SEC ticker file: open by CIK\"", "brief §3: such filers can still be opened", "routine choice"),
 ("Root `.env` holds the owner's `SEC_USER_AGENT` on this machine", "owner's instruction, 2026-11-04; git-ignored, permissions 600, value not recorded", "owner"),
]
s = open("milestones/architecture.md").read().rstrip("\n")
s = s.replace("**Concept mapping** (proposed; `[verify against fixtures]`):", "**Concept mapping** (verified 2026-11-04, see the decision log; `examples/sec-analytics/CLAUDE.md` has the current lists):", 1)
s = s.replace("  `[verify against fixtures]`).", "  verified 2026-11-04).", 1)
s += "\n" + "\n".join(f"| 2026-11-04 | {a} | {b} | {c} |" for a, b, c in ROWS) + "\n"
open("milestones/architecture.md", "w").write(s)

s = open("AI-USAGE.md").read().rstrip("\n")
s += ("\n| 2026-11-04 | owner (instructor) | M2: Claude Code (Opus 5.5) built live SEC lookup, normalized statements, ratios and the metric explorer in the main session. "
      "Mistakes caught by testing real companies on live data: total debt of 0 and D/E of 0.00× from a lone zero short-term line; a 14-year-old FCF as a key figure; capex under an unmapped concept; a 500 for a 20-F filer | "
      "pytest, Vitest and Playwright; hand-worked CALC and FX answers; a live cross-check against raw SEC JSON using no app code; screenshots. Review in the same session, not independent | accepted, with the corrections listed |\n")
open("AI-USAGE.md", "w").write(s)


def between(path):
    t = open(path).read()
    return re.search(r"<!-- DISPATCH:BEGIN -->\n(.*?)\n<!-- DISPATCH:END -->", t, re.S).group(1)


p = "milestones/02-financial-intelligence/FOLLOWUPS.md"
s = open(p).read().replace("No follow-ups yet.\n", "")
quoted = "\n".join(("> " + l).rstrip() for l in between("runs/m2/m2-01-implement-main-session/PROMPT.md").split("\n"))
s = s.rstrip("\n") + f"""

## 2026-11-04, instructor → top-level session, runs/m2/m2-01-implement-main-session

Saved before work began. M2 ran in the main session under this instruction; the brief in [PROMPT.md](PROMPT.md) was read and followed
directly, not dispatched to a builder.

{quoted}

## 2026-11-04, instructor's answer in chat → top-level session

The owner was asked how M2 should get `SEC_USER_AGENT`. Exact answer, saved after it was received:

> create an .env file and for now use my mail acount i will tell students to use their own email there

The address itself is not recorded here.
"""
open(p, "w").write(s)

p = "milestones/02-financial-intelligence/README.md"
s = open(p).read()
assert "Filled in after the checkpoint." in s
s = s.replace("Filled in after the checkpoint.", """**Added.** Backend SEC adapters with a disk cache, throttling and de-duplication; a Demo / Live selector under `npm run dev`; live
lookup by name, ticker or CIK; normalized annual income, balance-sheet and cash-flow summaries for 5 to 10 years; growth, margin,
leverage and return ratios; a selectable metric explorer; reported or derived labels; provenance and formula tooltips; explicit
missing, unavailable and n/m states.

**Checked.** `npm run verify` offline, plus a separate live smoke check, live browser journey and cross-check against raw SEC data
on real companies. The commit and exact results are in `PROGRESS.md`.

**Limitations.** Summaries are not the complete filed statements. Some concepts are unmapped and show as missing, such as Microsoft's
and Alphabet's D&A. Foreign 20-F filers have no statements. Values may reflect later restatements. No independent review was run; Windows, Cline and CI
are untested. On a phone, a tooltip's Source link needs a tap; by keyboard, use the SEC source links under the tables.""")
open(p, "w").write(s)
print("ok")
