# PROMPT — B01-orchestrator-bootstrap-plan

- Sender: owner (top-level Claude Code session, Opus 5.5)
- Receiver: project-orchestrator (`.claude/agents/project-orchestrator.md`, uncommitted draft at dispatch time)
- Starting commit: 6e8314a (working tree also holds uncommitted drafts: scripts/dispatch-step.mjs, two agents, this record)
- Skills to load: none yet (the toolkit does not exist); instruction paths: GOAL.md, PROGRESS.md
- Dispatch: `node scripts/dispatch-step.mjs --step runs/bootstrap/B01-orchestrator-bootstrap-plan --agent project-orchestrator --mode default`
- Purpose: first recorded step; also tests that `--agent` loads a project agent and that the final message is captured.

<!-- DISPATCH:BEGIN -->
You are being dispatched as the project-orchestrator for the App Creator build. Read GOAL.md completely and PROGRESS.md. The folder is a fresh git repo (one commit). The starter ZIP (app-starter.zip, v0.3.0) was inspected by the owner: it has 11 skills (product-interview, design-interface, test-and-check, debug-issue, add-accounts, build-feature, integrate-api, review-changes, add-payments, prepare-deploy, manage-data) and 4 read-only reviewer agents; the owner will preserve and adapt them.

Task: plan the BOOTSTRAP phase only (everything before the `template` branch / `template-v1` tag), as small recorded steps per GOAL.md §3, §8. Do not plan milestone implementation in detail. Required content:
1. An ordered step table (id `B<nn>-<slug>`, agent, skills, inputs, work, done-when, parallel?) covering: official-documentation research (Claude Code skill/agent formats, SEC EDGAR APIs and fair access, OpenRouter API), toolkit creation (skills, agents, root instructions, launcher scripts), the delegated product interview (interviewer questions → delegated-product-owner answers → decisions/product docs), writing the five milestone PROMPT.md files, toolkit verification, and the template checkpoint.
2. Which steps can safely run in parallel and the file-ownership boundaries that make that safe.
3. The gate for the template-v1 checkpoint (what must be verified, and what must NOT be present).
4. Risks you see in GOAL.md for this phase (contradictions, things needing the owner).
Keep it under about 900 words. Do not edit files. End with the Handoff block from your agent instructions.
<!-- DISPATCH:END -->
