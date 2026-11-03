<!-- app-starter 0.3.0 (2026-11-02). Shared instructions for every AI coding assistant (Claude Code imports this file
     from CLAUDE.md; Cline reads it directly). Tool-specific notes: CLAUDE.md, .clinerules/cline.md.
     Students: read START-HERE.md instead. -->
# Working on this application

This folder is an application project built by a student (or a student team) with an AI coding assistant (Claude
Code, Cline or similar). The student decides what is built; you plan, implement, test and explain. The student may
be new to programming: explain in plain language, define technical terms the first time you use them, and keep the
code readable.

## First thing in every session

- If `docs/product.md` does not exist, or is not marked agreed: use the `product-interview` skill before writing
  any application code.
- Otherwise read `docs/product.md`, `docs/architecture.md` and the latest entries of `docs/plan.md` before acting,
  and do not ask questions those documents already answer.

## Where things live

| Path | What | Who changes it |
|---|---|---|
| `AGENTS.md`, `CLAUDE.md`, `.clinerules/`, `START-HERE.md`, `PROMPTS.md`, `.claude/` | the starter: instructions, skills (`.claude/skills/`), reviewer instructions (`.claude/agents/`), settings | only on the student's explicit request |
| `docs/product.md`, `docs/architecture.md`, `docs/acceptance.md`, `docs/plan.md` | the product's decisions and progress (created by the interview) | you, kept current after every change |
| `app/` | the application: code, dependency file, tests, `app/README.md`, `app/.env.example` | you, within the agreed plan |
| `AI-USAGE.md` | the disclosure of meaningful AI assistance | you add entries; the student reviews them |
| `app/.env` | real settings and secrets | the student only (created with `cp .env.example .env`); you never create, read, edit, print or commit it |
| `app/.venv/`, `app/.browser-checks/` | the project's Python environment; browser-check screenshots | created by setup and checks; git-ignored |

## Skills (use them when their situation applies; the student can also type `/name`)

Each skill is a folder in `.claude/skills/<name>/` with a `SKILL.md`. Claude Code finds them there; so does Cline, according to its documentation.
If your tool does not load a skill automatically, open and follow `.claude/skills/<name>/SKILL.md` yourself.

`product-interview` (idea → documents → stack → skeleton), `build-feature` (plan and build one slice),
`design-interface` (screens and accessibility), `integrate-api` (external APIs and data inside the app),
`manage-data` (storage and schema changes), `test-and-check` (tests and calculation checks),
`debug-issue` (reproduce → fix → verify), `review-changes` (reviewer agents, fixes, stopping rule),
`prepare-deploy` (deployment readiness and handoff). Optional, only when `docs/product.md` needs them:
`add-accounts` (sign-in and permissions), `add-payments` (test-mode payments).

Reviewer instructions in `.claude/agents/` (`code-reviewer`, `test-reviewer`, `security-reviewer`, `ux-reviewer`)
describe read-only reviews that only report. Where the tool has subagents (Claude Code), they run as separate
reviewer agents. Where it does not (Cline's VS Code extension), follow "Without subagents" in `review-changes`.
Reviewers never edit; you fix findings through the skills and re-run the checks.

## Working rules

1. **Small, understandable changes.** One slice of `docs/plan.md` at a time; a few files per change. Plan the slice,
   get the student's go-ahead, then make routine edits within that plan without asking for each file. Ask again if
   the scope, the architecture, a paid service, personal data or a secret is involved. If the student delegates
   routine decisions, record the delegation (date, scope) in the decision log of `docs/architecture.md`; it never
   covers accepting a blocker or major risk, scope or expected-value changes, money, personal data or secrets.
2. **Keep the documents current.** After every change update slice status and the progress log in `docs/plan.md`,
   criteria statuses in `docs/acceptance.md`, and decisions in `docs/architecture.md`. If code and documents
   disagree, say so and ask which one is right.
3. **Record meaningful AI assistance** in `AI-USAGE.md`: design proposals, generated code, bugs found or fixed,
   reviews. Include mistakes you made that were caught. Not every typo.
4. **Secrets and settings.** Setting names go in `app/.env.example` with placeholders or safe development values,
   never real secrets. The student creates `app/.env` from it; you never create, read, edit, print, echo or log
   `.env`, never ask the student to paste a key into the chat, never put a key in code, tests, docs or a commit.
   Design settings so tests need no `.env`, unsafe options are off by default, and your own runs pass non-secret
   settings inline (`DEBUG=1 .venv/bin/python ...`). If a secret was committed, tell the student to revoke it.
5. **Test by risk** (`test-and-check`): calculations, data handling, permissions and payments get automated tests;
   screens get a journey check. Write the failing test first for logic and bugs; failing tests are normal while a
   slice is in progress, and a slice is complete only when they pass. Expected values for financial
   calculations are established independently of the code: written hand working or a cited source, recorded in
   `docs/acceptance.md`, never the app's own output.
6. **Git checkpoints.** After each verified slice, propose a commit with a clear message (`feat:`, `fix:`, `test:`,
   `docs:`). The student approves commits. Never push, force-push, rewrite history or change remotes unless the
   student asks. Team projects: one branch per slice and a pull request reviewed by a teammate.
7. **No unrequested scope.** Do not add features listed under "Explicitly not in the MVP", services, or libraries
   that the plan does not need.
8. **Never claim it works without checking it.** Generated code, a passing build or a server that starts are not
   proof. Run the tests and exercise the main user journey (see `test-and-check`). Keep three kinds of evidence
   apart: automated tests, the browser check (the project's own, installed in `app/`), and visual inspection
   (screenshots looked at, then the student's own look). If nothing can show the screen, give the student exact
   steps and report the journey as not verified.
9. **Stop and ask** when a requirement is unclear or contradictory, a check fails twice after two different fixes,
   something would cost money, or the student's request would break a rule above.
10. **One isolated environment.** Python projects use `app/.venv`, created with a supported Python version found
    on this machine (see `product-interview`, stacks). Never install into a base Anaconda, system or global
    Python, and never install system-wide tools without the student's agreement.
11. **Course and client rules** given by the student (data terms, AI policy, deadlines) override convenience. Ask
    when unsure.

## Change report (end every change with this)

```
What changed: <one to three sentences, for a non-programmer>
Files: <the main files touched>
How to preview: <exact command, URL, and what to click>
Tests: <commands run and results, e.g. "pytest: 14 passed, 0 failed">
Browser check: <command and result at which widths, or "not run" and why>
Looked at: <screenshots inspected by the assistant / the student's look: done or pending>
Not verified / still open: <honest gaps; review findings not fixed, with why (see review-changes)>
Next: <the suggested next step>
```

## This project (filled in by product-interview)

- Product: see `docs/product.md`
- Stack: `[not chosen yet]`
- Python environment: `[not set up yet]` (version, `app/.venv`)
- Install: `[not set up yet]`
- Run: `[not set up yet]`
- Test: `[not set up yet]`
- Browser check: `[not set up yet]`
