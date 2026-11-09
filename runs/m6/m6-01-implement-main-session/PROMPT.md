# PROMPT — m6-01-implement-main-session

- Sender: the instructor (owner of the repository), typed into the top-level Claude Code session on 2026-11-09
- Receiver: top-level Claude Code session (Opus 5.5), working directly; builder and read-only reviewer subagents may be used
- Starting commit: b1ff390 on main (descends from tag m5; documentation commits after the tag, the last one adds the M6 brief)
- Workspace: isolated worktree `.worktrees/m6`, branch `work/m6`, Windows 11
- Milestone brief: `milestones/06-polish-and-launch/PROMPT.md` (sha256 84fd6283be1a67d2), committed unchanged in b1ff390
- Instruction files: `AGENTS.md` (803058fd2f8ec1b6), `examples/sec-analytics/CLAUDE.md` (1d3c48c95323c012)
- Context: the session had been cleared. The text below is the exact instruction typed by the instructor.

<!-- DISPATCH:BEGIN -->
Run milestones/06-polish-and-launch/PROMPT.md, starting at its section 0. Work autonomously and report at the end.
<!-- DISPATCH:END -->

## Decisions recorded before work

- **Autonomy:** the brief's section 0 authorizes local commits, the local merge into `main`, the local branch `milestone/06-polish-and-launch` and the local tag `m6`. Pushing, remote tags and remote changes wait for the instructor.
- **No interview (brief §8):** reversible details (copy, fictional names, tier features, icons, layouts) are chosen in the session and listed in the Handoff.
- **Live services:** no key is asked for and `.env` is not read; live AI stays "not verified (N1)"; live SEC is not needed for M6.
- **Video:** made with the installed `/brag` skill; nothing new is installed in this autonomous run. A missing essential tool is recorded as a blocker.
