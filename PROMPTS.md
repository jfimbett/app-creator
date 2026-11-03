# Prompt sheet: Claude Code and Cline

The same skills, agents and review criteria serve both assistants. Only the way you call them differs. Results
depend on the model: a smaller model may need smaller requests, more retries and more help from you.

**Legend.** **used** = run while building App Creator (2026-11-03). **documented** = from the tool's official
documentation (Claude Code and Cline docs retrieved 2026-11-03), not yet run with this toolkit. **untested** = Cline:
no prompt on this sheet has been run with Cline in this build. Unless a row says otherwise, Claude Code prompts are
*documented* and Cline prompts *untested*.

Skills (15): `product-interview`, `plan-architecture`, `design-interface`, `build-feature`, `integrate-api`,
`manage-data`, `add-accounts`, `add-payments`, `test-and-check`, `debug-issue`, `review-changes`, `prepare-deploy`,
`git-collaboration`, `write-docs`, `orchestrate-steps`. When to use each: [.claude/skills/INDEX.md](.claude/skills/INDEX.md).

## Check that the assistant sees the project (do this first)

Both tools, same prompt:

```text
Do not change any file. Which file holds this project's rules, which skills can you see, and what must happen first in every session?
```

Expected answer: `AGENTS.md` (Claude Code reaches it through `CLAUDE.md`), a list that includes
`product-interview`, `build-feature` and `review-changes`, and "read `app-creator.config.json`; run the product
interview while the app's `product.md` is missing or not agreed".

## Calling the skills

Claude Code: type the prompt as shown. Cline (VS Code extension): start in **Plan** mode, type `/` and choose the
skill (its documentation lists `.claude/skills/` as a skills folder), add the same text, then switch to **Act**
after you agree with the plan. If a skill is not listed: `Follow .claude/skills/<name>/SKILL.md. <the same text>`.

| Step | Prompt |
|---|---|
| Product interview | `/product-interview My idea: <who it is for and what problem it solves>.` |
| Plan or change the architecture | `/plan-architecture <the endpoint, data, service or setting you want to add>` |
| Build the next slice | `/build-feature <what users should be able to do>` (or `/build-feature the next slice of plan.md`) |
| Design or change a screen | `/design-interface <the screen and what should change>` |
| Connect an API or data source | `/integrate-api <the service, what data, how fresh it must be>` |
| Save or cache data | `/manage-data <what must be kept between visits>` |
| Accounts (optional) | `/add-accounts <who signs in and what each role may see>` |
| Payments (optional, test mode) | `/add-payments <what is sold and how>` |
| Tests and calculation checks | `/test-and-check <the calculation or feature>` |
| Fix a problem | `/debug-issue <what you did, expected, happened, exact error>` |
| Review | Claude Code: `/review-changes` (reviewers run as separate read-only subagents, in parallel). Cline: see the review prompt below |
| Git and teamwork | `/git-collaboration <what you want to do, e.g. open a pull request>` |
| Docs | `/write-docs <which document and what changed>` |
| Prepare hand-in | `/prepare-deploy <where it should run, or "not decided">` |

## Calling an agent directly (Claude Code)

Agents in `.claude/agents/` (13): `project-orchestrator`, `delegated-product-owner`, `product-architect`,
`frontend-engineer`, `backend-engineer`, `design-lead`, `test-engineer`, `docs-writer`, `github-coach`,
`code-reviewer`, `test-reviewer`, `security-reviewer`, `ux-reviewer`.

```text
Use the github-coach agent: explain my git status and propose a safe way to share this branch.
```

Cline's VS Code extension has no subagents. Start a new task and paste
`Follow .claude/agents/<agent>.md. <your request>` (Cline then reads the file as instructions; it does not become
that agent).

## Review prompt for tools without subagents (Cline)

Start a **new task** in **Act** mode (auto-approve: only "Read project files") and paste, choosing one reviewer each
time (`code-reviewer`, `test-reviewer`, `security-reviewer`, `ux-reviewer`). Approve only read-only commands
(`git show`, `git diff`, `npm run verify`); refuse any file edit. (Cline's documentation says Plan mode cannot run
commands; if you review in Plan mode, paste the output of `git show HEAD` and of `npm run verify` yourself.)

```text
You are the <reviewer name>. Read .claude/agents/<reviewer name>.md and follow it exactly.
Scope: the last commit (git show HEAD), with the acceptance.md in the app's docs folder (app-creator.config.json, "docsDir") for the expected behaviour.
Do not edit any file; run only read-only commands. Return only the report in the format that file specifies.
```

Then, in your main task: `Here are the review reports. Follow review-changes from step 3.` and paste them.

If you cannot start a new task, use the same conversation (less independent; the reports must say so):

```text
Switch to reviewing only. Following "Without subagents" in review-changes, run the <reviewer name> review on the
last commit and return its report. Do not edit any file.
```

## Delegated mode (the owner writes a brief instead of answering)

Only when you, the owner, want the assistant to make routine product decisions for you (see
[docs/TOOLKIT.md](docs/TOOLKIT.md) §4). Write the brief first, for example `BRIEF.md`, and say in it what is
delegated. Money, publication, personal data, secrets, new scope and accepting a blocker are never delegated.

```text
/product-interview Delegated mode. The brief is BRIEF.md and it delegates routine product decisions. Use the delegated-product-owner agent to answer the interview from it, record each answer and its basis in the decisions file, and stop for anything the delegation does not cover.
```

## Orchestrated steps (recorded work for agents)

For larger work split into steps, each with a saved prompt and the agent's verbatim answer in `runs/`. Rules and
file formats: [orchestrate-steps](.claude/skills/orchestrate-steps/SKILL.md).

```text
/orchestrate-steps Plan the next slice of plan.md as recorded steps. Save each PROMPT.md before dispatching, and gate on npm run verify.
```

The dispatcher that sent the bootstrap steps of this build (**used**, see [runs/INDEX.md](runs/INDEX.md)):

```bash
node scripts/dispatch-step.mjs --step runs/<milestone>/<step-id> --agent <agent-name>
```

It needs the Claude Code CLI. In Cline, record steps by hand:
[manual-capture-cline.md](.claude/skills/orchestrate-steps/manual-capture-cline.md) (**untested**).

## When a smaller model struggles

- Ask for one thing at a time: one function, one test, one screen element.
- Start a new task when the conversation gets long, and say `Read AGENTS.md and the app's plan.md first.`
- If it loops or breaks things: stop, `git status`, `git diff`, and ask it to undo its last change, or use git
  yourself (`git restore <file>`).
- Paste the exact error text; ask it to run `npm run verify` and read the result before changing code.
