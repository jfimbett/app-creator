# PROMPT — B18-discovery-check

- Sender: owner (top-level Claude Code session)
- Receiver: default (fresh default session; tests what is loaded)
- Starting commit at prompt write: 6727dc2 (RESULT.json records the commit at dispatch)
- Skills to load: none (observes skill listing)
- Key instruction/reference files (sha256 prefix when written):
  - docs/TOOLKIT.md 72165a1d6238722a
  - GOAL.md 20b3a7b8e8c2aa44
- Dispatch: `node scripts/dispatch-step.mjs --step runs/bootstrap/B18-discovery-check --agent default --mode default --milestone bootstrap`

<!-- DISPATCH:BEGIN -->
Task B18: discovery check for the App Creator toolkit. Do not change any file and do not run commands that write. Answer from what this Claude Code session actually has loaded, not from reading files: (1) list every skill name available to you in this session (from your skill listing), marking which come from this project's .claude/skills/; (2) list every subagent type available to you (from your agent/Task tool description), marking which come from this project's .claude/agents/; (3) which file holds this project's rules and what must happen first in every session. Then, separately and clearly labelled "from files", compare with `ls .claude/skills .claude/agents` and report any skill or agent folder that exists on disk but was NOT in your loaded lists.

End your final message with exactly this block (concise):
## Handoff
Changes: <files created/changed>
Verification evidence: <commands run and exit codes>
Remaining findings: <open issues, doubts>
Next action: <one line>
Do not commit, push, tag or change git configuration; the owner integrates and commits. Never read, create or print .env files or secrets, and never write email addresses into files.
<!-- DISPATCH:END -->
