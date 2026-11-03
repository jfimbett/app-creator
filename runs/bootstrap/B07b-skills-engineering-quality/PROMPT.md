# PROMPT — B07b-skills-engineering-quality

- Sender: owner (top-level Claude Code session)
- Receiver: docs-writer (agent created in B06)
- Starting commit: 47dbf85 (working tree may hold uncommitted owner/step changes; see git status in RESULT/PROGRESS)
- Skills to load: integrate-api, manage-data, add-accounts, add-payments, test-and-check, debug-issue, review-changes, prepare-deploy (as files to edit)
- Key instruction/reference files (sha256 prefix at dispatch):
  - docs/TOOLKIT.md 136a3145d82696f1
  - GOAL.md 20b3a7b8e8c2aa44
  - docs/research/claude-code-and-cline.md 465f89b85d605c92
- Dispatch: `node scripts/dispatch-step.mjs --step runs/bootstrap/B07b-skills-engineering-quality --agent docs-writer --mode bypassPermissions --milestone bootstrap`

<!-- DISPATCH:BEGIN -->
Task B07b of the App Creator bootstrap: engineering and quality skills.
Read first: `docs/TOOLKIT.md` (conventions, frozen skill names, root commands, working modes; follow it), `GOAL.md` §3 (required coverage), `docs/research/claude-code-and-cline.md` (current skill format; if missing, use the existing SKILL.md frontmatter format), and the existing skill folders you own (imported unchanged from app-starter 0.3.0; preserve their good content, rules and tone, and adapt rather than rewrite blindly).
General adaptation rules for every skill you touch: paths come from `app-creator.config.json` (the app may live in `app/frontend`, `app/backend`, docs in the configured docs dir) instead of the starter's single `app/`; the standard stack is Next.js/React/TS/Tailwind/Recharts + FastAPI (Streamlit and Django are no longer the defaults; mention alternatives only briefly); run/test via the root `npm run setup|dev|verify|demo` contract; Playwright (project-local, run by `npm run verify`) replaces the starter's Python browser_check; the approval rules follow docs/TOOLKIT.md §4 (interactive default; recorded delegation allows routine decisions and commits, never scope/money/publication/personal data/secrets). Every SKILL.md: valid YAML frontmatter (`name` equals folder name; `description` = concrete trigger conditions, under ~300 characters), then Inputs, Actions (concrete numbered workflow), Outputs, Verification (checks), Stop when (failure handling), Common mistakes, and at least one short concrete example. Supporting guides live in the same folder and are linked from SKILL.md with relative links; make them practical (checklists, code snippets, commands), not generic essays. Domain-neutral: no SEC/finance assumptions (a neutral financial example is acceptable where it teaches a general rule like "missing is not zero"). Do not create category subfolders; do not touch files outside your listed folders.
Verification: run a check that each of your SKILL.md files parses (frontmatter name matches folder, description present) and that every relative link in your files resolves; report the command output.
Your folders (all under .claude/skills/): integrate-api/, manage-data/, add-accounts/, add-payments/, test-and-check/, debug-issue/, review-changes/, prepare-deploy/.
Work:
1. integrate-api: keep its rules; add server-side-only calls, host/path allowlists and redirect validation (no arbitrary URL proxy), identification headers when a provider requires them, timeouts, throttling, retries with backoff honoring Retry-After, request dedup, disk caching with expiry, provenance (source, retrieval time, live vs cached vs recorded fixture), recorded fixtures vs synthetic fixtures (labelled, isolated), optional AI/LLM provider integration (user-supplied keys forwarded transiently, never logged/stored, bounded requests). Guide: http-client-patterns.md with a short FastAPI/httpx example.
2. manage-data: keep; add guide caching-and-storage.md (disk cache layout, SQLite with migrations, when no DB is needed, background jobs kept simple).
3. add-accounts: keep (off by default); add guide authn-authz.md (sessions vs tokens, password hashing, server-side authorization per endpoint, roles, CSRF, one test per rule) for the standard stack.
4. add-payments: keep (test mode, hosted checkout, webhook verification); adapt to FastAPI.
5. test-and-check: keep its excellent rules (independent expected values, units, missing ≠ 0). Replace browser_check.py/browser-checks.md with playwright-journeys.md (project-local Playwright via PLAYWRIGHT_BROWSERS_PATH=.cache/ms-playwright, smoke spec example in TypeScript, desktop 1366 px and narrow 390 px screenshots, visually inspecting them, separate evidence kinds). Add performance.md (measure before optimizing; bundle size, slow endpoints, caching, N+1) and a short section on frontend unit tests (Vitest) and backend tests (pytest, respx for HTTP mocking). Delete browser_check.py only after its useful ideas are moved into the guide.
6. debug-issue: keep; add refactoring.md (refactor only under passing tests, small steps, separate commits with no behavior change).
7. review-changes: keep the stopping rule and "Without subagents (Cline)" route; add the delegated-mode decision rules from docs/TOOLKIT.md §4; reviewers are code/test/security/ux.
8. prepare-deploy: keep; add guides ci.md (GitHub Actions running `npm ci && npm run setup && npm run verify` offline, optional matrix over refs, caching), docker.md (optional, never a prerequisite; a sketch for frontend+backend), env-and-secrets.md (.env.example, per-environment settings, rotation, leaked-key response), security-checklist.md (headers, CORS, host binding, dependency audit, logging without secrets). Deployment is preparation only; nothing is hosted without the owner.

End your final message with exactly this block (concise):
## Handoff
Changes: <files created/changed>
Verification evidence: <commands run and exit codes>
Remaining findings: <open issues, doubts>
Next action: <one line>
Do not commit, push, tag or change git configuration; the owner integrates and commits. Never read, create or print .env files or secrets, and never write email addresses into files.
<!-- DISPATCH:END -->
