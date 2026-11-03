# PROMPT — B07a-skills-product-design

- Sender: owner (top-level Claude Code session)
- Receiver: docs-writer (agent created in B06)
- Starting commit: 47dbf85 (working tree may hold uncommitted owner/step changes; see git status in RESULT/PROGRESS)
- Skills to load: product-interview, plan-architecture, design-interface, build-feature (as files to edit)
- Key instruction/reference files (sha256 prefix at dispatch):
  - docs/TOOLKIT.md 136a3145d82696f1
  - GOAL.md 20b3a7b8e8c2aa44
  - docs/research/claude-code-and-cline.md 465f89b85d605c92
- Dispatch: `node scripts/dispatch-step.mjs --step runs/bootstrap/B07a-skills-product-design --agent docs-writer --mode bypassPermissions --milestone bootstrap`

<!-- DISPATCH:BEGIN -->
Task B07a of the App Creator bootstrap: product and design skills.
Read first: `docs/TOOLKIT.md` (conventions, frozen skill names, root commands, working modes; follow it), `GOAL.md` §3 (required coverage), `docs/research/claude-code-and-cline.md` (current skill format; if missing, use the existing SKILL.md frontmatter format), and the existing skill folders you own (imported unchanged from app-starter 0.3.0; preserve their good content, rules and tone, and adapt rather than rewrite blindly).
General adaptation rules for every skill you touch: paths come from `app-creator.config.json` (the app may live in `app/frontend`, `app/backend`, docs in the configured docs dir) instead of the starter's single `app/`; the standard stack is Next.js/React/TS/Tailwind/Recharts + FastAPI (Streamlit and Django are no longer the defaults; mention alternatives only briefly); run/test via the root `npm run setup|dev|verify|demo` contract; Playwright (project-local, run by `npm run verify`) replaces the starter's Python browser_check; the approval rules follow docs/TOOLKIT.md §4 (interactive default; recorded delegation allows routine decisions and commits, never scope/money/publication/personal data/secrets). Every SKILL.md: valid YAML frontmatter (`name` equals folder name; `description` = concrete trigger conditions, under ~300 characters), then Inputs, Actions (concrete numbered workflow), Outputs, Verification (checks), Stop when (failure handling), Common mistakes, and at least one short concrete example. Supporting guides live in the same folder and are linked from SKILL.md with relative links; make them practical (checklists, code snippets, commands), not generic essays. Domain-neutral: no SEC/finance assumptions (a neutral financial example is acceptable where it teaches a general rule like "missing is not zero"). Do not create category subfolders; do not touch files outside your listed folders.
Verification: run a check that each of your SKILL.md files parses (frontmatter name matches folder, description present) and that every relative link in your files resolves; report the command output.
Your folders: .claude/skills/product-interview/, .claude/skills/plan-architecture/ (new), .claude/skills/design-interface/, .claude/skills/build-feature/.
Work:
1. product-interview: keep the interview rounds, templates and "stop and ask" rules. Add a **Delegated mode** section: when the owner has recorded a delegation (a brief such as GOAL.md), the interviewer writes its questions, the `delegated-product-owner` agent answers them from the brief, and the interviewer records questions, exact answers and basis (explicit requirement vs delegated assumption vs not delegable) in the decisions file (`docs/PRODUCT-DECISIONS.md` by default), then fills the four documents. Templates stay in templates/ (product, architecture, acceptance, plan) and are written to the configured docs dir. Requirements/MVP/acceptance-criteria guidance must be strong (checkable criteria, known-answer calculations). Rewrite stacks.md around the standard stack and the launcher contract; keep the excellent Python-interpreter discovery (Anaconda, py -0p) but as what `npm run setup` does and how to override with APP_PYTHON.
2. plan-architecture (new): architecture boundaries (UI / logic / data access / external services), API design (resource naming, typed contracts, pagination, error envelope, light versioning), database/storage design (when SQLite vs files vs nothing; schema and migrations pointer to manage-data), validation (server-side, pydantic; client-side only for UX), error handling (user-facing vs logged, no stack traces to users), caching/background jobs (when needed; simple options first), environment/secrets layout, and a decision log. Guides: api-and-contracts.md, errors-and-validation.md, caching-and-jobs.md.
3. design-interface: keep the good content. Replace the finance-specific financial-visuals.md with a domain-neutral charts-and-data-display.md (keep its general rules: missing ≠ 0, units, periods, tabular numerals, text alternative). Add guides: design-system.md (tokens, dark/light theme via CSS variables with Tailwind v4, typography scale, spacing, density, shadcn/ui usage), ui-states-and-forms.md (loading/empty/error/offline/missing-data states, forms with labels, validation messages), responsive-and-accessibility.md (390/1366 px widths, keyboard, focus, contrast, reduced motion, charts' text alternatives). Update links in product-interview that pointed to the old file.
4. build-feature: adapt to the step/handoff workflow (in delegated mode the orchestrator plans and gates; see orchestrate-steps), small slices, logic-first with tests, the root verify command.

End your final message with exactly this block (concise):
## Handoff
Changes: <files created/changed>
Verification evidence: <commands run and exit codes>
Remaining findings: <open issues, doubts>
Next action: <one line>
Do not commit, push, tag or change git configuration; the owner integrates and commits. Never read, create or print .env files or secrets, and never write email addresses into files.
<!-- DISPATCH:END -->
