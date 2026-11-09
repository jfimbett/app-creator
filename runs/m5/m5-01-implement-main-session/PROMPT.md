# PROMPT — m5-01-implement-main-session

- Sender: the instructor (owner of the repository), typed into the top-level Claude Code session on 2026-11-09
- Receiver: top-level Claude Code session (Opus 5.5), working directly; read-only review subagents and builder subagents may be used
- Starting commit: 40b0ea0 on main (descends from tag m4, d82ab2a; only a documentation commit after the tag)
- Workspace: isolated worktree `.worktrees/m5`, branch `work/m5`, Windows 11
- Milestone brief: `milestones/05-ai-financial-analyst/PROMPT.md` (sha256 c3caadf1aa1c028d), unchanged since `template-v1`
- Instruction files: `AGENTS.md` (803058fd2f8ec1b6), `examples/sec-analytics/CLAUDE.md` (6e5e2c532cb43b43)
- Context: the assistant had reported M4 done and not pushed. The text below is the exact reply. It authorized pushing M4 (done before this step) and starting M5; routine decisions and local commits inside M5 follow the earlier "work autonomously" instruction.

<!-- DISPATCH:BEGIN -->
push and start with m5
<!-- DISPATCH:END -->

## Decisions recorded before work

- **Live AI (N1):** the instructor has not said that an authorized, limited OpenRouter test key is configured. Per brief §8, no key is asked for, `.env` is not read, and no live AI call is made: M5 is verified with mocked integration and reported as "live AI: not verified (N1)".
- As in M3 and M4, this session is also the integrator: it commits and creates the `m5` checkpoint locally and updates `PROGRESS.md` and `runs/` at the checkpoint (brief §11–§12 address a delegated implementer). Pushing waits for the instructor.
