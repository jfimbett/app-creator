# Start here: build your application with an AI coding assistant

## What this folder gives you

A ready-made workspace for building your own application with an AI coding assistant, from idea to a version you
can hand in. It works with **Claude Code** and with **Cline** (a VS Code extension). Both read the same instructions,
skills, templates and review criteria.

- **A product interview** that asks what your users should see and do (including whether you want a dashboard
  with cards and charts), turns your idea into four short documents (product, architecture, acceptance
  criteria, plan) and recommends a simple stack: a **dashboard** for data and analysis tools, or a
  **customer-facing web app** when users must sign in, save data or pay.
- **Skills** (`.claude/skills/`) that guide the assistant through the work: building features, designing screens,
  connecting APIs, storing data, testing calculations, debugging, optional accounts and payments, and preparing
  deployment.
- **Four reviewers** (`.claude/agents/`: code, tests, security, usability) that check the work and report problems.
- **Working rules** in `AGENTS.md`: small changes, honest test results, secrets kept out of git, and an
  `AI-USAGE.md` record of how AI helped. `CLAUDE.md` and `.clinerules/cline.md` only add what differs per tool.
- **A prompt sheet**, `PROMPTS.md`, with the exact prompts for both tools.

Your application will live in `app/`, and its documents in `docs/`. Nothing there exists yet: the interview creates it.

## What you need (both routes)

- **git** (`git --version` in a terminal should print a version) and **VS Code**.
- **Python 3.11 or later** for the recommended stacks. Check with `python --version` **and** `python3 --version`
  (Windows: `py -0p`): they can be different installations, and on a Mac `python3` may be an old 3.9. The
  assistant looks for a supported version and creates a separate environment for your project in `app/.venv`, so
  your Anaconda or system Python is never changed.

## Choose your route

| | Route A: Claude Code | Route B: Cline |
|---|---|---|
| What it is | Anthropic's coding assistant, in a terminal | an open-source VS Code extension that uses a model you choose through an API key |
| You need | an account whose plan includes Claude Code (the free Claude.ai plan did not on 2026-11-01) | an API key with a spending limit (in this course: the key your instructor gives you) |
| Install | follow https://code.claude.com/docs | VS Code → Extensions (`Ctrl/Cmd+Shift+X`) → search **Cline** → Install |
| Reviewers | separate read-only reviewer agents, run in parallel | no subagents in the VS Code extension: one new task per reviewer, approving only read-only commands (see `PROMPTS.md`) |
| Permissions | set by this folder (`.claude/settings.json`) | set by you in Cline's auto-approve menu (below) |

Results depend on the model behind the assistant. A smaller, cheaper model can do the same steps but needs smaller
requests and more checking.

## Open it

1. **Copy or unzip** this folder somewhere that is **not inside another project** (for example
   `Documents/my-app`). Assistants also read instruction files from folders above this one. Files starting with a
   dot (`.claude`, `.clinerules`, `.gitignore`) may be hidden in Finder or Explorer. Keep them.
2. Open the folder in VS Code (*File → Open Folder…*).

### Route A: Claude Code

Open a terminal in VS Code (*Terminal → New Terminal*) and run:

```bash
claude
```

When it asks whether you trust this folder, answer **yes**. Otherwise the project's settings are not applied.
If it offers to use a browser extension or your own browser, you can answer **no**: the project installs its own
browser check.

**Permissions.** Claude may edit files inside the folder without asking each time. It runs the project's tests and
checks without asking, but asks before installing packages, starting the app, deleting files, every commit, and any
change to `.claude/settings.json`. Reading or editing `.env` files is blocked. Never switch to a mode that bypasses
all permissions.

### Route B: Cline

1. Open the Cline panel (its icon in the left bar).
2. In Cline's settings, choose the **API provider** and paste your **API key** there, then choose the **model** your
   instructor names. The key is stored by Cline, outside this folder. Never put it in a file of this project, never
   paste it into the chat, and never share it.
3. **Auto-approve:** turn on only **Read project files**. Leave editing, commands, browser and MCP off, and never turn
   on **YOLO mode**. Cline will then ask before every edit and every command: read what it wants to run before you
   click Approve.
4. Use **Plan** mode to discuss a plan (it cannot change files), and **Act** mode to let it work after you agree.
   For reviews, see `PROMPTS.md`.

Cline reads `AGENTS.md` and `.clinerules/`, and its documentation says it finds skills in `.claude/skills/`. If a
skill does not appear when you type `/`, ask it to follow `.claude/skills/<name>/SKILL.md`.

## Check that it works (both routes)

```text
Do not change any file. Which file holds this project's rules, which skills can you see, and what must happen first in every session?
```

It should name `AGENTS.md`, list skills such as `product-interview`, and say that the product interview comes first.

## Your first prompt

Route A: type this, replacing the part in angle brackets. Route B: in Plan mode, type `/`, choose
`product-interview`, then add the same text.

```text
/product-interview My idea: <who it is for and what problem it solves, in one or two sentences>.
```

The assistant asks a few questions at a time. Then it proposes the screens, the documents and a stack, and waits for
your agreement before it writes any code. After that it sets up a first version that runs.

## Afterwards

| You want to | Type (Route B: start in Plan mode) |
|---|---|
| Run the app | `How do I run the app?` (the commands are also in `app/README.md` once it exists) |
| Check the screens in a real browser | `Set up and run the browser check.` (screenshots appear in `app/.browser-checks/`) |
| Add or change a feature | `/build-feature <what users should be able to do>` |
| Fix something | `/debug-issue <what you did, what you expected, what happened, the exact error>` |
| Review the work | Route A: `/review-changes`. Route B: the review prompt in `PROMPTS.md` |
| Prepare deployment or hand-in | `/prepare-deploy <where it should run, or "not decided">` |
| See where you are | `Summarise docs/plan.md: what is done, what is next, what is open.` |

Every change ends with a short report: what changed, how to preview it, which tests ran, what the browser check
found, what was looked at, and what is still open. Passing tests do not show that a screen looks right: open
the app yourself, try it on a narrow window too, and commit when you are satisfied.

## Good to know

- Personal skills or settings with the same names as the ones here may be used instead of this folder's.
- **Settings and keys for your app:** when the setup says so, create your settings file yourself: in `app/`, run
  `cp .env.example .env` (Windows: `copy .env.example .env`), then put your own values in `app/.env` with an
  editor. The assistant never reads or writes that file. Never paste keys or passwords into the chat.
- **If a key leaks** (committed, pasted, shared): revoke it at the provider first, then remove it from the files.
- If the app says the port is busy, ask the assistant to start it on another port (for example 8001).
- Want to undo a change? Ask the assistant, or use git: every checkpoint is a commit.
