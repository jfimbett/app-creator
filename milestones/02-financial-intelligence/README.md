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

Filled in after the checkpoint.
