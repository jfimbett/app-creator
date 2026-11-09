# App Creator

> **In class?** Start with [CLASSROOM.md](CLASSROOM.md). `main` contains the latest SEC Analytics example, M6 (tag `m6`).

App Creator is a starter for building a web application with an AI coding assistant. It gives the assistant
working rules, 15 skills (step-by-step instructions for planning, building, testing, reviewing and shipping) and
13 specialist agents, plus four root commands that install, run and check the app the same way on macOS and
Windows. **Claude Code** is the main route; **Cline** (a VS Code extension) is documented but untested in this
build.

It was made for a business-school programming and AI course. Students first **inspect** a prepared example app,
SEC Analytics, in six versions, and later **start their own** app from the generic starter.

New here? Read [START-HERE.md](START-HERE.md). It walks you through both paths step by step.

## Branches and tags

A **tag** is a fixed, named version; a **branch** is a line of work that can move. Every published version has both:
the tag is the reference you check out, the branch of the same name points at the same commit.

| Branch | Tag | What it holds | Brief and records |
|---|---|---|---|
| `template` | `template-v1` | the generic toolkit and a tiny walking-skeleton app (`scaffold/`). **No SEC application.** Start a new, unrelated app here. | [runs/bootstrap](runs/bootstrap) |
| `milestone/01-foundation` | `m1` | SEC Analytics M1: dark shell, search, profile, revenue and net income from recorded SEC data | [01-foundation](milestones/01-foundation/README.md) |
| `milestone/02-financial-intelligence` | `m2` | + Demo/Live, statement summaries, ratios, metric explorer | [02-financial-intelligence](milestones/02-financial-intelligence/README.md) |
| `milestone/03-filing-intelligence` | `m3` | + filings, the 10-K/10-Q reader with sections and search | [03-filing-intelligence](milestones/03-filing-intelligence/README.md) |
| `milestone/04-comparative-analysis` | `m4` | + Compare 2–4 companies, indexing, CSV export | [04-comparative-analysis](milestones/04-comparative-analysis/README.md) |
| `milestone/05-ai-financial-analyst` | `m5` | + the optional AI analyst with your own OpenRouter key | [05-ai-financial-analyst](milestones/05-ai-financial-analyst/README.md) |
| `milestone/06-polish-and-launch` | `m6` | + dark and light themes, the redesigned interface, a landing page at `/` (app at `/app`), a launch video | [06-polish-and-launch](milestones/06-polish-and-launch/README.md) |
| `main` | (none) | the newest milestone plus later documentation commits; today the same as `m6` plus its records | [PROGRESS.md](PROGRESS.md) |
| `wip/m3-filing-intelligence-unverified` | (none) | history only: M3 as it stood when a classroom freeze stopped it, before any browser check. Use `m3` instead. | [m3-03 record](runs/m3/m3-03-classroom-freeze/PROMPT.md) |

Each version keeps everything earlier ones did. Every prompt given to an assistant for a milestone, the exact brief, its
follow-ups and the step records, is listed in [milestones/PROMPT-INDEX.md](milestones/PROMPT-INDEX.md). Branches named
`work/…` or `exercise/…` exist only on the computer that made them and are never published.

## Path A: inspect the prepared SEC Analytics milestones

```bash
git clone https://github.com/jfimbett/app-creator.git app-creator
cd app-creator
git fetch origin --tags
git switch --detach m1        # or m2 … m6
npm ci
npm run setup
npm run demo                  # offline demo, no keys, no network
```

## Path B: start a new app from the generic starter

```bash
git clone --branch template <repository-url> my-app   # or: --branch template-v1
cd my-app
npm ci                  # once: prepares the root launcher
npm run setup           # no app yet: checks Node and Python, prints next steps
npm run create-app      # copies scaffold/ to app/ and points app-creator.config.json at it
npm run setup           # now installs the new app (Python .venv, node_modules, test browser)
claude                  # start Claude Code in this folder
```

Then, inside Claude Code:

```text
/product-interview My idea: <who it is for and what problem it solves, in one or two sentences>.
```

The interview asks a few questions at a time, writes four documents in `app/docs/` (product, architecture,
acceptance criteria, plan) and waits for your agreement before writing code. You can also skip `create-app` and
run `/product-interview` first: it creates the app the same way.

_Checked 2026-11-03 on macOS, Node 22.14, Python 3.10, in template mode: `npm ci`, `npm run setup`, `npm run dev`,
`npm run demo` (each prints "No app is configured yet" with next steps, exit 0), `npm run create-app -- --dry-run`
and `npm run verify` (all checks passed, including the scaffold copied, installed, built and browser-tested in a
temporary folder). Not verified in this build: cloning from the published repository, and running a real
`npm run create-app` followed by `npm run dev`._

## Requirements

- **git**
- **Node.js 22.13 or newer** (`node --version`), which includes npm
- **Python 3.10 to 3.13** (`python3 --version`; on Windows `py -0p`). `npm run setup` finds a supported one and
  creates a private environment for the app, so your system or Anaconda Python is never changed. Set `APP_PYTHON`
  to choose one yourself (see [.env.example](.env.example)).
- **Claude Code** (an account whose plan includes it) or **Cline** with a model API key.

## The four commands

Run them from the repository root. They read `app-creator.config.json` to find the app.

| Command | What it does | Before an app exists |
|---|---|---|
| `npm run setup` | checks versions, creates the backend's Python `.venv`, installs locked packages and the test browser; safe to repeat | checks versions, prints next steps |
| `npm run dev` | starts the backend and the website (default http://127.0.0.1:3000); Ctrl+C stops both | prints next steps |
| `npm run demo` | like `dev`, with the app's demo settings (for example offline data) | prints next steps |
| `npm run verify` | toolkit checks, lint, type checks, tests, production build and a browser smoke test; fails loudly | toolkit checks plus a full check of `scaffold/` |

Also: `npm run create-app` (create the app from `scaffold/`) and `npm run check-toolkit` (toolkit checks only).
The full contract is in [docs/TOOLKIT.md](docs/TOOLKIT.md) §3. Optional settings (ports, Python) are listed in
[.env.example](.env.example); copy it to `.env` and edit your copy if you need them.

## What is in the toolkit

| Part | Where | More |
|---|---|---|
| Working rules for every assistant | [AGENTS.md](AGENTS.md); Claude Code notes in [CLAUDE.md](CLAUDE.md); Cline notes in [.clinerules/cline.md](.clinerules/cline.md) | |
| 15 skills | `.claude/skills/<name>/SKILL.md` | [.claude/skills/INDEX.md](.claude/skills/INDEX.md) |
| 13 agents (orchestration, builders, GitHub coach, 4 read-only reviewers) | `.claude/agents/` | [agents table in INDEX.md](.claude/skills/INDEX.md#agents-claudeagents) |
| Prompt sheet for Claude Code and Cline | [PROMPTS.md](PROMPTS.md) | |
| Walking-skeleton app (Next.js + FastAPI) | `scaffold/` | [scaffold/README.md](scaffold/README.md) |
| Root commands | `scripts/` | [docs/TOOLKIT.md](docs/TOOLKIT.md) |
| Record of AI assistance | [AI-USAGE.md](AI-USAGE.md) | |
| Step records of delegated work | `runs/` | [orchestrate-steps](.claude/skills/orchestrate-steps/SKILL.md) |
| App Creator's own documentation | `docs/` | [docs/README.md](docs/README.md) |

## License

MIT, see [LICENSE](LICENSE).
