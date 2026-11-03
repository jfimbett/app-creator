<!-- app-starter 0.3.0. Claude Code reads this file; the shared rules are in AGENTS.md (imported below). -->
@AGENTS.md

## Claude Code only

- Skills: `.claude/skills/` (type `/name`, or Claude uses them when the situation matches).
- Reviewers: `.claude/agents/` run as **subagents** with read-only tools (`review-changes` runs them in parallel).
- Permissions: `.claude/settings.json` (edits accepted, project test commands allowed, `.env` blocked, every other
  command asks). Never switch to a mode that bypasses permissions.
