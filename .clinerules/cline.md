# Cline only

The shared rules are in `AGENTS.md` (Cline reads it). Follow them; this file only adds what differs in Cline.
Compatibility with Cline is **untested** in this build of App Creator: these notes come from Cline's documentation
(retrieved 2026-11-03, see `docs/research/claude-code-and-cline.md`) and from a rehearsal with the earlier starter.

- **Paths:** read `app-creator.config.json` first. The app's code and documents are where it says (`app.frontendDir`,
  `app.backendDir`, `app.docsDir`; default `app/frontend`, `app/backend`, `app/docs`). `"app": null` means no app
  yet: start with the `product-interview` skill.
- **Commands:** run them from the repository root: `npm ci` (once), `npm run setup`, `npm run dev`, `npm run demo`,
  `npm run verify`, `npm run create-app`. They are the same on macOS and Windows (`docs/TOOLKIT.md` §3). Do not
  install packages any other way.
- **Skills** are the folders in `.claude/skills/` (index: `.claude/skills/INDEX.md`). Cline's documentation lists
  `.claude/skills/` as a project skills folder, so they should appear when the owner types `/`. If a skill is not
  offered, open `.claude/skills/<name>/SKILL.md` and follow it exactly. A global Cline skill with the same name
  wins over the project's.
- **Agents and reviewers:** Cline's VS Code extension has no subagents and does not run `.claude/agents/` as
  agents. A new task can follow an agent file as instructions. For reviews, follow "Without subagents" in
  `.claude/skills/review-changes/SKILL.md`: preferably one new task per reviewer, using the review prompt in
  `PROMPTS.md`. As a reviewer, never edit a file; ask before every command and run only read-only ones (`git show`,
  `git diff`, `npm run verify`). Never call a review done in this same conversation "independent".
- **Recorded steps:** `scripts/dispatch-step.mjs` needs the Claude Code CLI. In Cline, record a step by hand with
  `.claude/skills/orchestrate-steps/manual-capture-cline.md`, and mark it as manual capture.
- **Plan and Act:** plan in **Plan** mode; switch to **Act** only after the owner agrees with the plan. Plan mode
  does not edit files, but it can still propose commands (seen in the instructor's rehearsal with Cline 4.1.26): in
  Plan mode propose only read-only commands, and say what each one does.
- **Python:** `npm run setup` finds a supported Python (3.10–3.13) and creates the backend's `.venv`. If it picks
  the wrong one or finds none (Anaconda is often not on the terminal's PATH), the owner sets `APP_PYTHON` to the
  full path of the interpreter in their own `.env` (see `.env.example`). Never install into a base Anaconda or
  system Python.
- **Permissions:** Cline has no per-command allow list, and `.claude/settings.json` does not apply to Cline. Ask
  before every command that installs, deletes, starts a server or changes git, even if auto-approve would let you
  run it. Never push, force-push, `git reset --hard` or `git clean`.
- **Secrets:** never open, mention with `@`, `cat`, print or edit `.env` files. `.clineignore` only keeps them out
  of automatic context; it does not stop a command from reading them. The API key for the model lives in Cline's
  settings, never in this folder.
