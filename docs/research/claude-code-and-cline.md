# Claude Code and Cline: implementation notes

All pages retrieved 2026-11-03. Sources: [SK] https://code.claude.com/docs/en/skills · [SA] https://code.claude.com/docs/en/sub-agents · [CLI] https://code.claude.com/docs/en/cli-reference · [HL] https://code.claude.com/docs/en/headless · [SE] https://code.claude.com/docs/en/sessions · [ME] https://code.claude.com/docs/en/memory · [PE] https://code.claude.com/docs/en/permissions · [PM] https://code.claude.com/docs/en/permission-modes · [ST] https://code.claude.com/docs/en/settings · [CR] https://docs.cline.bot/features/cline-rules · [CS] https://docs.cline.bot/features/skills · [CC] https://docs.cline.bot/getting-started/config.md · [CU] https://docs.cline.bot/core-workflows/using-commands · [CA] https://docs.cline.bot/features/subagents. code.claude.com served all pages directly; no docs.anthropic.com redirect was needed. Items marked (summary) came from the tail of a truncated page. The fetch tool paraphrased those parts, so check the exact wording before quoting it.

## 1. Skills [SK]

- **Locations:** project `.claude/skills/<name>/SKILL.md`, personal `~/.claude/skills/...`, enterprise (managed settings directory), plugin `<plugin>/skills/...`, `--add-dir` directories, and nested `<subdir>/.claude/skills/...`.
- **Frontmatter:** "All fields are optional. Only `description` is recommended." Unknown fields are ignored silently, and field names must match exactly, hyphens included. If the YAML fails to parse, the skill still loads with no fields set.
  - `name`: defaults to the directory name.
  - `description`: if missing, the first non-empty line of the body is used. `description` plus `when_to_use` is truncated at 1,536 characters in the listing.
  - Other fields: `when_to_use`, `argument-hint`, `arguments`, `disable-model-invocation`, `user-invocable`, `allowed-tools`, `disallowed-tools`, `model`, `effort`, `context: fork`, `agent`, `paths`, `hooks`, `metadata`, among others.
  - `allowed-tools` grants last only for the invoking turn: "The grant clears when you send your next message."
- **Portability:** claude.ai uploads and the Skills API accept only `name`, `description`, `license`, `compatibility`, `metadata` and `allowed-tools`. Any other field is a hard error there. Keep the toolkit to that set if the skills must be portable.
- **Supporting files:** link them from SKILL.md with relative Markdown links, e.g. `[reference.md](reference.md)`. Run scripts through `${CLAUDE_SKILL_DIR}/scripts/...`. Keep SKILL.md under 500 lines.
- **Arguments:**
  - `$ARGUMENTS` is all arguments. `$ARGUMENTS[N]` and `$N` are 0-based, so `$0` is the first argument. Named `$name` comes from `arguments:`.
  - If no placeholder is present, the arguments are appended as `ARGUMENTS: <value>`.
  - Note: `$1` is the *second* argument.
- **Discovery:**
  - Descriptions are always in context. The full body loads only when the skill is invoked and is not re-read on later turns.
  - `disable-model-invocation: true` removes the description from context.
  - Skill files are watched, so adding or editing a skill takes effect without a restart. A skills directory that did not exist at session start needs `/reload-skills`.
- **Nested directories:**
  - `.claude/skills/` loads from the start directory and every parent up to the repository root.
  - A `.claude/skills/` directory *below* the start directory is not loaded at startup. It loads the first time Claude reads or edits a file in that subdirectory. Same-name skills are then addressed like `/apps/web:deploy`.
- **README/INDEX in `.claude/skills/`:** [unverified]. The docs do not say how loose files or directories without SKILL.md are treated. They state only that a skill is `<name>/SKILL.md`. Avoid a skill folder named `synced` (reserved).

## 2. Subagents [SA]

- **Priority:** managed settings > `--agents` JSON > `.claude/agents/` > `~/.claude/agents/` > plugin.
  - Directories are scanned recursively.
  - Project agents are found by walking up to the repository root, and the closest definition wins.
- **Frontmatter:**
  - Required: `name` and `description`. A file missing either is skipped, as is a `name` containing `:` or starting with `-`.
  - Optional: `tools` (all tools inherited if omitted), `disallowedTools` (applied first), `model` (`sonnet|opus|haiku|fable`, a full ID, or `inherit`), `permissionMode` (`default|acceptEdits|auto|dontAsk|bypassPermissions|plan|manual`), `maxTurns`, `skills` (full content preloaded), `mcpServers`, `hooks`, `memory` (`user|project|local`), `background`, `isolation: worktree`, `effort`, `color`, `initialPrompt`, `omitClaudeMd`, `autoCompactWindow`.
- **permissionMode is overridden** when the parent session runs in `bypassPermissions`, `acceptEdits` or auto: the subagent then inherits the parent's mode.
- **Skills:** the `skills:` field only preloads skills. Without it, a subagent can still invoke skills through the Skill tool. A subagent does not inherit the parent's conversation history or the skills the parent already loaded.
- **Mid-session agents:** files added or edited in `.claude/agents/` or `~/.claude/agents/` are "detected within a few seconds… no restart needed." Restart in three cases:
  1. The first agent file in a scope's new `agents` directory.
  2. Edits under `--add-dir` directories.
  3. Sessions started with `--disable-slash-commands`.
- **`/agents`:** now only prints a reminder to edit the files. The wizard existed only in v2.1.197 and earlier.
- **Nesting:** **yes**. "A subagent can spawn subagents of its own, up to three layers below the main conversation."
  - Change the limit with `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`. Setting it to `1` disables nesting.
  - Block spawning for one agent by leaving `Agent` out of its `tools`.
  - `Agent(type,...)` lists in a subagent's `tools` are ignored. They work only when the agent runs as the main thread via `--agent`.
- **Main thread as an agent:** `claude --agent <name>` or `"agent"` in `.claude/settings.json`. The agent's prompt *replaces* the default system prompt; CLAUDE.md still loads.

## 3. CLI [CLI][HL][SE]

- **`claude -p "query"`** runs non-interactively.
  - Exit code 0 on success, non-zero on failure. Failures inside the run are printed as the result on stdout.
  - Since v2.1.302, `-p` starts in Manual mode, so calls that need approval are denied unless they are pre-approved. Use `--allowedTools`, `--permission-mode`, or `--permission-prompts none` (v2.1.259+).
  - `--bare` skips CLAUDE.md, skills, agents, hooks and MCP, and is "recommended for scripted calls". **Do not use `--bare` when the toolkit itself is under test.**
- **`--agent <name>`** sets the session agent. **`--agents '<json>'`** defines session-only agents; with `-p` it also accepts a file path (v2.1.281+).
- **`--output-format text|json|stream-json`**. stream-json needs `--verbose`.
  - JSON fields documented: `result`, `session_id`, `total_cost_usd` (plus a per-model breakdown), and `structured_output` (with `--json-schema`). Usage metadata is mentioned without a field name.
  - `is_error` and `num_turns` are not documented [unverified]. Parse defensively.
- **Session flags:**
  - `--resume <id|name|abs .jsonl path>`, `--continue`, `--fork-session`, and `--session-id <uuid>` (summary).
  - `-p` sessions are excluded from the picker and from plain `--continue`. Resume them by ID; `claude -p --continue` includes them.
- **Transcripts:** `~/.claude/projects/<cwd with non-alphanumerics replaced by '-'>/<session-id>.jsonl`.
  - The format is "internal… changes between versions". Do not parse it; use `/export` or the JSON output instead.
  - `/export [filename]` writes a readable plain-text transcript.

## 4. CLAUDE.md and AGENTS.md [ME]

- **Load order:** files are loaded from the cwd and every parent, concatenated from the filesystem root down. `CLAUDE.local.md` follows `CLAUDE.md` in each directory. A subdirectory's CLAUDE.md loads when Claude touches a file there.
- **`@path` imports:**
  - Relative paths resolve from the importing file. Absolute paths and `@~/...` also work.
  - Maximum depth is four hops. Imports inside code spans or fenced blocks are skipped.
  - Imports outside the working directory trigger a one-time approval dialog. If declined, they stay disabled.
- **AGENTS.md:** read natively since v2.1.277, but "only when you have no `CLAUDE.md` in your working directory or above it." `~/.claude/CLAUDE.md` does not count toward that check.
  - **Because this repo has both files, CLAUDE.md must contain `@AGENTS.md`** to load it. "Keeping the import never makes Claude read `AGENTS.md` twice."

## 5. Permissions [PE][PM][ST]

- **Shape:** `{"permissions":{"allow":[…],"ask":[…],"deny":[…]}}`. Lists from different settings files are merged.
  - Settings precedence: managed > CLI > `.claude/settings.local.json` > `.claude/settings.json` > user.
  - Rules are evaluated deny → ask → allow, first match wins. "An allow rule can't carve an exception out of a deny rule."
- **Bash:**
  - `Bash(npm run build)` is an exact match.
  - `Bash(git log *)` matches any text after `git log`, including bare `git log`. `Bash(ls*)` also matches `lsof`. `:*` is equivalent to ` *`.
  - An allow rule does not cover `a && b`. A deny rule applies when any subcommand matches.
  - Deny rules are "not a security boundary".
- **Read/Edit:** gitignore-style patterns.
  - A `Read` deny also blocks Edit and Write. `Write(...)` rules never match; use `Edit(...)`.
- **Other tools:** `WebFetch(domain:x.com)`, `mcp__server__*` (summary), `Agent(Explore)`, and `Skill(skill:<name>)` for deny.
- **Modes:** `default` (Manual), `acceptEdits`, `plan`, `auto`, `dontAsk`, `bypassPermissions`.
- **bypassPermissions:** **"Deny rules block in every mode, including `bypassPermissions`."**
  - Explicit ask rules still prompt.
  - "Allow rules have no effect in `bypassPermissions`."
  - Bypass mode skips prompts for writes to protected paths such as `.git` and `.claude`.
  - Disable bypass mode with `permissions.disableBypassPermissionsMode: "disable"`.

## 6. Cline

- **Rules [CR]:**
  - Workspace: `.clinerules/` or `.cline/rules/`, both searched.
  - Also detected: `.cursorrules`, `.windsurfrules`, `AGENTS.md` and `~/.agents/AGENTS.md`.
- **AGENTS.md:** **supported** at the project root [CR][CC].
- **Skills [CS]:**
  - Project: `.cline/skills/` (recommended), `.clinerules/skills/`, **`.claude/skills/`**. Global: `~/.cline/skills/`.
  - [CC] also lists `.agents/skills/` and `~/.agents/skills/`. [CS] does not; that is a docs inconsistency.
  - `name` and `description` are **required**; `name` must equal the directory name; description is limited to 1,024 characters.
  - A global skill beats a project skill with the same name, the opposite of Claude Code's order.
  - Skills are invocable as `/skill-name` [CU].
- **Slash commands [CU]:** built-ins such as `/newtask`, `/smol`, `/newrule` and `/deep-planning`.
  - Workflow directories are `.cline/workflows/` and `.clinerules/workflows/` [CC].
  - The workflows page returned 404, so the file format and invocation are [unverified].
- **Subagents [CA]:** Cline CLI and Desktop only, "VS Code and JetBrains extensions don't use them."
  - Subagents are started through the `spawn_agent` tool, with a separate context and no MCP tools.
  - Approving `spawn_agent` approves everything the subagent then does.
  - Agent-definition directories `.cline/agents/` and `~/.cline/agents/` exist [CC], but their format is [unverified].

## Implications for App Creator

1. Keep skill frontmatter at `name` and `description`, with `name` equal to the folder name, and put no other files at the top of `.claude/skills/`. This satisfies Claude Code, Cline and the Skills API.
2. Add `@AGENTS.md` to CLAUDE.md.
3. Define agents in `.claude/agents/`. Cline will not read them, so the docs must state that the subagent workflow is Claude Code-only.
4. Scripted runs: use `claude -p --output-format json`, read `.result` and `.session_id`, and avoid `--bare`.
5. Put secret paths in `deny` rules, because those still apply under bypass mode.
