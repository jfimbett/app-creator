# M2 Financial intelligence

**What it delivers.** On top of the earlier milestones, SEC Analytics adds backend SEC adapters with a fair-access client (declared contact, 1 request per second, cache, Retry-After); an explicit Demo/Live choice under `npm run dev`; annual income statement, balance sheet and cash-flow summaries for 5–10 years; a metric explorer with charts; ratios (margins, FCF, debt-to-equity, ROE, ROA) whose formulas and inputs show on hover; and missing data shown as missing, never as zero.

## Inspect it at its tag

From a clean checkout (stop any running `npm run dev` or `npm run demo` and check `git status` first):

```bash
git fetch origin --tags
git switch --detach m2
npm ci
npm run setup
npm run demo
```

Open http://127.0.0.1:3000. Open Apple, hover a revenue cell to see concept, period, form and accession, then hover a ratio to see its formula. In the explorer pick net margin and FCF. `npm run demo` needs no keys and no network. The tag also has a branch,
`milestone/02-financial-intelligence`.

## Rebuild it (exercise)

Start from the previous milestone's tag, `m1`, on a new branch, and give the assistant [PROMPT.md](PROMPT.md):

```bash
git switch -c exercise/build-m2 m1
```

The `m2` checkout is for inspection, not for re-running its own prompt. Your result will differ from `m2`:
replaying a prompt does not reproduce the same code. The tag is the reference version.

## Files

- [PROMPT.md](PROMPT.md): the exact build brief used for this milestone (unchanged after `template-v1`).
- [FOLLOWUPS.md](FOLLOWUPS.md): any implementation-changing follow-up prompts, saved before they were sent.
- Shared planning: [product](../product.md), [architecture](../architecture.md), [acceptance](../acceptance.md),
  [plan](../plan.md).

## Results

**Added.** Backend SEC adapters with a disk cache, throttling and de-duplication; a Demo / Live selector under `npm run dev`; live
lookup by name, ticker or CIK; normalized annual income, balance-sheet and cash-flow summaries for 5 to 10 years; growth, margin,
leverage and return ratios; a selectable metric explorer; reported or derived labels; provenance and formula tooltips; explicit
missing, unavailable and n/m states.

**Checked.** `npm run verify` offline, plus a separate live smoke check, live browser journey and cross-check against raw SEC data
on real companies. The commit and exact results are in `PROGRESS.md`.

**Limitations.** Summaries are not the complete filed statements. Some concepts are unmapped and show as missing, such as Microsoft's
and Alphabet's D&A. Foreign 20-F filers have no statements. Values may reflect later restatements. No independent review was run; Windows, Cline and CI
are untested. On a phone, a tooltip's Source link needs a tap; by keyboard, use the SEC source links under the tables.
