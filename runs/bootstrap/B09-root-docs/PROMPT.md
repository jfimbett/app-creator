# PROMPT — B09-root-docs

- Sender: owner (top-level Claude Code session)
- Receiver: docs-writer (agent created in B06)
- Starting commit at prompt write: 14c2d39 (RESULT.json records the commit at dispatch)
- Skills to load: write-docs, git-collaboration (read)
- Key instruction/reference files (sha256 prefix when written):
  - docs/TOOLKIT.md cde60522bfd2ce4b
  - GOAL.md 20b3a7b8e8c2aa44
  - docs/research/claude-code-and-cline.md 465f89b85d605c92
- Dispatch: `node scripts/dispatch-step.mjs --step runs/bootstrap/B09-root-docs --agent docs-writer --mode bypassPermissions --milestone bootstrap`

<!-- DISPATCH:BEGIN -->
Task B09 of the App Creator bootstrap: root instructions and student-facing entry documents for the GENERIC starter (the `template` branch). Read first: docs/TOOLKIT.md, GOAL.md §3, §4, §9 (README/START-HERE requirements), the current .claude/skills/INDEX.md and .claude/agents/, the root package.json and scripts/ (the launcher contract as implemented — read scripts/*.mjs and scaffold/README.md, do not edit them), docs/research/claude-code-and-cline.md (Cline facts), and the starter files imported unchanged: CLAUDE.md, AGENTS.md, START-HERE.md, PROMPTS.md, AI-USAGE.md, .clinerules/cline.md, .clineignore, docs/README.md.
You own: CLAUDE.md, AGENTS.md, START-HERE.md, PROMPTS.md, AI-USAGE.md, README.md (new), .clinerules/ (files inside), .clineignore, docs/README.md, LICENSE (new: MIT, copyright 2026 the App Creator authors; keep it standard text). Do not edit other files.
Work:
1. CLAUDE.md: short; `@AGENTS.md` import plus Claude-Code-only notes (skills, agents as subagents, settings, `claude -p --agent` used by scripts/dispatch-step.mjs). AGENTS.md: keep it short and generic (the starter's working rules, adapted): where things live (config-driven app dirs, docs dir, runs/), first thing in every session (read config; if the app's product doc is missing/not agreed → product-interview), working modes (interactive default; recorded delegation per docs/TOOLKIT.md §4), the rules (small changes, docs current, AI-USAGE, secrets, test by risk, git checkpoints — commits need approval in interactive mode; never push/force-push/rewrite/change remotes unless the owner asks, never claim unverified results, stop and ask, one isolated environment, course rules), the change report format, and a "This project" section that reads the commands from the root contract. No finance/SEC rules (the SEC example adds its own examples/sec-analytics/CLAUDE.md later).
2. README.md: what App Creator is; two paths: (A) inspect the prepared SEC Analytics milestones (on `main` and milestone tags m1–m5, which do not exist yet on this branch — say "after the example is published") and (B) start a new generic app from the `template` branch / `template-v1` tag (`npm ci`, `npm run setup`, `npm run create-app`, `claude`, `/product-interview ...`); requirements (git, Node ≥ 22.12, Python 3.10–3.13); the four commands; the toolkit inventory (link INDEX.md and agents); explain `main` (complete example) vs `template` (generic starter, no SEC app); license. Do not invent the repository URL; write `<repository-url>` as a placeholder the publisher replaces.
3. START-HERE.md: adapt the starter's excellent student guide to the two paths above and to Claude Code / Cline routes (keep its permission and secret advice; Cline: reads AGENTS.md and .clinerules; does not run Claude subagents or slash commands identically; reviewers run as separate tasks; compatibility untested in this build). Include the "check that it works" prompt and the first prompt.
4. PROMPTS.md: the prompt sheet for both tools updated to the new skills (15) and agents, including delegated mode and orchestrated steps (link orchestrate-steps), legend tested/documented (mark Claude Code prompts "documented" unless they were actually run in this build; Cline untested).
5. AI-USAGE.md: keep the template; add a first log row for this build: "2026-11-03, owner (instructor), Claude Code (Opus 5.5) built the toolkit via recorded steps in runs/; checked by toolkit checks and reviews; accepted/changed per runs/".
6. .clinerules/cline.md: update paths/commands; keep its honest caveats. .clineignore: keep, add .cache/ and .logs/.
7. docs/README.md: becomes an index of App Creator's own documentation (TOOLKIT.md, research/, GITHUB-COLLABORATION.md, and the future SETUP/ARCHITECTURE/TEACHING-GUIDE etc. marked "added with the example"), and explains that a new app's product docs live in the configured docs dir (default app/docs/).
Verification: `npm run check-toolkit` must pass for links in your files; report its output.

End your final message with exactly this block (concise):
## Handoff
Changes: <files created/changed>
Verification evidence: <commands run and exit codes>
Remaining findings: <open issues, doubts>
Next action: <one line>
Do not commit, push, tag or change git configuration; the owner integrates and commits. Never read, create or print .env files or secrets, and never write email addresses into files.
<!-- DISPATCH:END -->
