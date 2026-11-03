# PROMPT — B19-template-gate

- Sender: owner (top-level Claude Code session)
- Receiver: project-orchestrator (gates template-v1)
- Starting commit at prompt write: d387e3d (RESULT.json records the commit at dispatch)
- Skills to load: orchestrate-steps (gate side)
- Key instruction/reference files (sha256 prefix when written):
  - docs/TOOLKIT.md 72165a1d6238722a
  - GOAL.md 20b3a7b8e8c2aa44
  - runs/bootstrap/B19-template-gate/verify-clean-worktree.log 1893c5b139be6459
- Dispatch: `node scripts/dispatch-step.mjs --step runs/bootstrap/B19-template-gate --agent project-orchestrator --mode bypassPermissions --milestone bootstrap`

<!-- DISPATCH:BEGIN -->
Task B19: gate the `template-v1` checkpoint. Candidate commit: d387e3d (current HEAD of main). Read GOAL.md §3 (template requirements), §8, your own B01 plan gate (runs/bootstrap/B01-orchestrator-bootstrap-plan/RESPONSE.md §3), PROGRESS.md, and runs/INDEX.md.
1. Re-check B17 against your B14 repair decision: compare runs/bootstrap/B14-review-milestone-prompts/RESPONSE.md with `git diff 23e9a15 d387e3d -- milestones docs/PRODUCT-DECISIONS.md` and say whether every required edit landed (and the owner's two extra line fixes are correct).
2. Gate evidence (read, and re-run what is cheap): the clean-worktree verification log at runs/bootstrap/B19-template-gate/verify-clean-worktree.log (bounded copy; full log .logs/verify-d387e3d-20261103T182248Z.log). Note also PROGRESS.md failures log: two earlier clean runs failed on a headless-shell screenshot hang, fixed in d387e3d (npm ci → npm run setup → npm run verify in an isolated worktree of the candidate); `npm run check-toolkit`; B18 discovery check; that `git ls-tree -r --name-only d387e3d` contains no examples/ directory, no SEC application code or fixtures, no .env, keys, node_modules, .venv, .cache or app-starter.zip; that README/START-HERE explain main vs template and the generic getting-started path works without the SEC example; that all five milestones/0*/PROMPT.md exist with starting refs template-v1→m1→m2→m3→m4; that every runs/bootstrap step has PROMPT.md + RESPONSE.md + RESULT.json or a recorded failure marker; that open findings are recorded (security #1 and #2 are owner decisions, reported not fixed).
Return gate-pass or gate-fail with evidence per item, then the handoff. Do not edit files.

End your final message with exactly this block (concise):
## Handoff
Changes: <files created/changed>
Verification evidence: <commands run and exit codes>
Remaining findings: <open issues, doubts>
Next action: <one line>
Do not commit, push, tag or change git configuration; the owner integrates and commits. Never read, create or print .env files or secrets, and never write email addresses into files.
<!-- DISPATCH:END -->
