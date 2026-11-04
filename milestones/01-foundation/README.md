# M1 Foundation

**What it delivers.** SEC Analytics starts with a dark, terminal-style shell; keyboard search (`/` or Ctrl/Cmd-K) by name, ticker or CIK over the three demo companies (Apple, Microsoft, Alphabet); a company profile with its SEC identifiers; and a small dashboard of annual revenue and net income built from authentic recorded SEC data, labelled `RECORDED SEC DEMO · snapshot <date>`, with the source of every number on hover. It also adds the example's own rules for assistants (`examples/sec-analytics/CLAUDE.md`), a nested `sec-edgar-data` skill and the fixture builder with its manifest.

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

**Added.** Dark terminal shell, keyboard search by name, ticker or CIK over three demo companies, company profile, key
figures, annual revenue and net income chart with a data table, source tooltips, and offline, no-match and error states.
Authentic SEC fixtures retrieved on 2026-11-03 (live SEC: 7 requests) with a manifest.

**Checked.** `npm run verify` (backend lint and tests, frontend lint, typecheck, unit tests, build, Playwright journeys at
1440, 1366 and 390 px) and visual inspection of the screenshots. The commit and exact results are in `PROGRESS.md`.

**Limitations.** Recorded data for three companies only; annual revenue and net income only; no live data. The planned
independent reviews were replaced by a same-session review at the owner's request. Windows and Cline are untested. Tables wider than a
phone scroll inside their own box.
