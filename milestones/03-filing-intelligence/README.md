# M3 Filing intelligence

**What it delivers.** On top of the earlier milestones, SEC Analytics adds a Filings tab with the latest 10-K and 10-Q (`Latest in snapshot (as of <date>)` in demo), a 10-year history with amendment labels, and a reader that shows the actual filing text, sanitized on the server, with automatically detected sections, text search and a link to the source document on sec.gov.

## Inspect it at its tag

From a clean checkout (stop any running `npm run dev` or `npm run demo` and check `git status` first):

```bash
git fetch origin --tags
git switch --detach m3
npm ci
npm run setup
npm run demo
```

Open http://127.0.0.1:3000. Open Apple → Filings → Read the latest 10-K, click Item 7, search for `revenue`, then open Source. `npm run demo` needs no keys and no network. The tag also has a branch,
`milestone/03-filing-intelligence`.

## Rebuild it (exercise)

Start from the previous milestone's tag, `m2`, on a new branch, and give the assistant [PROMPT.md](PROMPT.md):

```bash
git switch -c exercise/build-m3 m2
```

The `m3` checkout is for inspection, not for re-running its own prompt. Your result will differ from `m3`:
replaying a prompt does not reproduce the same code. The tag is the reference version.

## Files

- [PROMPT.md](PROMPT.md): the exact build brief used for this milestone (unchanged after `template-v1`).
- [FOLLOWUPS.md](FOLLOWUPS.md): any implementation-changing follow-up prompts, saved before they were sent.
- Shared planning: [product](../product.md), [architecture](../architecture.md), [acceptance](../acceptance.md),
  [plan](../plan.md).

## Results

Filled in after the checkpoint.
