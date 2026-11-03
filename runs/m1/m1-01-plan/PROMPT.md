# PROMPT — m1-01-plan

- Sender: owner (top-level Claude Code session)
- Receiver: project-orchestrator (plans M1)
- Starting commit at prompt write: 776a7b6 (RESULT.json records the commit at dispatch)
- Skills to load: orchestrate-steps
- Key instruction/reference files (sha256 prefix when written):
  - docs/TOOLKIT.md 72165a1d6238722a
  - GOAL.md 20b3a7b8e8c2aa44
  - milestones/01-foundation/PROMPT.md 298457211d6a0d6f
- Dispatch: `node scripts/dispatch-step.mjs --step runs/m1/m1-01-plan --agent project-orchestrator --mode bypassPermissions --milestone m1`

<!-- DISPATCH:BEGIN -->
Task m1-01: plan milestone M1 (Foundation) of the SEC Analytics example. The immutable brief is milestones/01-foundation/PROMPT.md (at tag template-v1; read it completely), with milestones/architecture.md, milestones/acceptance.md, milestones/plan.md and docs/PRODUCT-DECISIONS.md. The current branch is main at a commit that descends from template-v1 (only step records were added after the tag).
How steps will be dispatched: each implementation step's text will be a short step scope written from your plan, followed by the full milestone brief embedded verbatim. Builders cannot spawn agents; the owner integrates, commits and checkpoints. The SEC contact (SEC_USER_AGENT) will be present in the environment of the step that captures fixtures (never in files or prompts); live SEC fetching is allowed only for that fixture capture and an optional live smoke check, throttled per the brief.
Plan M1 as small, verifiable steps (ids m1-02…): which agent (backend-engineer, frontend-engineer, design-lead, test-engineer, a reviewer, ...), skills, the exact scope and file ownership, done-when (acceptance ids and commands), and which steps can run in parallel without editing the same files (name the shared contract — API shapes and fixture formats — each parallel step must respect). Include the review steps (which reviewers) and the gate. Keep it under ~800 words. Do not edit files.

End your final message with exactly this block (concise):
## Handoff
Changes: <files created/changed>
Verification evidence: <commands run and exit codes>
Remaining findings: <open issues, doubts>
Next action: <one line>
Do not commit, push, tag or change git configuration; the owner integrates and commits. Never read, create or print .env files or secrets, and never write email addresses into files.
<!-- DISPATCH:END -->
