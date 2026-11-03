# RESPONSE — B06-agents

- From: default → to: owner (top-level Claude Code session)
- Captured by: scripts/dispatch-step.mjs from the `result` field of `claude -p --output-format json`
- Session id: 735d38e4-45bf-4eca-9819-dc27a9c8cb86 (local Claude Code transcript; not committed)
- Finished: 2026-11-03T17:14:48.329Z; exit code 0; status completed
- Redaction: only explicit [REDACTED:<kind>] markers were inserted; otherwise verbatim.

<!-- VERBATIM:BEGIN -->
I adapted the four reviewers, fixed one format problem in the orchestrator, and created the seven new agents, all in `.claude/agents/`. All 13 agent files pass the frontmatter check. I didn't commit anything.

**Reviewers** (`code-reviewer`, `security-reviewer`, `test-reviewer`, `ux-reviewer`): they stay read-only, and their report format and good content are unchanged. Each now has a "Where the app is" paragraph: the app's folders come from `app-creator.config.json` (`app.frontendDir`, `app.backendDir`, `app.docsDir`), with `app: null` handled. Checks run through `npm run verify`, `npm run verify -- --quick`, or the narrower commands in the app's README. The old `docs/…` and `app/…` paths now point at the configured docs folder.
- **`ux-reviewer`:** the browser check is now the project's Playwright suite, with screenshots in the frontend's `test-results/` folder. It previews the app with `npm run demo`.
- **`security-reviewer`:** added the same-origin `/api/*` proxy and binding to `127.0.0.1`, CORS limits, SSRF (server-side request forgery: allowlisted hosts and paths, redirects re-checked, no "fetch any URL" endpoint), untrusted HTML rendering, and keys forwarded only for one request and never stored or logged.
- **`test-reviewer`:** added offline-by-default tests with live tests opt-in, synthetic fixtures clearly marked and kept apart, and recorded real fixtures with their source and date. Its description and "Financial checks" are now domain-neutral "Calculation checks".

**Orchestration:** `project-orchestrator` had a `Decision:` line inside the handoff block. I moved it above the block so the four handoff fields match `docs/TOOLKIT.md` §7. `delegated-product-owner` needed no changes. Neither role changed.

**New agents:** `product-architect`, `frontend-engineer`, `backend-engineer`, `design-lead`, `test-engineer`, `docs-writer` and `github-coach`, each 55–64 lines. Each has:
- a role statement, a "Read first" list, numbered steps, the hard rules you listed, and the shared handoff;
- a `skills:` list, which the current format supports, with the skills also named in the text;
- `Agent` left out of its tools, so it cannot start other agents; the owner dispatches them.

`github-coach` cannot edit files.

**Two limits to know about:**
- **Four skills don't exist yet:** `plan-architecture`, `write-docs`, `git-collaboration` and `orchestrate-steps`. Three of the new agents preload them, and the orchestrator reads `orchestrate-steps`. I don't know what Claude Code does with a missing name in `skills:`, so that needs re-checking once they're written.
- **`github-coach` can still run any shell command.** Only its instructions keep it to read-only git, plus the project setting that asks before commands.

Separately, `AGENTS.md` still describes the starter's single `app/` folder and its `app/.env`; I left it alone because it was outside this task. No restart should be needed, since the agents folder already existed.

## Handoff
Changes: modified `.claude/agents/code-reviewer.md`, `security-reviewer.md`, `test-reviewer.md`, `ux-reviewer.md`, `project-orchestrator.md`; created `.claude/agents/product-architect.md`, `frontend-engineer.md`, `backend-engineer.md`, `design-lead.md`, `test-engineer.md`, `docs-writer.md`, `github-coach.md`. `delegated-product-owner.md` unchanged.
Verification evidence: `node /tmp/check-agents.mjs .claude/agents` → 13/13 ok (frontmatter present, name = filename, description present and YAML-safe, tools restricted), exit 0. PyYAML `safe_load` parsed every file's frontmatter, exit 0. `grep` for finance/SEC terms and email addresses → no matches (exit 1 = none found). Agents were not invoked live.
Remaining findings: `plan-architecture`, `write-docs`, `git-collaboration` and `orchestrate-steps` are missing (named in `skills:` or read by the orchestrator); what Claude Code does with a missing preload is unknown, so re-run the check once they exist. `github-coach` read-only git is enforced by its instructions and the project's ask-permissions, not by its tool list. `AGENTS.md` still uses the starter's `app/` paths (out of scope).
Next action: create the four missing skills, then re-run the agent check and dispatch each new agent once to confirm it loads.
<!-- VERBATIM:END -->
