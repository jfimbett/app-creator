# Manual capture (Cline or any tool without the dispatcher)

Part of [orchestrate-steps](SKILL.md). `scripts/dispatch-step.mjs` calls the Claude Code CLI. Cline's VS Code
extension has no equivalent command and does not run Claude Code subagents, so the same record is made by hand.
Records made this way are **manual capture**: their fidelity depends on careful copying, and they say so. This
workflow has not been tested with Cline in this repository.

## Steps

1. **Save PROMPT.md first**, exactly as in [step-records.md](step-records.md#promptmd), with
   `- Dispatch: manual (Cline, new task)` in the metadata and `- Receiver: Cline task following
   .claude/agents/<agent>.md` (Cline reads the agent file as instructions; it does not become that agent).
2. **Start a new Cline task** and paste only the text between `<!-- DISPATCH:BEGIN -->` and `<!-- DISPATCH:END -->`.
   If the step needs an agent's instructions, start the text with "Follow `.claude/agents/<agent>.md`." inside the
   DISPATCH block, so the record shows it.
3. **Approve tool use** as Cline asks, within the step's scope. Refuse anything touching `.env`, pushes or settings.
4. **Copy the final message** (the task's last assistant message / completion result) as plain text, unchanged.
5. **Write RESPONSE.md** immediately:
   ```markdown
   # RESPONSE — m2-03-results-table

   - From: Cline task (following .claude/agents/frontend-engineer.md) → to: owner
   - Captured by: manual capture (copied from the Cline chat by the owner)
   - Model: <as shown in Cline's settings>
   - Finished: 2026-11-03T14:20Z
   - Redaction: only explicit [REDACTED:<kind>] markers were inserted; otherwise verbatim.

   <!-- VERBATIM:BEGIN -->
   <pasted final message>
   <!-- VERBATIM:END -->
   ```
   Before saving, replace any key, token or email with `[REDACTED:<kind>]`. Do not fix typos or shorten it.
   If the message was lost (chat closed, crash), write `[MISSING FINAL MESSAGE] <what happened>` instead; never
   rewrite it from memory.
6. **Write RESULT.json** by hand with the fields you know, and `null` for the rest:
   ```json
   {
     "stepId": "m2-03-results-table", "milestone": "m2",
     "sender": "owner", "receiver": "Cline task (frontend-engineer instructions)",
     "dispatcher": "manual capture (Cline)", "startCommit": "1a2b3c4", "endCommit": null,
     "startedAt": "2026-11-03T14:02Z", "finishedAt": "2026-11-03T14:20Z",
     "status": "completed", "sessionId": null, "missingRecord": null
   }
   ```
7. **Append a line to `runs/INDEX.md`** in the same format as the dispatcher's lines, adding `(manual capture)`.
8. Continue with the normal check, judge, follow-up and audit steps in [SKILL.md](SKILL.md). Without subagents,
   the orchestrator and reviewer roles are separate Cline tasks that follow `.claude/agents/<name>.md`
   (see `review-changes`, "Without subagents").
