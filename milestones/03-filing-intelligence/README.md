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

**Added.** A Filings tab for each company: the latest 10-K and 10-Q (labelled `Latest in snapshot (as of <date>)` in demo,
`Latest on EDGAR (retrieved …)` in live mode), a 10-year history of 10-K, 10-Q and their amendments with form, filing date,
period and accession, and filters for annual, quarterly and amendments. An amendment never replaces the original as "latest";
both link to each other. A reader shows the filing's own text, sanitized on the server into plain text blocks, with automatically
detected Item sections (a rail on desktop, a select on a phone), a labelled full-text fallback when no sections are found, text
search with highlighted matches, a count and next/previous, and links to the exact document and filing index on sec.gov. Demo
mode carries the unmodified latest 10-K and 10-Q of Apple, Microsoft and Alphabet; other filings link to sec.gov only.

**Checked.** `npm run verify` offline (pytest, Vitest, lint, types, production build, Playwright including the six M3 journeys
in `frontend/e2e/m3-filings.spec.ts` at 1440 and 390 px), screenshots looked at, one live retrieval (NVIDIA's filing list and
latest 10-K read and searched in the browser) and independent security and test reviews, whose findings were fixed (bounded
nested-table parsing, download time and unzip limits, stronger tests). Exact results:
[runs/m3/m3-04-finish-main-session/RESULT.json](../../runs/m3/m3-04-finish-main-session/RESULT.json).

**Limitations.** Section detection is a heuristic over Item headings; it is labelled "may be imperfect". Exhibits are not shown,
only the primary document. Very long documents are cut at a block limit with a link to the rest on sec.gov. Demo mode has
documents for six filings only. Older filings (before about 2001) may be plain text with no sections.
