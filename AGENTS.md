<!-- App Creator. Shared instructions for every AI coding assistant (Claude Code imports this file from CLAUDE.md;
     Cline reads it directly). Tool-specific notes: CLAUDE.md, .clinerules/cline.md. Toolkit conventions:
     docs/TOOLKIT.md. People: read START-HERE.md instead. -->
# Working on this application

This repository is an application project built by a student, a student team or an instructor (the **owner**) with
an AI coding assistant (Claude Code, Cline or similar). The owner decides what is built; you plan, implement, test
and explain. The owner may be new to programming: explain in plain language, define a technical term the first
time you use it, and keep the code readable.

## First thing in every session

1. Read `app-creator.config.json`. `"app": null` means no app exists yet (template mode). Otherwise `app.docsDir`,
   `app.frontendDir` and `app.backendDir` (written `<docs>`, `<frontend>`, `<backend>` below) say where the app is.
2. If there is no app, or `<docs>/product.md` is missing or not marked `Status: agreed on <date>`: use the
   `product-interview` skill before writing any application code.
3. Otherwise read `<docs>/product.md`, `<docs>/architecture.md` and the latest entries of `<docs>/plan.md` before
   acting, and do not ask questions those documents already answer.

## Where things live

| Path | What | Who changes it |
|---|---|---|
| `AGENTS.md`, `CLAUDE.md`, `.clinerules/`, `.clineignore`, `START-HERE.md`, `PROMPTS.md`, `.claude/` | the toolkit: rules, skills (`.claude/skills/`, index in `INDEX.md`), agents (`.claude/agents/`), permissions | only on the owner's explicit request |
| `scripts/`, `scaffold/`, `package.json` | the root commands and the walking-skeleton app that `npm run create-app` copies | only on the owner's explicit request |
| `app-creator.config.json` | which app the root commands run | `npm run create-app`, or you with the owner's agreement |
| `<frontend>`, `<backend>` (default `app/frontend`, `app/backend`) | the application code and its tests | you, within the agreed plan |
| `<docs>` (default `app/docs`): `product.md`, `architecture.md`, `acceptance.md`, `plan.md` | the product's decisions and progress (created by the interview) | you, kept current after every change |
| `docs/` | App Creator's own documentation, not the app's | only on the owner's request |
| `runs/` | append-only records of delegated steps (prompt, verbatim response, result) | the owner and `scripts/dispatch-step.mjs` |
| `AI-USAGE.md` | the disclosure of meaningful AI assistance | you add entries; the owner reviews them |
| `.env.example` | setting names with placeholders or safe development values | you |
| `.env` | real settings and secrets | the owner only; you never create, read, edit, print or commit it |
| `<backend>/.venv/`, `node_modules/`, `.cache/`, `.logs/` | Python environment, packages, test browser, logs | created by the root commands; git-ignored |

## Skills and agents

Skills are folders `.claude/skills/<name>/SKILL.md`; `.claude/skills/INDEX.md` says when to use each one. If your
tool does not load a skill automatically, open its `SKILL.md` and follow it yourself. Agents in `.claude/agents/`
are specialists (builders, read-only reviewers, orchestration). Where the tool has subagents (Claude Code) they run
as separate agents. Where it does not (Cline's VS Code extension), a separate task follows the agent file; see
"Without subagents" in `review-changes`. Reviewers never edit; you fix their findings and re-run the checks.

## Working modes

- **Interactive (default).** The owner answers the product interview, approves each slice plan and every commit.
- **Delegated.** Only when the owner has written a brief that explicitly delegates routine decisions (see
  `docs/TOOLKIT.md` §4). Then `delegated-product-owner` answers routine interview questions from the brief and
  records each answer with its basis, and work runs as recorded steps (`orchestrate-steps`). Commits inside the
  delegated scope need no prompt. The delegation never covers new scope, money, publication, personal data,
  secrets or accepting a blocker: stop and ask, or record a blocker.

## Working rules

1. **Small, understandable changes.** One slice of `<docs>/plan.md` at a time; a few files per change. Plan the
   slice, get the go-ahead (interactive) or check it against the delegation (delegated), then make routine edits
   within that plan without asking for each file. Ask again if the scope, the architecture, a paid service,
   personal data or a secret is involved.
2. **Keep the documents current.** After every change update slice status and the progress log in
   `<docs>/plan.md`, criteria statuses in `<docs>/acceptance.md`, and decisions in `<docs>/architecture.md`. If code
   and documents disagree, say so and ask which one is right.
3. **Record meaningful AI assistance** in `AI-USAGE.md`: design proposals, generated code, bugs found or fixed,
   reviews, and your own mistakes that were caught. Not every typo.
4. **Secrets and settings.** Setting names go in `.env.example` with placeholders or safe development values,
   never real secrets. The owner creates `.env` from it; you never create, read, edit, print, echo or log a `.env`
   file, never ask anyone to paste a key into the chat, never put a key in code, tests, docs, `runs/` or a commit.
   Design settings so tests need no `.env`, unsafe options are off by default, and pass non-secret settings inline
   (`BACKEND_PORT=8001 npm run dev`). If a secret was committed or pasted, tell the owner to revoke it first.
5. **Test by risk** (`test-and-check`): calculations, data handling, permissions and payments get automated tests;
   screens get a browser journey check. Write the failing test first for logic and bugs; a slice is complete only
   when its tests pass. Expected values for calculations come from hand working or a cited source recorded in
   `<docs>/acceptance.md`, never from the app's own output.
6. **Git checkpoints.** After each verified slice, propose a commit with a clear message (`feat:`, `fix:`,
   `test:`, `docs:`). Interactive mode: the owner approves every commit. Never push, force-push, rewrite shared
   history, move tags or change remotes unless the owner asks. Teams: one branch per slice and a pull request
   reviewed by a teammate (`git-collaboration`).
7. **No unrequested scope.** Do not add features listed under "Explicitly not in the MVP", or services and
   libraries the plan does not need.
8. **Never claim it works without checking it.** Generated code, a passing build or a server that starts are not
   proof. Run `npm run verify` and exercise the main user journey. Keep three kinds of evidence apart: automated
   tests, the browser check (Playwright, run by `npm run verify`), and visual inspection (screenshots you looked at,
   then the owner's own look). If nothing can show the screen, give exact steps and report the journey as not
   verified.
9. **Stop and ask** when a requirement is unclear or contradictory, a check fails twice after two different fixes,
   something would cost money, or a request would break a rule above.
10. **One isolated environment.** Use the root commands: `npm run setup` creates `<backend>/.venv` with a supported
    Python and installs locked packages. Never install into a base Anaconda, system or global Python or npm, and
    never install system-wide tools without the owner's agreement.
11. **Course and client rules** given by the owner (data terms, AI policy, deadlines) override convenience. Ask
    when unsure.

## Change report (end every change with this)

```
What changed: <one to three sentences, for a non-programmer>
Files: <the main files touched>
How to preview: <exact command, URL, and what to click>
Tests: <commands run and results, e.g. "npm run verify: all checks passed">
Browser check: <command and result at which widths, or "not run" and why>
Looked at: <screenshots inspected by the assistant / the owner's look: done or pending>
Not verified / still open: <honest gaps; review findings not fixed, with why (see review-changes)>
Next: <the suggested next step>
```

Delegated steps end with the `## Handoff` block of `docs/TOOLKIT.md` §7 instead.

## This project

The commands are the same for every app; they read `app-creator.config.json` (contract: `docs/TOOLKIT.md` §3).
Run them from the repository root after a one-time `npm ci`.

- Product: `<docs>/product.md` (none yet while `"app"` is `null`)
- Stack: Next.js + FastAPI (`docs/TOOLKIT.md` §2), unless `<docs>/architecture.md` records another choice
- Create the app: `npm run create-app` (copies `scaffold/` to `app/`)
- Install: `npm run setup`
- Run: `npm run dev` (offline demo: `npm run demo`)
- Test and browser check: `npm run verify`
