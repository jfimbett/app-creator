# PROMPT — B14-review-milestone-prompts

- Sender: owner (top-level Claude Code session)
- Receiver: project-orchestrator (read-only judge)
- Starting commit at prompt write: 49dd630 (RESULT.json records the commit at dispatch)
- Skills to load: orchestrate-steps (judge side)
- Key instruction/reference files (sha256 prefix when written):
  - docs/TOOLKIT.md 72165a1d6238722a
  - GOAL.md 20b3a7b8e8c2aa44
  - milestones/01-foundation/PROMPT.md 41cb350fb8ae472a
  - milestones/02-financial-intelligence/PROMPT.md 6cbed727ffed9fe2
  - milestones/03-filing-intelligence/PROMPT.md 7f135930c6d6e6e4
  - milestones/04-comparative-analysis/PROMPT.md 47af2b5062577555
  - milestones/05-ai-financial-analyst/PROMPT.md 38a7b36eeb9dbe1d
- Dispatch: `node scripts/dispatch-step.mjs --step runs/bootstrap/B14-review-milestone-prompts --agent project-orchestrator --mode bypassPermissions --milestone bootstrap`

<!-- DISPATCH:BEGIN -->
Task B14: review the five milestone build prompts before they become immutable at `template-v1`. Read GOAL.md completely, docs/PRODUCT-DECISIONS.md, milestones/*.md, and each milestones/0*/PROMPT.md. Judge each prompt against GOAL.md §4–§9 and the required sections (starting ref; context; new work; design; architecture/files with endpoint shapes; fixtures/data; SEC rules applicable; no-interview defaults; tests and verification gate; acceptance criteria; out of scope; handoff). Look specifically for: wrong starting refs; later-milestone features leaking into earlier ones (e.g. live search or ratios in M1, filings in M2, comparisons before M4, AI before M5); missing GOAL requirements at the milestone where they belong (M1 fixture-universe explanation and browser smoke test; M2 duration/instant, restatement policy, ratio formulas, missing=null, provenance tooltips; M3 sanitization, TOC-repeat handling, amendment labels, fallback; M4 fiscal dates/units, normalization labelling, CSV; M5 key handling, citations validation, injection tests, caps); contradictions with docs/PRODUCT-DECISIONS.md; any instruction that would make an implementer invent data, an email, or a key; anything that is not self-contained. Do not edit files. Return per prompt: accept or repair, with exact repair instructions (quote the text to change and the replacement), then the decision line and handoff.
Also consider the open items B13 itself reported in runs/bootstrap/B13-milestone-prompts/RESPONSE.md (Handoff) and say how each should be resolved.

End your final message with exactly this block (concise):
## Handoff
Changes: <files created/changed>
Verification evidence: <commands run and exit codes>
Remaining findings: <open issues, doubts>
Next action: <one line>
Do not commit, push, tag or change git configuration; the owner integrates and commits. Never read, create or print .env files or secrets, and never write email addresses into files.
<!-- DISPATCH:END -->
