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

Filled in after the checkpoint.
