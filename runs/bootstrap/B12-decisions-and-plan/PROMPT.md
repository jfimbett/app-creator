# PROMPT — B12-decisions-and-plan

- Sender: owner (top-level Claude Code session)
- Receiver: product-architect (interviewer role, continuing B10 as a new step)
- Starting commit at prompt write: 14c2d39 (RESULT.json records the commit at dispatch)
- Skills to load: product-interview (Delegated mode), plan-architecture
- Key instruction/reference files (sha256 prefix when written):
  - docs/TOOLKIT.md cde60522bfd2ce4b
  - GOAL.md 20b3a7b8e8c2aa44
  - runs/bootstrap/B10-interview-questions/RESPONSE.md 56e36d99e20752f3
  - runs/bootstrap/B11-delegated-answers/RESPONSE.md d67ff39fc6c7bf5c
  - .claude/skills/product-interview/SKILL.md a188d28441e36165
- Dispatch: `node scripts/dispatch-step.mjs --step runs/bootstrap/B12-decisions-and-plan --agent product-architect --mode bypassPermissions --milestone bootstrap`

<!-- DISPATCH:BEGIN -->
Task B12 of the App Creator bootstrap: delegated product interview, step 3 of 3 — record the decisions and write the agreed planning documents for the SEC Analytics example. Load and follow `.claude/skills/product-interview/SKILL.md` (Delegated mode) and its templates, and `.claude/skills/plan-architecture/SKILL.md`. Inputs: the questions (runs/bootstrap/B10-interview-questions/RESPONSE.md) and the delegate's answers (runs/bootstrap/B11-delegated-answers/RESPONSE.md), GOAL.md, PROGRESS.md, docs/TOOLKIT.md, docs/research/*.md.
Write exactly these files:
1. docs/PRODUCT-DECISIONS.md — scoped explicitly to the SEC Analytics example; for every question: id, the question verbatim, the delegate's answer verbatim, basis class (Explicit instructor requirement / Delegated assumption / Not delegable), and source (GOAL.md section or decision id). Add a header that explains the delegation (who answered, from which brief, links to both step records, date 2026-11-03), and a short section listing the non-delegable items and how they are handled.
2. milestones/product.md, milestones/architecture.md, milestones/acceptance.md, milestones/plan.md — the four documents from the templates, status "agreed on 2026-11-03 (delegated, see docs/PRODUCT-DECISIONS.md)". Architecture: Next.js frontend in examples/sec-analytics/frontend, FastAPI backend in examples/sec-analytics/backend, fixtures in examples/sec-analytics/fixtures, same-origin /api proxy, SEC calls server-side only with host/path allowlist, disk cache, throttling; data modes (demo/fixture vs live vs cached) and their UI labels; module layout; API endpoints per milestone (name them with request/response shapes); concept-mapping and restatement policy outline; OpenRouter boundary (key transient, server-side forward, localhost). Acceptance: checkable criteria with ids grouped per milestone (M1-AC1…, M2-AC1…, etc.), known-answer calculation examples with hand working for each ratio (use round illustrative inputs, clearly labelled illustrative, NOT claimed SEC values), edge cases (missing tags, duplicate filings, zero denominators, negative equity, incompatible units, 52/53-week years, amendments, prompt injection, invalid citations). Plan: the five milestones as slices with their criteria ids and skills.
3. milestones/README.md — what the milestones are (five cumulative student-facing releases of SEC Analytics), the ref chain (template-v1 → m1 → m2 → m3 → m4 → m5), links to the four documents and to each milestone folder, and that a completed checkout is for inspection, not for re-running its own prompt.
Keep finance specifics in these files (not in generic toolkit files). Do not write the milestone PROMPT.md files (next step). Do not edit other files. Verify that every question id appears in docs/PRODUCT-DECISIONS.md (run a grep/count) and that `npm run check-toolkit` passes for links in your files; report output.

End your final message with exactly this block (concise):
## Handoff
Changes: <files created/changed>
Verification evidence: <commands run and exit codes>
Remaining findings: <open issues, doubts>
Next action: <one line>
Do not commit, push, tag or change git configuration; the owner integrates and commits. Never read, create or print .env files or secrets, and never write email addresses into files.
<!-- DISPATCH:END -->
