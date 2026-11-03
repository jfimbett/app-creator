# PROMPT — B17-repair-milestone-prompts

- Sender: owner (top-level Claude Code session)
- Receiver: product-architect (applies orchestrator repair decision from B14)
- Starting commit at prompt write: 6727dc2 (RESULT.json records the commit at dispatch)
- Skills to load: plan-architecture
- Key instruction/reference files (sha256 prefix when written):
  - docs/TOOLKIT.md 72165a1d6238722a
  - GOAL.md 20b3a7b8e8c2aa44
  - runs/bootstrap/B14-review-milestone-prompts/RESPONSE.md d0c640c84582cddc
- Dispatch: `node scripts/dispatch-step.mjs --step runs/bootstrap/B17-repair-milestone-prompts --agent product-architect --mode bypassPermissions --milestone bootstrap`

<!-- DISPATCH:BEGIN -->
Task B17: apply the project-orchestrator's repair decision for the milestone prompts and planning documents. The exact edits are in runs/bootstrap/B14-review-milestone-prompts/RESPONSE.md: apply every "Quote → Replace with" and "Add" edit under "Per prompt" (M1 optional hardening, M2 items 1–3, M3 items 1–2, M5 items 1–2 — include the optional ones), and B13 open items 1, 2, 3, 4, 6, 7 and 9 from "B13's open items: how to resolve each" (item 1 and the other decision changes also add rows to the "Changes to earlier decisions" section of docs/PRODUCT-DECISIONS.md, each citing B14 as the basis). Make each edit exactly as specified; where a quoted text is not found verbatim, locate the equivalent sentence, apply the intent, and list it in your handoff. Edit only milestones/** and docs/PRODUCT-DECISIONS.md. Do not touch runs/. Verify: `npm run check-toolkit` exit 0; grep shows no email addresses in milestones/ and docs/PRODUCT-DECISIONS.md; print the sha256 of each of the five milestones/0*/PROMPT.md files after your edits.

End your final message with exactly this block (concise):
## Handoff
Changes: <files created/changed>
Verification evidence: <commands run and exit codes>
Remaining findings: <open issues, doubts>
Next action: <one line>
Do not commit, push, tag or change git configuration; the owner integrates and commits. Never read, create or print .env files or secrets, and never write email addresses into files.
<!-- DISPATCH:END -->
