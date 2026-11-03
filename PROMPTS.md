# Prompt sheet: Claude Code and Cline

The same skills, templates and review criteria serve both assistants. Only the way you call them differs.
Results depend on the model: a smaller model may need smaller requests, more retries and more help from you.

Legend: **tested** = run by the instructor with this starter; **documented** = from the tool's official documentation
on 2026-11-02, not yet run with this starter.

## Check that the assistant sees the project (do this first)

Both routes, same prompt:

```text
Do not change any file. Which file holds this project's rules, which skills can you see, and what must happen first in every session?
```

Expected answer: `AGENTS.md` (Claude Code reaches it through `CLAUDE.md`), a list that includes
`product-interview`, `build-feature` and `review-changes`, and "run the product interview if `docs/product.md` is
not agreed".

## Calling the main steps

| Step | Claude Code | Cline (VS Code extension) |
|---|---|---|
| Product interview | `/product-interview My idea: <who it is for and what problem it solves>.` (tested) | Plan mode. Type `/`, choose `product-interview`, add `My idea: ...` (documented). If it is not listed: `Follow .claude/skills/product-interview/SKILL.md. My idea: ...` |
| Build the next slice | `/build-feature <what users should be able to do>` | Plan mode: `/build-feature <...>`; reply "go" and switch to Act after you agree with the plan |
| Design or change a screen | `/design-interface <the screen and what should change>` | same, starting in Plan mode |
| Tests and calculation checks | `/test-and-check <the calculation or feature>` | same |
| Fix a problem | `/debug-issue <what you did, expected, happened, exact error>` | same |
| Review | `/review-changes` (reviewers run as separate read-only subagents, in parallel) | No subagents: one **new task** per reviewer, in Act mode with auto-approve on reading only, with the review prompt below; approve only `git show`, `git diff` and the test command, refuse any edit. Paste each report back into your main task |
| Prepare hand-in | `/prepare-deploy <where it should run, or "not decided">` | same |

## Review prompt for tools without subagents (Cline)

Start a **new task** in **Act** mode (auto-approve: only "Read project files") and paste, choosing one reviewer each
time (`code-reviewer`, `test-reviewer`, `security-reviewer`, `ux-reviewer`). Approve only read-only commands
(`git show`, `git diff`, the test command); refuse any file edit. (Cline's documentation says Plan mode cannot run
commands; if you review in Plan mode, paste the output of `git show HEAD` and of the tests into the task yourself.)

```text
You are the <reviewer name>. Read .claude/agents/<reviewer name>.md and follow it exactly.
Scope: the last commit (git show HEAD), with docs/acceptance.md for the expected behaviour.
Do not edit any file; run only read-only commands. Return only the report in the format that file specifies.
```

Then, in your main task: `Here are the review reports. Follow review-changes from step 3.` and paste them.

If you cannot start a new task, use the same conversation (less independent; the reports must say so):

```text
Switch to reviewing only. Following "Without subagents" in review-changes, run the <reviewer name> review on the
last commit and return its report. Do not edit any file.
```

## When a smaller model struggles

- Ask for one thing at a time: one function, one test, one screen element.
- Start a new task when the conversation gets long, and say `Read AGENTS.md and docs/plan.md first.`
- If it loops or breaks things: stop, `git status`, `git diff`, and ask it to undo its last change, or use git
  yourself (`git restore <file>`).
- Paste the exact error text; ask it to run the test command and read the result before changing code.
