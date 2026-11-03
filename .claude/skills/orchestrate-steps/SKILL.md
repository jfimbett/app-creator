---
name: orchestrate-steps
description: Use when work is split into delegated steps for specialist agents, when dispatching a recorded step with scripts/dispatch-step.mjs, saving a follow-up or repair prompt, auditing runs/ for missing prompts or responses, or gating and checkpointing a milestone.
---

# Plan, dispatch and record steps

Big work (a milestone, a large feature) is done as many **small recorded steps**. Each step is one task for one
agent, with the exact prompt saved before it is sent and the agent's exact final message saved after. The record
lets anyone see later who asked what, what came back and what was checked. It documents the process; it does
**not** guarantee that re-sending a prompt regenerates the same code (models are not deterministic). Git
checkpoints (branches and tags) are the authoritative versions.

Roles (see `docs/TOOLKIT.md` §4 and §7):

- **owner**: the top-level session or person. Saves prompts, dispatches, integrates, runs checks, commits and tags.
- **project-orchestrator**: plans steps and judges results. Read-only; it cannot dispatch.
- **specialist agents** (`backend-engineer`, `frontend-engineer`, `test-engineer`, reviewers…): do one step each.
- **delegated-product-owner**: answers routine product questions from the written brief (delegated mode only).

## Inputs

- The milestone or feature brief (for example `milestones/<nn-name>/PROMPT.md`) and the app's planning documents
  in `<docs>` (`app.docsDir` in `app-creator.config.json`).
- `runs/INDEX.md` and the existing step folders; `PROGRESS.md` if present.
- The agents in `.claude/agents/` and skills in [../INDEX.md](../INDEX.md).
- Whether the owner has recorded a delegation (`docs/TOOLKIT.md` §4). Without one, the student approves each plan
  and commit.

## Actions

1. **Plan.** Ask `project-orchestrator` for a step plan (it returns id, agent, skills, inputs, work, done-when,
   parallel?). Step ids: `<milestone>-<nn>-<slug>`, for example `m2-03-results-table`; bootstrap steps `B07c`.
   Small: one area, one sitting, a checkable "done when".
2. **Save the prompt before dispatch.** Create `runs/<milestone>/<step-id>/PROMPT.md` from the template in
   [step-records.md](step-records.md#promptmd): metadata (sender, receiver, starting commit, skills to load,
   instruction files with sha256 prefixes, dispatch command, follow-up-of) and the exact text between
   `<!-- DISPATCH:BEGIN -->` and `<!-- DISPATCH:END -->`. The text must ask for the `## Handoff` block.
   Get hashes with `shasum -a 256 <file> | cut -c1-16` and the commit with `git rev-parse --short HEAD`.
3. **Dispatch** from the repository root:
   ```bash
   node scripts/dispatch-step.mjs --step runs/<milestone>/<step-id> --agent <agent-name> --milestone <milestone>
   ```
   Flags are listed exactly in [step-records.md](step-records.md#dispatcher-flags). The script sends only the
   DISPATCH block to `claude -p --output-format json`, then writes `RESPONSE.md` (verbatim, with only
   `[REDACTED:<kind>]` markers), `RESULT.json` and one line in `runs/INDEX.md`. Exit 0 = completed; 1 = failed;
   2 = refused before dispatch.
4. **Read the response and check the work.** Compare the handoff with reality: `git status`, `git diff --stat`, run
   the named checks (`npm run verify`, tests). Ask `project-orchestrator` to judge: accept, repair or blocked.
5. **Follow-ups are new steps.** A repair or clarification gets a **new step id** (`m2-03b-fix-empty-state`) with its
   own PROMPT.md saved first and `Follow-up of: <step-id>` in its metadata. To continue the same agent session,
   add `--resume <session-id>` (the id is in the earlier step's `RESULT.json`). Never edit a dispatched PROMPT.md
   and never overwrite a RESPONSE.md. For milestones, also append the exact follow-up text to
   `milestones/<nn-name>/FOLLOWUPS.md` before sending it.
6. **Integrate and commit.** The owner commits verified work (`feat: ...`), interactive mode with the student's
   approval, delegated mode within the delegation. Do not write a commit's own SHA inside that commit; record it in
   the next log update or the final manifest.
7. **Audit** before every checkpoint with the script in [step-records.md](step-records.md#audit): every step has a
   PROMPT.md and either a RESPONSE.md or an explicit missing-message marker; PROMPT.md was not changed after
   dispatch. If capture failed, write the gap down and fix the capture before dispatching more steps.
8. **Gate and checkpoint.** `project-orchestrator` gates on real evidence (acceptance criteria, `npm run verify`
   exit 0, Playwright smoke, screenshots looked at, review findings). Then the owner creates the branch and
   annotated tag (see [step-records.md](step-records.md#checkpoints)); pushing them is publication and needs the
   owner's explicit go-ahead.

Using Cline or another tool without the dispatcher? Follow [manual-capture-cline.md](manual-capture-cline.md);
records made that way are labelled **manual capture**.

## Outputs

- `runs/<milestone>/<step-id>/` with `PROMPT.md`, `RESPONSE.md`, `RESULT.json` (and `stderr.log` if any).
- `runs/INDEX.md` with one appended line per dispatch, including failed attempts.
- `milestones/<nn-name>/FOLLOWUPS.md` for milestone follow-ups; a final manifest of result SHAs after checkpoints.
- Orchestrator summaries kept **separately** (for example in `PROGRESS.md`), never in RESPONSE.md.

## Verification

- `node scripts/dispatch-step.mjs` exited 0 and `RESULT.json` says `"status": "completed"` with a `sessionId`.
- The audit prints no "NO PROMPT", "changed after dispatch" or unexplained "NO RESPONSE".
- `git status` after the step shows only files the step was allowed to touch.
- Each accepted step's checks were re-run by the owner, not only reported by the agent.

## Stop when

- The step is accepted and committed, or recorded as blocked with the reason.
- **Stop and fix the process** when a response was not captured (do not dispatch further until capture works).
- **Stop and ask the owner** when a step needs new scope, money, a publication action, personal data or a secret;
  when a check fails after two different repairs; or when a tag would have to move.

## Common mistakes

- Writing PROMPT.md after dispatch, or "tidying" it later. The record must be the text actually sent.
- Pasting a summary into RESPONSE.md, or reconstructing a lost reply from memory. Write
  `[MISSING FINAL MESSAGE]` and the reason instead.
- Reusing a step id for a retry (the dispatcher refuses to overwrite RESPONSE.md; use `B07c2`, `m2-03b`).
- Trusting "all tests pass" in a handoff without running them.
- Leaving out failed attempts from `runs/INDEX.md` so the history looks cleaner than it was.
- Sending a step to an agent without write tools (for example a read-only reviewer) and expecting edits.

## Example

```bash
mkdir -p runs/m2/m2-03-results-table
# write runs/m2/m2-03-results-table/PROMPT.md (template in step-records.md), then:
node scripts/dispatch-step.mjs --step runs/m2/m2-03-results-table --agent frontend-engineer --milestone m2
# [dispatch-step] m2-03-results-table: completed (exit 0), session 4f1c...
git diff --stat && npm run verify     # owner checks; orchestrator judges: "repair: empty state missing"
mkdir -p runs/m2/m2-03b-results-empty-state
# write its PROMPT.md with "Follow-up of: m2-03-results-table" and the exact repair text, then:
node scripts/dispatch-step.mjs --step runs/m2/m2-03b-results-empty-state --agent frontend-engineer \
  --milestone m2 --resume 4f1c...
```
Real example in this repository: `runs/bootstrap/B07c-skills-process/` failed (sent to an agent without write
tools); the retry is a new step, `runs/bootstrap/B07c2-skills-process/`, whose PROMPT.md says so.
