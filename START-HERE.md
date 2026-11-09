# Start here: build an application with an AI coding assistant

## What this repository gives you

A ready-made workspace for building a web application with an AI coding assistant, from idea to a version you can
hand in. It works with **Claude Code** (the main, tested route) and with **Cline**, a VS Code extension (documented,
not tested in this build). Both read the same rules, skills and review criteria.

- **A product interview** that asks who your users are and what they should see and do (for example a dashboard
  with cards and charts), then writes four short documents: product, architecture, acceptance criteria and plan.
- **Skills** (`.claude/skills/`, listed in [INDEX.md](.claude/skills/INDEX.md)): step-by-step instructions the
  assistant follows to plan, design screens, build features, connect APIs, store data, test, debug, review, use
  git with a team, write docs and prepare a hand-in. Accounts and payments are optional skills.
- **Agents** (`.claude/agents/`): specialists such as a frontend or backend engineer, and four **reviewers** (code,
  tests, security, usability) that only report problems.
- **Working rules** in [AGENTS.md](AGENTS.md): small changes, honest test results, secrets kept out of git, and an
  [AI-USAGE.md](AI-USAGE.md) record of how AI helped.
- **Four commands** that install, run and check the app: `npm run setup`, `npm run dev`, `npm run demo`,
  `npm run verify` ([README.md](README.md#the-four-commands)).
- **A prompt sheet**, [PROMPTS.md](PROMPTS.md), with the exact prompts for both tools.

## Two paths

- **Path A: look at a finished example.** SEC Analytics, a financial dashboard built with this toolkit in six
  versions (milestones `m1`–`m6`), lives on the `main` branch and the `milestone/…` branches (one per tag). It is
  not on the `template` branch. The branches are explained in [README.md](README.md#branches-and-tags).
- **Path B: build your own app.** Start from the `template` branch (or the `template-v1` tag). It contains the
  toolkit and a tiny working app to grow, and no SEC code.

## What you need (both paths)

- **git**: `git --version` in a terminal should print a version.
- **Node.js 22.13 or newer**: `node --version`. Install it from https://nodejs.org if it is missing or older.
- **Python 3.10 to 3.13**: check with `python --version` **and** `python3 --version` (Windows: `py -0p`). They can
  be different installations, and on a Mac `python3` may be an old 3.9. `npm run setup` looks for a supported
  version and creates a private environment for the app (a `.venv` folder), so your Anaconda or system Python is
  never changed.
- **VS Code** (recommended for both routes, required for Cline).

## Get the code

Put the folder somewhere that is **not inside another project** (for example `Documents/my-app`): assistants also
read instruction files from the folders above. Files starting with a dot (`.claude`, `.clinerules`, `.gitignore`)
may be hidden in Finder or Explorer. Keep them.

**Path A:**

```bash
git clone https://github.com/jfimbett/app-creator.git app-creator
cd app-creator
git fetch origin --tags
git switch --detach m1        # look at milestone 1; later m2 … m6
npm ci
npm run setup
npm run demo
```

Before switching to another milestone: stop the app with **Ctrl+C**, run `git status` and keep or commit any
edits you made, then switch and run `npm run setup` again (packages can change between versions).

**Path B:**

```bash
git clone --branch template <repository-url> my-app
cd my-app
npm ci
npm run setup
```

`<repository-url>` is the address your instructor gives you. `npm ci` prepares the root commands (once).
`npm run setup` checks Node and Python. With no app yet it prints **"No app is configured yet"** and two ways to
start. That is expected.

_Checked 2026-11-03 on macOS (Node 22.14, Python 3.10) in an existing checkout of this branch: `npm ci` and
`npm run setup` both exit 0 with that message. Cloning from the published repository was not verified._

**If it fails:**
- `Node <version> is too old; App Creator needs Node 22.13 or newer`: install a newer Node, open a new terminal,
  retry.
- `no supported Python found`: install Python 3.12 from https://python.org, or point `APP_PYTHON` at one (copy
  `.env.example` to `.env` and set it there; see the comments in [.env.example](.env.example)).

## Choose your assistant

| | Route 1: Claude Code | Route 2: Cline |
|---|---|---|
| What it is | Anthropic's coding assistant, in a terminal | an open-source VS Code extension that uses a model you choose through an API key |
| You need | an account whose plan includes Claude Code (the free Claude.ai plan did not on 2026-11-01) | an API key with a spending limit (in a course: the key your instructor gives you) |
| Install | follow https://code.claude.com/docs | VS Code → Extensions (`Ctrl/Cmd+Shift+X`) → search **Cline** → Install |
| Rules it reads | `CLAUDE.md`, which imports `AGENTS.md` | `AGENTS.md` and `.clinerules/` |
| Skills | `/name` | `/name`, per Cline's documentation (it lists `.claude/skills/`) |
| Agents and reviewers | separate subagents; reviewers run in parallel | no subagents in the VS Code extension: one new task per reviewer (see [PROMPTS.md](PROMPTS.md)) |
| Permissions | set by this folder (`.claude/settings.json`) | set by you in Cline's auto-approve menu (below) |
| Status in this build | used to build the toolkit | **untested**: compatibility is from Cline's documentation only |

Results depend on the model behind the assistant. A smaller, cheaper model can do the same steps but needs smaller
requests and more checking.

### Route 1: Claude Code

Open the folder in VS Code (*File → Open Folder…*), open a terminal (*Terminal → New Terminal*) and run:

```bash
claude
```

When it asks whether you trust this folder, answer **yes**. Otherwise the project's settings are not applied.
If it offers to use a browser extension or your own browser, you can answer **no**: the project installs its own
test browser.

**Permissions.** Claude may edit files inside the folder without asking each time. It runs the project's tests and
`npm run verify` without asking, but asks before installing packages, starting the app, deleting files, every
commit, and any other command. Reading or editing `.env` files, force-pushing, `git reset --hard` and `git clean`
are blocked. Never switch to a mode that bypasses all permissions.

### Route 2: Cline

1. Open the folder in VS Code and open the Cline panel (its icon in the left bar).
2. In Cline's settings, choose the **API provider**, paste your **API key** there, and choose the **model** your
   instructor names. The key is stored by Cline, outside this folder. Never put it in a file of this project, never
   paste it into the chat, and never share it.
3. **Auto-approve:** turn on only **Read project files**. Leave editing, commands, browser and MCP off, and never
   turn on **YOLO mode**. Cline will then ask before every edit and every command: read what it wants to run before
   you click Approve.
4. Use **Plan** mode to discuss a plan (it does not change files), and **Act** mode to let it work after you agree.

Cline reads `AGENTS.md` and `.clinerules/`. It does not run Claude Code's subagents, and its slash commands are not
identical to Claude Code's. If a skill does not appear when you type `/`, ask it to follow
`.claude/skills/<name>/SKILL.md`. Reviews run as separate tasks ([PROMPTS.md](PROMPTS.md)).

## Check that it works (both routes)

```text
Do not change any file. Which file holds this project's rules, which skills can you see, and what must happen first in every session?
```

It should name `AGENTS.md` (Claude Code reaches it through `CLAUDE.md`), list skills such as `product-interview`,
`build-feature` and `review-changes`, and say that it first reads `app-creator.config.json` and runs the product
interview while no agreed product document exists.

## Your first prompt (Path B)

Route 1: type this, replacing the part in angle brackets. Route 2: in Plan mode, type `/`, choose
`product-interview`, then add the same text.

```text
/product-interview My idea: <who it is for and what problem it solves, in one or two sentences>.
```

The assistant asks a few questions at a time. Then it proposes the screens, the documents and the stack, and waits
for your agreement before it writes code. It then creates the app (`npm run create-app` copies the tiny starter app
to `app/`), installs it with `npm run setup`, and checks it with `npm run verify`. Your app's documents go to
`app/docs/`.

Prefer to see the tiny app first? Run `npm run create-app`, `npm run setup`, then `npm run dev`, and open
http://127.0.0.1:3000: the page shows a **Backend status** panel that should say **OK**. Stop it with Ctrl+C.
_Not verified by hand in this build; `npm run verify` checks the same starter app (install, build, browser test)
and passed on 2026-11-03._

## Afterwards

| You want to | Type (Route 2: start in Plan mode) |
|---|---|
| Run the app | `npm run dev` in a terminal, or ask `How do I run the app?` |
| Check everything (tests, build, browser) | `npm run verify` (screenshots go to `app/frontend/test-results/`) |
| Add or change a feature | `/build-feature <what users should be able to do>` |
| Change how a screen looks | `/design-interface <the screen and what should change>` |
| Fix something | `/debug-issue <what you did, what you expected, what happened, the exact error>` |
| Review the work | Route 1: `/review-changes`. Route 2: the review prompt in [PROMPTS.md](PROMPTS.md) |
| Work with git or a team | `/git-collaboration <what you want to do>` |
| Prepare deployment or hand-in | `/prepare-deploy <where it should run, or "not decided">` |
| See where you are | `Summarise app/docs/plan.md: what is done, what is next, what is open.` |

Every change ends with a short report: what changed, how to preview it, which tests ran, what the browser check
found, what was looked at, and what is still open. Passing tests do not show that a screen looks right: open the
app yourself, try a narrow window too, and commit when you are satisfied.

## Good to know

- Personal skills or settings with the same names as the ones here may be used instead of this folder's.
- **Settings and keys:** the setting names are in `.env.example`. If you need them, create your own settings
  file yourself: `cp .env.example .env` (Windows: `copy .env.example .env`), then put your values in `.env` with an
  editor. The assistant never reads or writes that file, and git ignores it. Never paste keys or passwords into the
  chat.
- **If a key leaks** (committed, pasted, shared): revoke it at the provider first, then remove it from the files.
- **`port 8000 (...) is already in use`:** the commands never stop other programs. Close the other app, or choose
  other ports: `BACKEND_PORT=8001 FRONTEND_PORT=3001 npm run dev` on macOS/Linux, or set `BACKEND_PORT` and
  `FRONTEND_PORT` in `.env` (works on Windows too).
- **Undo a change:** ask the assistant, or use git: every checkpoint is a commit. Avoid `git reset --hard`; ask
  `/git-collaboration` for a safe way.
- More about the toolkit itself: [docs/README.md](docs/README.md).
