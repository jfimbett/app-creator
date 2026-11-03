# M1 Foundation

**What it delivers.** On top of the earlier milestones, SEC Analytics adds a dark, terminal-style shell; keyboard search (`/` or Ctrl/Cmd-K) by name, ticker or CIK over the three demo companies (Apple, Microsoft, Alphabet); a company profile with its SEC identifiers; and a small dashboard of annual revenue and net income built from authentic recorded SEC data, labelled `RECORDED SEC DEMO · snapshot <date>`, with the source of every number on hover. It also adds the example's own rules for assistants (`examples/sec-analytics/CLAUDE.md`), a nested `sec-edgar-data` skill and the fixture builder with its manifest.

## Inspect it at its tag

From a clean checkout (stop any running `npm run dev` or `npm run demo` and check `git status` first):

```bash
git fetch origin --tags
git switch --detach m1
npm ci
npm run setup
npm run demo
```

Open http://127.0.0.1:3000. Press `/`, type `aapl`, press ↓ and Enter. Hover a key figure to see its SEC concept and accession. Search `tesla` to see the limited demo universe. `npm run demo` needs no keys and no network. The tag also has a branch,
`milestone/01-foundation`.

## Rebuild it (exercise)

Start from the previous milestone's tag, `template-v1`, on a new branch, and give the assistant [PROMPT.md](PROMPT.md):

```bash
git switch -c exercise/build-m1 template-v1
```

The `m1` checkout is for inspection, not for re-running its own prompt. Your result will differ from `m1`:
replaying a prompt does not reproduce the same code. The tag is the reference version.

## Files

- [PROMPT.md](PROMPT.md): the exact build brief used for this milestone (unchanged after `template-v1`).
- [FOLLOWUPS.md](FOLLOWUPS.md): any implementation-changing follow-up prompts, saved before they were sent.
- Shared planning: [product](../product.md), [architecture](../architecture.md), [acceptance](../acceptance.md),
  [plan](../plan.md).

## Results

Filled in after the checkpoint.
