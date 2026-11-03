# PROMPT — B07c2-skills-process

- Sender: owner (top-level Claude Code session)
- Receiver: docs-writer (agent created in B06)
- Follow-up of: B07c-skills-process (terminated: misrouted to github-coach, which has no write tools). Dispatched text below is byte-identical to B07c.
- Starting commit: 47dbf85 (working tree may hold uncommitted owner/step changes; see git status in RESULT/PROGRESS)
- Skills to load: git-collaboration, write-docs, orchestrate-steps (new, as files to create)
- Key instruction/reference files (sha256 prefix at dispatch):
  - docs/TOOLKIT.md 136a3145d82696f1
  - GOAL.md 20b3a7b8e8c2aa44
  - docs/research/claude-code-and-cline.md 465f89b85d605c92
- Dispatch: `node scripts/dispatch-step.mjs --step runs/bootstrap/B07c2-skills-process --agent docs-writer --mode bypassPermissions --milestone bootstrap`

<!-- DISPATCH:BEGIN -->
Task B07c of the App Creator bootstrap: process skills, the skills index and the GitHub collaboration guide.
Read first: `docs/TOOLKIT.md` (conventions, frozen skill names, root commands, working modes; follow it), `GOAL.md` §3 (required coverage), `docs/research/claude-code-and-cline.md` (current skill format; if missing, use the existing SKILL.md frontmatter format), and the existing skill folders you own (imported unchanged from app-starter 0.3.0; preserve their good content, rules and tone, and adapt rather than rewrite blindly).
General adaptation rules for every skill you touch: paths come from `app-creator.config.json` (the app may live in `app/frontend`, `app/backend`, docs in the configured docs dir) instead of the starter's single `app/`; the standard stack is Next.js/React/TS/Tailwind/Recharts + FastAPI (Streamlit and Django are no longer the defaults; mention alternatives only briefly); run/test via the root `npm run setup|dev|verify|demo` contract; Playwright (project-local, run by `npm run verify`) replaces the starter's Python browser_check; the approval rules follow docs/TOOLKIT.md §4 (interactive default; recorded delegation allows routine decisions and commits, never scope/money/publication/personal data/secrets). Every SKILL.md: valid YAML frontmatter (`name` equals folder name; `description` = concrete trigger conditions, under ~300 characters), then Inputs, Actions (concrete numbered workflow), Outputs, Verification (checks), Stop when (failure handling), Common mistakes, and at least one short concrete example. Supporting guides live in the same folder and are linked from SKILL.md with relative links; make them practical (checklists, code snippets, commands), not generic essays. Domain-neutral: no SEC/finance assumptions (a neutral financial example is acceptable where it teaches a general rule like "missing is not zero"). Do not create category subfolders; do not touch files outside your listed folders.
Verification: run a check that each of your SKILL.md files parses (frontmatter name matches folder, description present) and that every relative link in your files resolves; report the command output.
Your files: .claude/skills/git-collaboration/ (new), .claude/skills/write-docs/ (new), .claude/skills/orchestrate-steps/ (new), .claude/skills/INDEX.md (new), docs/GITHUB-COLLABORATION.md (new). Also read scripts/dispatch-step.mjs (do not edit it) and GOAL.md §8 and §9. This step is the exception to read-mostly: you are authorized to create these files.
Work:
1. git-collaboration: substantial, practical coverage: clone/fork/origin/upstream, branches, small commits with good messages, PRs and code review, resolving conflicts step by step, merge vs rebase (never rebase shared history; prefer merge or squash-merge for teams), releases and tags (annotated, never move a published tag), Issues, Projects, branch protection (suggest; never apply automatically), five-person collaboration (roles, shared contracts such as API types and fixtures, ownership, daily integration), switching refs safely (stop services, git status, stash or commit, rerun setup), and recovery without destructive commands (git restore, git revert, git switch -c rescue; reset --hard and clean are never default advice). Clearly separate LOCAL actions from PUBLICATION actions (push, PR, release, repo settings), which need the owner. Guides: branching-and-prs.md, conflicts-merge-rebase.md, releases-issues-projects.md, team-of-five.md. Safe command examples only.
2. write-docs: docs that match tested commands (README, setup, troubleshooting, changelog, architecture diagram, teaching notes); every command written must have been run or be labelled untested; versions and dates; no invented results.
3. orchestrate-steps: the step-record workflow from docs/TOOLKIT.md §5 and GOAL.md §8: orchestrator plans small steps; owner saves PROMPT.md BEFORE dispatch (metadata: sender, receiver, starting commit, loaded skills, instruction paths and hashes, exact text between DISPATCH markers); dispatch with `node scripts/dispatch-step.mjs` (document its flags exactly as implemented); RESPONSE.md verbatim with explicit redaction markers; RESULT.json; runs/INDEX.md; follow-ups as new step ids (or --resume) with exact text saved first; milestone FOLLOWUPS.md; never fabricate or reconstruct a response; mark gaps; audit that every step has prompt+response or a missing marker; checkpoint branches/tags; exact prompts do not guarantee identical regeneration. Explain how to do the same manually in Cline (copy prompt, paste final message), labelled as manual capture.
4. INDEX.md: a table of all 15 skills (name, when to use, key guides) grouped by phase within the table (not in folders), plus the agents list with one line each.
5. docs/GITHUB-COLLABORATION.md: student-facing guide for a team of five (roles, shared contracts, feature branches, PRs/reviews/conflicts, suggested protections, fork/origin/upstream, nothing applied automatically), linking to the skill guides.

End your final message with exactly this block (concise):
## Handoff
Changes: <files created/changed>
Verification evidence: <commands run and exit codes>
Remaining findings: <open issues, doubts>
Next action: <one line>
Do not commit, push, tag or change git configuration; the owner integrates and commits. Never read, create or print .env files or secrets, and never write email addresses into files.
<!-- DISPATCH:END -->
