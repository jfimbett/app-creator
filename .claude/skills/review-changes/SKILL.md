---
name: review-changes
description: Use when someone asks for a review or audit, before merging, submitting or a milestone gate, after a large slice, or after any change to accounts, permissions, payments, secrets, external APIs or calculations.
---

# Review changes with the reviewer agents, then fix

Reviewers read and report; this workflow decides, fixes and re-checks. Reviewers never edit application code.

Paths: `<docs>` and `<frontend>` are `app.docsDir` and `app.frontendDir` in `app-creator.config.json`. Reviewer
instructions live in `.claude/agents/` (`code-reviewer`, `test-reviewer`, `security-reviewer`, `ux-reviewer`).

## Inputs

- What to review: a **completed increment**, meaning a slice or fix whose own tests pass. Prefer a committed
  snapshot, so later work does not leak into the review: `git show <hash>`, or `git diff <base>..<hash>` for
  several commits, or a branch compared with `main` (`git diff main...HEAD`). Uncommitted changes (`git diff`) or
  named files only when the student asks for a review before committing.
- The **working mode** (`docs/TOOLKIT.md` §4): interactive (default), or delegated by a written brief (for example
  `GOAL.md`) or a delegation recorded in the decision log of `<docs>/architecture.md`. See "Decisions" below.
- `<docs>/` (the reviewers read these themselves).

## Actions

1. **Pick reviewers by what changed** (all four for a full audit before submission):

   | Reviewer agent | When |
   |---|---|
   | `code-reviewer` | any code change |
   | `test-reviewer` | logic, calculations, data, or tests changed |
   | `security-reviewer` | settings, secrets, external APIs, storage, accounts, payments, uploads, deployment files |
   | `ux-reviewer` | screens, forms, flows, error messages |

2. **Run them** (in parallel as subagents where the tool has them; otherwise see "Without subagents"), each with:
   the scope (commit or diff command), the relevant acceptance criteria ids, the root commands (`npm run verify`
   for lint, tests, build and the Playwright journeys; `npm run demo` to look at the app offline), where the
   screenshots are (`<frontend>/test-results/`), and an instruction to use test or fixture data, never the
   owner's local database or `.env`.
   If you keep working test-first while a reviewer runs, name the tests that are deliberately failing for the next
   slice; the reviewer reports them under "Not checked", not as findings. Ask each for its standard report.
3. **Merge the findings** into one list, most severe first, removing duplicates. Keep each finding's label
   (`verified` or `suspected`). Show the list to the student (interactive) or record it in the step's handoff
   (delegated).
4. **Decide** what to fix now (see "Decisions" for who decides): all `blocker` findings, `major` findings unless the
   student accepts the risk in writing, `minor` findings when cheap. For a `suspected` finding, first confirm or
   dismiss it with a check (a test, a reproduction), and record which.
5. **Fix** each chosen finding with the matching skill (`debug-issue` for defects, `test-and-check` for missing
   tests, `design-interface` for usability), each with a check that proves it.
6. **Commit the fixes** (after the student's approval; in delegated mode within the delegated scope, see below),
   then **re-run only the reviewers whose areas were touched**,
   scoped to the fix commits. A re-review of a small fix diff can use a faster, cheaper model setting if the
   student's tool offers one.
7. **Record** in `<docs>/plan.md` (progress log): reviewers run, findings by severity, fixed, dismissed, accepted, open.
   Copy every finding that is not fixed into "Known problems" using the format below. Add a line to `AI-USAGE.md`.

## Without subagents (for example Cline's VS Code extension)

A subagent is a separate assistant with its own fresh context and, here, read-only tools: it does not see your
reasoning, so it reviews the work rather than your intentions. Without subagents, use the most independent option
available, and say in the report which one was used:

1. **Separate task per reviewer (preferred).** The student starts a new task or conversation (fresh context) and
   pastes the review prompt from `PROMPTS.md` with the reviewer's name. The reviewer reads
   `.claude/agents/<name>.md` and returns only its report. Repeat for each reviewer, one after the other. The
   student pastes the reports back into the main task. A reviewer must be able to run read-only commands
   (`git show`, the test command) to mark findings `verified`. In Cline, use **Act** mode with auto-approve limited
   to reading files, and approve only those read-only commands; refuse any file edit. (Cline's documentation says
   **Plan** mode cannot run commands; in Plan mode, paste the output of `git show HEAD` and of the test command into
   the task yourself, and findings without a run stay `suspected`.)
2. **Sequential review in the same conversation (fallback).** Switch to a mode that cannot edit files, then for each
   reviewer: read `.claude/agents/<name>.md`, apply its checklist to the scope, write its report in its format, and
   only then move to the next. This reviewer has seen how the code was written, so it is less independent: label
   the reports "same-conversation review" and do not call them independent.

Either way, do not edit any file during the review; fixes happen only in step 5, in the main task.

## Decisions: interactive or delegated (`docs/TOOLKIT.md` §4)

**Interactive (default).** Show the merged list and ask before fixing; the student approves each commit.

**Delegated.** The owner has written a brief that explicitly delegates routine decisions (for example a
`GOAL.md`, used by `delegated-product-owner` and gated by `project-orchestrator`), or the student said "decide
routine review fixes yourself" and that delegation is recorded once, with date and scope, in the decision log of
`<docs>/architecture.md`. Under it you may, without asking each time:

- fix blockers, majors and cheap minors with the matching skill, each with its check;
- dismiss a `suspected` finding that a check disproved (record the check);
- leave a minor finding for a named later slice, with a reason;
- commit the fixes inside the delegated scope (one commit per finding or small group, clear `fix:` messages).

Each such decision still appears in the report, in `<docs>/plan.md`, and (delegated runs) in the step's handoff.

The delegation **never** covers, so stop and ask, or record a blocker in the handoff when nobody can answer:

- accepting a blocker or a major as a known risk, or any blocker at all;
- new scope, or changes to acceptance criteria or expected values;
- money (a paid service, a paid tier, live payment keys);
- publication: push, pull request merge, tag, release, deployment, anything public;
- personal data, and secrets (new secrets, exposed secrets, rotation);
- architecture changes and any rule in `AGENTS.md`.

## Reporting findings that stay open

Every finding not fixed is reported, in the change report and under "Known problems" in `<docs>/plan.md`:

```
| Finding | Severity | Status | Why still open | Decided by | Next step |
| security-reviewer #2: no rate limit on sign-in | major | verified | accepted risk for the laptop demo; must be fixed before deployment | student, 2026-11-02 | prepare-deploy |
```

"Why still open" is one of: accepted risk (who accepted it), deferred to a named slice, dismissed with the check
that disproved it, or not fixed after two rounds (what was tried). Never drop a finding silently.

## Outputs

The merged findings list, fixes with checks, the re-review result, updated `<docs>/plan.md`, a change report.

## Verification

- Every blocker is fixed and its check passes, or it is listed as open with the reason.
- The re-run reviewers report no new blockers in the changed areas.

## Stop when (stopping rule)

- No open blockers, and every major finding is fixed or accepted by the student (never by a delegation): done.
- **At most two fix-and-re-review rounds.** If blockers remain after the second round, stop fixing. Report each
  remaining blocker with its evidence, what was tried, and the options (change scope, ask the instructor or a
  teammate, accept and document the risk). Never mark the work finished while a blocker is open.

## Common mistakes

- Letting a reviewer edit files, or editing a reviewer's report to make findings disappear.
- Fixing twenty minor findings in one commit.
- Treating a `suspected` finding as proven, or ignoring it without a check.
- Reviewing a working tree full of deliberately failing tests and treating them as findings.
- Calling a same-conversation review "independent", or editing files while reviewing.
- Using a delegation to accept a major risk on the student's behalf, or to push or publish.

## Example

A slice adds an external statistics API (commit `a1b2c3d`). Reviewers: `code-reviewer`, `test-reviewer`,
`security-reviewer` (external API, settings), `ux-reviewer` (new error message), scoped to `git show a1b2c3d`.
Merged list: security #1 `blocker verified` (the route forwards any `url` query parameter: arbitrary proxy);
test #1 `major verified` (no test for 429 handling); ux #1 `minor suspected` (error text hard to read at 390 px).
Delegated mode: fix security #1 with an allowlist plus a refusal test, add the 429 test, check ux #1 on the
390 px screenshot: readable, so dismissed with that check. Commit `fix: restrict stats client to allowlisted
paths` and `test: cover rate-limited stats responses`; re-run `security-reviewer` and `test-reviewer` on those
commits: no new findings. Record in `<docs>/plan.md`; nothing left open. In interactive mode the same list is
shown to the student first.
