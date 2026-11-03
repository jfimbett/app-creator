# App Creator toolkit: conventions and inventory

App Creator is a reusable starter for building a web application with an AI coding assistant (Claude Code
first, Cline as a documented but untested alternative). It grew out of `app-starter` 0.3.0, whose skills,
reviewers and rules were imported unchanged (commit `47dbf85`) and then adapted. This file is the single
reference for how the toolkit is organized. Skills and agents link here instead of repeating it.

## 1. Layout

| Path | Contents | Generic or example-specific |
|---|---|---|
| `CLAUDE.md`, `AGENTS.md` | short shared working rules (`CLAUDE.md` imports `AGENTS.md`) | generic |
| `.clinerules/`, `.clineignore` | Cline equivalents of the rules | generic |
| `.claude/skills/<name>/SKILL.md` | skills, flat (one folder per skill; no category folders). Index: `.claude/skills/INDEX.md` | generic |
| `.claude/agents/<name>.md` | specialist agents (builders, reviewers, orchestration) | generic, plus example agents added with the example |
| `.claude/settings.json` | project permissions (`.env` reads/edits denied, commits ask) | generic |
| `app-creator.config.json` | which app the root commands run (frontend dir, backend dir, docs dir, ports, demo env) | per branch |
| `scaffold/` | minimal walking-skeleton app (Next.js + FastAPI) copied by `npm run create-app` | generic |
| `app/` | a student's new application (created from `scaffold/`); its docs in `app/docs/` | per project |
| `scripts/` | portable Node launchers (`setup`, `dev`, `verify`, `demo`, `create-app`), `check-toolkit.mjs`, `dispatch-step.mjs` | generic |
| `runs/` | append-only step records (prompt, verbatim response, result) | per project |
| `milestones/` | the SEC Analytics example's build briefs and planning documents | example |
| `examples/sec-analytics/` | the SEC Analytics example app (only on milestone branches and `main`) | example |
| `docs/` | App Creator's own documentation | generic, plus example reports on `main` |

## 2. Standard stack (what the launchers support)

Next.js (App Router) + React + TypeScript + Tailwind CSS v4, shadcn/ui-style components where they help,
Recharts for charts; Python FastAPI backend; SQLite or a disk cache only when needed; pytest; Vitest for pure
frontend logic; project-local Playwright for browser journeys. The frontend calls the backend **same-origin** through
`/api/*`, which Next.js rewrites to the backend in development. Browsers never call third-party APIs or hold server
secrets. Other stacks can be used, but then the root commands must be adapted (see `prepare-deploy`).

## 3. Root commands (contract)

Run them from the repository root after a one-time `npm ci`. The root `package.json` has no runtime dependencies,
but `npm ci` still installs the lockfile.

| Command | Does | With no app configured (template) |
|---|---|---|
| `npm run setup` | checks Node ≥ 20.9 and finds a supported Python (3.10–3.13; `APP_PYTHON` overrides). Creates `<backend>/.venv` and installs `requirements.lock`; runs `npm ci` in `<frontend>`; installs Playwright Chromium into `.cache/ms-playwright`. Idempotent: it skips steps whose lockfile hash has not changed. It never calls `npm run setup` recursively. | checks versions, prints next steps, exits 0 |
| `npm run dev` | starts the backend (127.0.0.1) and frontend. It refuses occupied ports (never kills them) and stops only its own child processes on Ctrl+C | prints guidance, exits 0 |
| `npm run demo` | like `dev`, but with the config's `demoEnv` (for example offline fixture mode, no keys, no network) | prints guidance, exits 0 |
| `npm run verify` | runs the toolkit checks, then for the app: backend lint and tests, frontend lint, typecheck, unit tests, production build in a separate dist dir, then both services on spare ports with a Playwright smoke test. Exits nonzero on any failure | runs the toolkit checks plus a scaffold check in a temporary copy |
| `npm run create-app` | copies `scaffold/` to `app/` (or `--dir <path>`) and points the config at it. It refuses to overwrite | — |

Environment: `.env.example` at the root lists every setting. The real `.env` is created by the person, git-ignored,
and never read or printed by an assistant. Ports default to backend 8000 and frontend 3000, and can be changed with
`BACKEND_PORT` / `FRONTEND_PORT`.

## 4. Working modes and approval rules

The starter required the student's go-ahead for every plan and commit. App Creator keeps that as the default
and adds a recorded delegation:

- **Interactive (default):** the student answers the `product-interview` questions, approves plans, approves
  every commit. Push, publish, paid services, personal data and secrets always need the student.
- **Delegated:** the owner has written a brief (for example a `GOAL.md`) that explicitly delegates routine
  decisions. Then `delegated-product-owner` answers routine interview questions from that brief, records each
  answer and its basis in the decisions file, and the `project-orchestrator` gates steps. Commits inside the
  delegated scope are allowed without a prompt. The delegation never covers: new scope, money, publication
  targets, personal data, secrets, or accepting a blocker. Those still stop and ask, or are recorded as blockers.

## 5. Step records (`runs/`)

Every meaningful delegated step gets `runs/<milestone-or-bootstrap>/<step-id>/`:
`PROMPT.md` (metadata plus the exact dispatched text between `<!-- DISPATCH:BEGIN -->` and `<!-- DISPATCH:END -->`,
written before dispatch), `RESPONSE.md` (the verbatim final message), and `RESULT.json` (timestamps, roles, commits,
status, session id). `node scripts/dispatch-step.mjs` does the dispatch and capture. Rules are in
`.claude/skills/orchestrate-steps/SKILL.md`.

## 6. Skills (frozen names)

`product-interview`, `plan-architecture`, `design-interface`, `build-feature`, `integrate-api`, `manage-data`,
`add-accounts`, `add-payments`, `test-and-check`, `debug-issue`, `review-changes`, `prepare-deploy`,
`git-collaboration`, `write-docs`, `orchestrate-steps`. Each `SKILL.md` has YAML frontmatter (`name` = folder name,
`description` = when to use it). The body covers inputs, actions, outputs, verification, stop-when and common
mistakes, plus supporting guides in the same folder that it links to.

## 7. Agents (frozen names)

Orchestration: `project-orchestrator`, `delegated-product-owner`. Builders: `product-architect`, `frontend-engineer`,
`backend-engineer`, `design-lead`, `test-engineer`, `docs-writer`. Coaching: `github-coach`. Read-only reviewers:
`code-reviewer`, `security-reviewer`, `ux-reviewer`, `test-reviewer`. Every handoff ends with:

```
## Handoff
Changes: <files, or none>
Verification evidence: <commands and exit codes, screenshots looked at>
Remaining findings: <open issues>
Next action: <one line>
```

## 8. What stays out of the generic toolkit

Domain rules (finance, SEC, AI-provider specifics) belong with the example (`examples/<name>/CLAUDE.md`,
example-specific skills or agents added with it). Generic skills may use neutral examples, including a financial
one when it teaches a general point such as "missing is not zero", but they must not assume the app is financial.
