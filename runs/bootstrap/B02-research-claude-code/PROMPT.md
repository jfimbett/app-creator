# PROMPT — B02-research-claude-code

- Sender: owner (top-level Claude Code session)
- Receiver: default Claude Code agent (`--agent default`; the toolkit's agents do not exist yet — orchestrator B01 risk 4)
- Starting commit: 10e8c6f
- Skills: none; instruction paths: GOAL.md, PROGRESS.md
- Dispatch: `node scripts/dispatch-step.mjs --step runs/bootstrap/B02-research-claude-code --agent default --mode bypassPermissions --milestone bootstrap`
- Plan reference: runs/bootstrap/B01-orchestrator-bootstrap-plan/RESPONSE.md

<!-- DISPATCH:BEGIN -->
Research task for the App Creator build (see GOAL.md §3 and §8). Topic: current Claude Code formats and behaviour, from https://code.claude.com/docs (and docs.anthropic.com/en/docs/claude-code if that redirects). Answer precisely: (1) project skills — location (.claude/skills/<name>/SKILL.md), required and optional frontmatter fields (name, description, allowed-tools, argument-hint, disable-model-invocation, etc.), how supporting files are referenced, $ARGUMENTS, how skills are discovered, whether nested .claude/skills in subdirectories are discovered, and whether a README/INDEX file inside .claude/skills/ causes problems; (2) subagents — .claude/agents/<name>.md frontmatter fields (name, description, tools, disallowedTools, model, skills, permissionMode, etc.), whether agents created mid-session are picked up without restart, whether a subagent can spawn other subagents; (3) the CLI: claude -p, --agent, --output-format json fields (result, session_id, ...), --resume, and where session transcripts live / how to export; (4) CLAUDE.md imports (@path) and AGENTS.md handling; (5) settings.json permission rule syntax and whether deny rules apply in bypassPermissions mode. Also check Cline's official docs (docs.cline.bot) for: .clinerules, AGENTS.md support, skills folders it reads, and whether it has subagents/slash commands equivalent to Claude Code.
Rules: use only official documentation (fetch the pages; do not answer from memory), cite every claim with its URL and the retrieval date 2026-11-03, and mark anything you could not fetch as [unverified]. Write ONLY the one file named below (create docs/research/ if needed); do not edit any other file, do not install anything, do not commit. Keep the file under about 1300 words, as practical implementation notes. Never print or write secrets or email addresses. End your final message with:
## Handoff
Changes: <file written>
Verification evidence: <pages fetched (URLs) and any failures>
Remaining findings: <surprises, contradictions with the notes in PROGRESS.md decisions D5/D6>
Next action: <one line>
File: docs/research/claude-code-and-cline.md

<!-- DISPATCH:END -->
