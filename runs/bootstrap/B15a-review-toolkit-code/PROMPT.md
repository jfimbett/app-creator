# PROMPT — B15a-review-toolkit-code

- Sender: owner (top-level Claude Code session)
- Receiver: code-reviewer (read-only reviewer)
- Starting commit at prompt write: 49dd630 (RESULT.json records the commit at dispatch)
- Skills to load: review-changes (reviewer side)
- Key instruction/reference files (sha256 prefix when written):
  - docs/TOOLKIT.md cde60522bfd2ce4b
  - GOAL.md 20b3a7b8e8c2aa44
- Dispatch: `node scripts/dispatch-step.mjs --step runs/bootstrap/B15a-review-toolkit-code --agent code-reviewer --mode bypassPermissions --milestone bootstrap`

<!-- DISPATCH:BEGIN -->
Task B15a: read-only code review of the App Creator generic toolkit before the `template-v1` checkpoint. Scope: `git diff 6e8314a..HEAD -- scripts/ scaffold/ package.json app-creator.config.json .github/` (the launcher, scaffold, toolkit checker, dispatcher and CI). Context: docs/TOOLKIT.md §3 is the command contract; GOAL.md §4 (portability macOS/Windows, idempotent setup, no recursive setup, dev cleans up only its own processes, never kill unrelated services, demo offline, verify exits nonzero on failure). Check correctness, Windows portability (paths, spawn/shell, process-tree cleanup, venv paths), idempotency logic, port handling, error messages, and the dispatcher's capture/redaction logic. You may run `npm run check-toolkit` and `npm run verify -- --quick` (both safe, local). Do not edit files. Return your standard report format, then the handoff.

End your final message with exactly this block (concise):
## Handoff
Changes: <files created/changed>
Verification evidence: <commands run and exit codes>
Remaining findings: <open issues, doubts>
Next action: <one line>
Do not commit, push, tag or change git configuration; the owner integrates and commits. Never read, create or print .env files or secrets, and never write email addresses into files.
<!-- DISPATCH:END -->
