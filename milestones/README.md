# SEC Analytics milestones

SEC Analytics is App Creator's worked example. It is a dark, terminal-style web app that reads public SEC EDGAR data
for US companies. It shows financial statements, ratios, filings, comparisons and, optionally, an AI analyst that
cites its sources. It is built in **five cumulative, student-facing releases**. Each release keeps everything the
earlier ones did and works on its own checkout, with `npm run demo` offline.

| Milestone | Folder | Adds | Starts from | Result tag |
|---|---|---|---|---|
| 01 Foundation | `milestones/01-foundation/` | dark shell, keyboard search over the 3 demo companies, profile, labelled demo dashboard | `template-v1` | `m1` |
| 02 Financial intelligence | `milestones/02-financial-intelligence/` | backend SEC adapters, live lookup, 5–10 years of statements, metric explorer, ratios with provenance, explicit missing data | `m1` | `m2` |
| 03 Filing intelligence | `milestones/03-filing-intelligence/` | latest 10-K/10-Q, history with amendment labels, sanitized reader with sections and search | `m2` | `m3` |
| 04 Comparative analysis | `milestones/04-comparative-analysis/` | compare 2–4 companies, labelled indexing, CSV export | `m3` | `m4` |
| 05 AI analyst | `milestones/05-ai-financial-analyst/` | optional OpenRouter analyst grounded in app data, with validated source references | `m4` | `m5` |

Ref chain: `template-v1` → `m1` → `m2` → `m3` → `m4` → `m5`. Each tag also has a branch (`template`,
`milestone/01-foundation`, … `milestone/05-ai-financial-analyst`). Each milestone folder holds its build brief
(`PROMPT.md`), its follow-up prompts (`FOLLOWUPS.md`) and a README.

## Shared planning documents

All five milestones are planned in four documents, agreed on 2026-11-03 under the instructor's delegation:

- [product.md](product.md): who it is for, the journey, screens, features per milestone, what is out of scope
- [architecture.md](architecture.md): parts, data modes and labels, API per milestone, SEC and OpenRouter boundaries,
  financial data rules
- [acceptance.md](acceptance.md): checkable criteria per milestone (`M1-AC1` …), worked calculations, edge cases
- [plan.md](plan.md): the slices of each milestone, with owners, criteria and skills
- Decisions behind them: [docs/PRODUCT-DECISIONS.md](../docs/PRODUCT-DECISIONS.md)

## Two ways to use a milestone

- **Inspect it (the main path in class).** Check out a tag, for example `git switch --detach m2`, then run
  `npm run setup` and `npm run demo`. A completed checkout is **for inspection**: do not run its own `PROMPT.md`
  on it, because that work is already done there.
- **Rebuild a transition (exercise).** Start from the *previous* tag on a new branch, for example
  `git switch -c exercise/build-m2 m1`, then give the assistant `milestones/02-financial-intelligence/PROMPT.md`.
  Your result will differ from `m2`: replaying a prompt does not reproduce the same code. The tags are the reference
  versions.

Before switching versions, stop running services and check `git status` so you do not lose your own edits. Then run
`npm run setup` again, because dependencies may change between milestones.
