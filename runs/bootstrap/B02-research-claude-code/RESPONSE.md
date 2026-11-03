# RESPONSE — B02-research-claude-code

- From: default → to: owner (top-level Claude Code session)
- Captured by: scripts/dispatch-step.mjs from the `result` field of `claude -p --output-format json`
- Session id: 982f5811-2949-4013-b576-6c08bf0bcdf0 (local Claude Code transcript; not committed)
- Finished: 2026-11-03T17:08:45.495Z; exit code 0; status completed
- Redaction: only explicit [REDACTED:<kind>] markers were inserted; otherwise verbatim.

<!-- VERBATIM:BEGIN -->
I've written `docs/research/claude-code-and-cline.md`. It's about 1,600 words by `wc`, over the 1,300 target; the source list and inline code make up much of that. Every claim is cited to a page fetched on 2026-11-03, and the gaps are marked [unverified].

Findings that affect the build:

- **AGENTS.md:** Claude Code reads AGENTS.md on its own only when there is no CLAUDE.md in the folder or any folder above it. This repo will have both (GOAL §3), so CLAUDE.md needs an `@AGENTS.md` import or AGENTS.md is never loaded.
- **Skill frontmatter:** Claude Code treats every field as optional. Cline requires `name` and `description`, and `name` must match the folder name. The Skills API rejects most extra fields. Keeping `name` + `description` (plus at most `allowed-tools`) works in all three.
- **Cline reads `.claude/skills/`:** it is in Cline's list of project skill folders, so our skills work there too. Cline does not read `.claude/agents/`, and its subagents exist only in its CLI and Desktop app, not the VS Code extension. The subagent workflow is effectively Claude Code-only.
- **Subagents can spawn subagents:** by default up to three levels below the main session. Files added or edited in `.claude/agents/` are picked up within seconds without a restart. The exception is the first agent file in an `agents/` folder that didn't exist when the session started, which needs a restart.
- **`bypassPermissions`:** deny rules still block and ask rules still prompt, but allow rules do nothing. Protected folders such as `.git` and `.claude` are not prompted for in this mode.
- **`claude -p`:** it now starts in Manual mode, so any action that needs approval is denied unless pre-approved. `--bare` skips CLAUDE.md, skills and agents, so it must not be used when testing the toolkit.
- **Transcripts:** they live at `~/.claude/projects/<folder>/<session-id>.jsonl`. The docs call the format internal and subject to change, so use `/export` or the JSON output rather than parsing it.
- **Unverified:** the docs don't say whether a README or INDEX file inside `.claude/skills/` causes problems. Treat it as unknown and keep loose files out of that folder.

## Handoff
Changes: `docs/research/claude-code-and-cline.md` (new; no other files touched, nothing installed or committed).
Verification evidence: Fetched successfully (HTTP 200): code.claude.com/docs/en/{skills, sub-agents, cli-reference, headless, sessions, memory, permissions, permission-modes, settings}; docs.cline.bot/{llms.txt, features/cline-rules, customization/cline-rules, features/skills, getting-started/config.md, core-workflows/using-commands, features/subagents, features/hooks, sdk/plugins.md}. No docs.anthropic.com fallback was needed. Failed: docs.cline.bot/features/slash-commands/workflows (404). The cli-reference, memory and permissions pages were truncated at about 40k characters, so their tails came as a paraphrase. Points taken from those tails are marked "(summary)": `--session-id`, the WebFetch/MCP rule details, and the protected-paths list.
Remaining findings:
- **D5/D6:** both are frontend/backend version pins, so nothing here contradicts them.
- **AGENTS.md:** must be imported into CLAUDE.md, as described above.
- **JSON output fields:** `is_error` and `num_turns` are not documented. Only `result`, `session_id`, `total_cost_usd` and `structured_output` are.
- **Positional arguments:** they are 0-based, so `$1` is the second argument.
- **Skill name clashes:** Cline gives a global skill priority over a project skill with the same name, the opposite of Claude Code.
- **Cline docs disagree:** one Cline page lists `.agents/skills` as a skill folder and another doesn't.
- **Open questions:** the README-in-skills behaviour and the Cline workflow file format are unverified.
Next action: Have the toolkit step add `@AGENTS.md` to CLAUDE.md and keep skill frontmatter to `name` + `description`, with `name` matching the folder name.
<!-- VERBATIM:END -->
