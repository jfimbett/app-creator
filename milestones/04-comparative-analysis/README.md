# M4 Comparative analysis

**What it delivers.** On top of the earlier milestones, SEC Analytics adds a Compare screen for 2–4 companies with selectable revenue, growth, margin, leverage and cash-flow metrics; tables and charts that keep each company's own fiscal year-end, units and currency ("Fiscal years are not aligned"); a labelled "Index = 100 at first common fiscal year" option; and CSV export of exactly the data shown.

## Inspect it at its tag

From a clean checkout (stop any running `npm run dev` or `npm run demo` and check `git status` first):

```bash
git fetch origin --tags
git switch --detach m4
npm ci
npm run setup
npm run demo
```

Open http://127.0.0.1:3000. Compare AAPL, MSFT and GOOGL on revenue and net margin, switch on indexing, then Export CSV and open the file. `npm run demo` needs no keys and no network. The tag also has a branch,
`milestone/04-comparative-analysis`.

## Rebuild it (exercise)

Start from the previous milestone's tag, `m3`, on a new branch, and give the assistant [PROMPT.md](PROMPT.md):

```bash
git switch -c exercise/build-m4 m3
```

The `m4` checkout is for inspection, not for re-running its own prompt. Your result will differ from `m4`:
replaying a prompt does not reproduce the same code. The tag is the reference version.

## Files

- [PROMPT.md](PROMPT.md): the exact build brief used for this milestone (unchanged after `template-v1`).
- [FOLLOWUPS.md](FOLLOWUPS.md): any implementation-changing follow-up prompts, saved before they were sent.
- Shared planning: [product](../product.md), [architecture](../architecture.md), [acceptance](../acceptance.md),
  [plan](../plan.md).

## Results

**Added.** A **Compare** link in the header opens `/compare`. Add 2–4 companies as chips (a fifth is refused with "Compare 2–4
companies"; a repeat is ignored), pick 1–6 metrics and 5–10 years. A table shows one line per company and metric, one column per
fiscal year label, and under every value that company's own period end; the fiscal year-ends are listed and "Fiscal years are
not aligned" appears when they differ. "Index = 100 at first common fiscal year" rebases revenue, operating cash flow and FCF
(labelled `INDEXED`, with the base year and each company's base period end); ratios say "not indexed: ratio". Charts: a trend
line per company and bars for one fiscal year. Different reporting currencies get a warning and no shared money axis. Export CSV
downloads exactly the rows of the table, with provenance. The whole state is in the URL.

**Checked.** `npm run verify` offline (pytest, Vitest, lint, types, build, Playwright including 13 M4 journeys and screenshots at
1440, 1366 and 390 px), the screenshots looked at, a known answer worked by hand (FX16: Apple 208.88, Microsoft 343.62 at base
FY2017) and re-derived by an independent reviewer, a live 4-company comparison (AAPL, MSFT, GOOGL, NVDA), and independent
security and test reviews whose findings were fixed. Exact results:
[runs/m4/m4-01-implement-main-session/RESULT.json](../../runs/m4/m4-01-implement-main-session/RESULT.json).

**Limitations.** Companies are never aligned to calendar years and currencies are never converted, by design. One index base
year serves all selected amount metrics, so adding a metric with a shorter history can move the base later. Offline, only three
companies (all USD) exist, so the fifth-company refusal and the currency warning are shown with mocked data in the tests.
