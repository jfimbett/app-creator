# PROMPT — B11-delegated-answers

- Sender: owner (top-level Claude Code session)
- Receiver: delegated-product-owner (answers on the instructor's behalf from GOAL.md)
- Starting commit at prompt write: 14c2d39 (RESULT.json records the commit at dispatch)
- Skills to load: product-interview (answer side, per its Delegated mode)
- Key instruction/reference files (sha256 prefix when written):
  - docs/TOOLKIT.md cde60522bfd2ce4b
  - GOAL.md 20b3a7b8e8c2aa44
  - PROGRESS.md 4df23ae15c294e6d
  - runs/bootstrap/B10-interview-questions/RESPONSE.md 56e36d99e20752f3
- Dispatch: `node scripts/dispatch-step.mjs --step runs/bootstrap/B11-delegated-answers --agent delegated-product-owner --mode default --milestone bootstrap`

<!-- DISPATCH:BEGIN -->
Task B11 of the App Creator bootstrap: delegated product interview, step 2 of 3. You are the delegated-product-owner for the course instructor. The instructor's brief is GOAL.md (read it completely); there is no decisions file yet (docs/PRODUCT-DECISIONS.md does not exist — that is expected). Also read PROGRESS.md (decisions D1–D8 already recorded by the build owner; cite them where they settle a question) and docs/TOOLKIT.md.
The interviewer's questions are in runs/bootstrap/B10-interview-questions/RESPONSE.md (between the VERBATIM markers). Answer every question in your required table format, each with its basis: Explicit (shortest quote + GOAL.md section, or PROGRESS.md decision id), Delegated assumption (reversible default + one-line reason), or Not delegable (why; what can continue). Do not restart the interview, do not ask the instructor anything, do not expand scope beyond GOAL.md, and do not invent domain facts (company descriptions, prices). Do not edit files. Return the full answer table and the handoff.

End your final message with exactly this block (concise):
## Handoff
Changes: <files created/changed>
Verification evidence: <commands run and exit codes>
Remaining findings: <open issues, doubts>
Next action: <one line>
Do not commit, push, tag or change git configuration; the owner integrates and commits. Never read, create or print .env files or secrets, and never write email addresses into files.
<!-- DISPATCH:END -->
