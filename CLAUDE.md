<!-- App Creator. Claude Code reads this file; the shared rules are in AGENTS.md (imported below).
     Claude Code reads AGENTS.md on its own only when no CLAUDE.md exists, so keep the import. -->
@AGENTS.md

## Claude Code only

- **Skills:** `.claude/skills/<name>/SKILL.md` (index: `.claude/skills/INDEX.md`). Type `/name`, or Claude uses one
  when the situation matches its description.
- **Agents:** `.claude/agents/<name>.md` run as **subagents** with their own fresh context. Reviewers have
  read-only tools; `review-changes` runs them in parallel.
- **Permissions:** `.claude/settings.json` (edits accepted, project test commands allowed, `.env` reads and edits
  denied, force-push, `git reset --hard` and `git clean` denied, every other command asks). Never switch to a mode
  that bypasses permissions in an interactive session.
- **Recorded steps:** `node scripts/dispatch-step.mjs --step runs/<milestone>/<step-id> --agent <name>` sends the
  saved `PROMPT.md` to an agent with `claude -p --agent <name> --output-format json` and writes the agent's final
  message to `RESPONSE.md` unchanged except for explicit `[REDACTED:<kind>]` markers. Rules: `.claude/skills/orchestrate-steps/SKILL.md`.
