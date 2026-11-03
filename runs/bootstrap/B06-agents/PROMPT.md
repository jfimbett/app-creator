# PROMPT — B06-agents

- Sender: owner (top-level Claude Code session)
- Receiver: default (Claude Code default agent; builder agents are created by this step)
- Starting commit: 47dbf85 (plus uncommitted owner changes listed in PROGRESS.md, if any)
- Skills to load: none (reads .claude/skills/review-changes/SKILL.md)
- Key instruction/reference files (sha256 at dispatch):
  - docs/TOOLKIT.md 136a3145d82696f1
  - GOAL.md 20b3a7b8e8c2aa44
- Dispatch: `node scripts/dispatch-step.mjs --step runs/bootstrap/B06-agents --agent default --mode bypassPermissions --milestone bootstrap`

<!-- DISPATCH:BEGIN -->
Task B06 of the App Creator bootstrap: create and adapt the generic agents in `.claude/agents/`. Read first: `docs/TOOLKIT.md` (conventions; frozen agent and skill names), `GOAL.md` §3 and §8, `docs/research/claude-code-and-cline.md` (current subagent frontmatter format; if the file is missing, use the format already used by the existing agents), the existing agents in `.claude/agents/` (four starter reviewers imported unchanged, plus `project-orchestrator.md` and `delegated-product-owner.md`), and `.claude/skills/review-changes/SKILL.md`.

Work (only files in `.claude/agents/`):
1. Keep `code-reviewer`, `security-reviewer`, `ux-reviewer`, `test-reviewer` read-only and keep their good content and report format. Adapt their path references from the starter's single `app/` folder to App Creator: the app's location comes from `app-creator.config.json` (frontend dir, backend dir, docs dir); run commands are the root `npm run verify` / `npm run demo` (or the narrower commands in the app's README). The browser check is now the project-local Playwright suite run by `npm run verify`. Add to security-reviewer: same-origin proxy and CORS/host binding, SSRF/arbitrary-URL-proxy risk for server-side fetchers (allowlisted hosts and paths, including redirects), untrusted HTML/text rendering, keys forwarded transiently, never logged. Add to test-reviewer: offline-by-default tests, synthetic fixtures clearly marked and isolated, recorded authentic fixtures with provenance. Keep them domain-neutral.
2. Review `project-orchestrator.md` and `delegated-product-owner.md` and only fix format problems (do not change their role).
3. Create: `product-architect` (requirements, MVP, acceptance criteria, architecture, API and data design; writes planning documents and briefs; uses product-interview and plan-architecture), `frontend-engineer` (Next.js/React/TS/Tailwind/Recharts screens, states, accessibility; uses build-feature, design-interface, test-and-check), `backend-engineer` (FastAPI, external API clients, validation, errors, caching; uses build-feature, integrate-api, manage-data, test-and-check), `design-lead` (design system, typography, layout, charts, responsive and accessible UI states; may edit styles/components; uses design-interface), `test-engineer` (writes meaningful tests and Playwright journeys, runs the verification commands; uses test-and-check, debug-issue), `docs-writer` (README/setup/teaching docs that match tested commands; uses write-docs), `github-coach` (explains and proposes safe git/GitHub workflows for a team of about five; read-mostly: may run read-only git commands, never pushes, force-pushes, rewrites shared history, or changes remotes/settings; uses git-collaboration).
Each agent: valid frontmatter (name = filename; a description that says when to use it; tool restrictions appropriate to the role; list its skills if the current format supports a skills field, otherwise name them in the body), a short role statement, what to read first, how it works (concrete steps), hard rules (no secrets, no unrequested scope, small changes, never claim unverified results, no commits/pushes unless the dispatching owner explicitly allows it), and the shared Handoff format from docs/TOOLKIT.md §7. Keep each file focused (roughly 40–90 lines). Domain-neutral: no finance or SEC content.
Verification: run a small node or shell check that every file in .claude/agents/ has frontmatter with name matching its filename and a description, and report the output.

End your final message with exactly this block (concise):
## Handoff
Changes: <files created/changed>
Verification evidence: <commands run and exit codes>
Remaining findings: <open issues, doubts>
Next action: <one line>
Do not commit, push, tag or change git configuration; the owner integrates and commits. Never read, create or print .env files or secrets, and never write email addresses into files.
<!-- DISPATCH:END -->
