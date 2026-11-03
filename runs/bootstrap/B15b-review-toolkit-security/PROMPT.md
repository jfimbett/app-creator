# PROMPT — B15b-review-toolkit-security

- Sender: owner (top-level Claude Code session)
- Receiver: security-reviewer (read-only reviewer)
- Starting commit at prompt write: 49dd630 (RESULT.json records the commit at dispatch)
- Skills to load: review-changes (reviewer side)
- Key instruction/reference files (sha256 prefix when written):
  - docs/TOOLKIT.md cde60522bfd2ce4b
  - GOAL.md 20b3a7b8e8c2aa44
- Dispatch: `node scripts/dispatch-step.mjs --step runs/bootstrap/B15b-review-toolkit-security --agent security-reviewer --mode bypassPermissions --milestone bootstrap`

<!-- DISPATCH:BEGIN -->
Task B15b: read-only security review of the App Creator generic toolkit before the `template-v1` checkpoint and public publication. Scope: all tracked files (`git ls-files`) and history (`git log -p`), with focus on .claude/settings.json, .gitignore, .clineignore, .env.example, scripts/ (launcher reads an optional root .env; dispatch-step.mjs redaction), scaffold/ (host binding 127.0.0.1, proxy), .github/workflows/verify.yml, runs/ (step records must not contain secrets, tokens or personal email addresses — report file:line only, never the value), and the skills' security guidance (integrate-api, prepare-deploy/security-checklist.md, env-and-secrets.md). Also confirm no `.env`, keys, node_modules, .venv, .cache or app-starter.zip are tracked. Do not edit files; never print secret values. Return your standard report format, then the handoff.

End your final message with exactly this block (concise):
## Handoff
Changes: <files created/changed>
Verification evidence: <commands run and exit codes>
Remaining findings: <open issues, doubts>
Next action: <one line>
Do not commit, push, tag or change git configuration; the owner integrates and commits. Never read, create or print .env files or secrets, and never write email addresses into files.
<!-- DISPATCH:END -->
