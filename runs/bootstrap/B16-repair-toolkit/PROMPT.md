# PROMPT — B16-repair-toolkit

- Sender: owner (top-level Claude Code session)
- Receiver: backend-engineer (repairs launcher/dispatcher/guide findings)
- Starting commit at prompt write: 49dd630 (RESULT.json records the commit at dispatch)
- Skills to load: debug-issue, review-changes (fix side), integrate-api
- Key instruction/reference files (sha256 prefix when written):
  - docs/TOOLKIT.md cde60522bfd2ce4b
  - GOAL.md 20b3a7b8e8c2aa44
  - runs/bootstrap/B15a-review-toolkit-code/RESPONSE.md ce2f6a676bf20547
  - runs/bootstrap/B15b-review-toolkit-security/RESPONSE.md 7aa7bb16828e77dc
- Dispatch: `node scripts/dispatch-step.mjs --step runs/bootstrap/B16-repair-toolkit --agent backend-engineer --mode bypassPermissions --milestone bootstrap`

<!-- DISPATCH:BEGIN -->
Task B16: repair the toolkit findings from the two read-only reviews before the `template-v1` checkpoint. Read both reports: runs/bootstrap/B15a-review-toolkit-code/RESPONSE.md (code findings #1–#12) and runs/bootstrap/B15b-review-toolkit-security/RESPONSE.md (security findings #3–#8). Load .claude/skills/debug-issue/SKILL.md and .claude/skills/review-changes/SKILL.md (fix side).
Fix: code #1–#12 and security #3, #4, #5 (same as code #1), #6, #7, #8. Specifics:
- #1/#5: verify (all steps) and demo must not load the root .env; dev may. Document it in docs/TOOLKIT.md §3 (one line) — this is the only docs/TOOLKIT.md edit allowed.
- #2/#3/#7/#9 and security #4: dispatcher robustness and redaction. Keep its CLI and record format backward compatible (existing runs/ records must stay valid). Add `redactions` counts and `responseRedactedSha256` to RESULT.json; refuse to dispatch (exit 2) if the dispatched text contains a credential pattern; add a home-directory pattern (/Users/<name>, /home/<name>, C:\Users\<name>) → `[REDACTED:user]`. Do not change how emails are redacted.
- #4: Windows hints show both PowerShell and cmd forms, plus the root .env option.
- security #6: update .claude/skills/integrate-api/http-client-patterns.md (response size cap via streaming, a real overall timeout, port check) and the size-limit line in integrate-api/SKILL.md.
- security #7: pin the GitHub Actions in .github/workflows/verify.yml to full commit SHAs with a version comment. Look the SHAs up with `gh api repos/<owner>/<repo>/git/ref/tags/<tag>` (dereference annotated tags via `gh api repos/<owner>/<repo>/git/tags/<sha>` when the ref type is "tag"); also run Linux install-deps from the installed Playwright (code #12) instead of a second pinned copy; add one line to .claude/skills/prepare-deploy/ci.md about SHA pinning.
- code #12 eslint peer warning: record it as a known, accepted issue in scaffold/README.md.
Do NOT edit .claude/settings.json (owned by the owner; security #2 is reported to the owner instead), do not touch runs/ records, milestones/ or docs/PRODUCT-DECISIONS.md, and do not change git configuration or history (security #1 is the owner's decision).
Verify: `node --check` each changed .mjs; a small throwaway test of `redact()` (credential samples, home path, an @example.com address unchanged) and of the dispatcher's missing-command error path that writes a failed record — run it against a temporary step directory under .cache/ (git-ignored), never under runs/; `npm run check-toolkit`; and the FULL `npm run verify` (it must exit 0, including build and Playwright). Report every command and exit code; leave no servers running.

End your final message with exactly this block (concise):
## Handoff
Changes: <files created/changed>
Verification evidence: <commands run and exit codes>
Remaining findings: <open issues, doubts>
Next action: <one line>
Do not commit, push, tag or change git configuration; the owner integrates and commits. Never read, create or print .env files or secrets, and never write email addresses into files.
<!-- DISPATCH:END -->
