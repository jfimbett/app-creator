# RESPONSE — B01-orchestrator-bootstrap-plan

- From: project-orchestrator → to: owner (top-level Claude Code session)
- Captured by: scripts/dispatch-step.mjs from the `result` field of `claude -p --output-format json`
- Session id: 197beebb-a91d-46c3-aa18-19ab8d601c34 (local Claude Code transcript; not committed)
- Finished: 2026-11-03T17:04:43.231Z; exit code 0; status completed
- Redaction: only explicit [REDACTED:<kind>] markers were inserted; otherwise verbatim.

<!-- VERBATIM:BEGIN -->
Verdict: plan accepted, with two problems to fix before B02 is dispatched. First, `.claude/`, `scripts/` and `runs/` are untracked, so this step's own starting commit (6e8314a) doesn't contain the dispatch script or the orchestrator agent definition. Second, `AGENTS.md`, `app-creator.config.json` and the `orchestrate-steps` skill that my instructions point to don't exist yet.

## 1. Bootstrap steps (in order)

| id | agent | skills | inputs | work (out of scope) | done when | parallel? |
|---|---|---|---|---|---|---|
| B00-commit-dispatch-tooling | owner | – | `.claude/agents/*`, `scripts/dispatch-step.mjs`, `runs/` | Commit the tooling. Note in B01's RESULT.json that it started before this commit. | `git status` clean, apart from B01's in-flight files | no |
| B02-research-claude-code | general (no `--agent`) | – | official Claude Code docs | `docs/research/claude-code.md`: skill and agent frontmatter, the `skills`/`tools` fields, how to check skills are found, whether a subagent can spawn agents (no toolkit edits) | Each claim has a URL and a retrieval date | yes |
| B03-research-sec | general | – | SEC developer and fair-access pages | `docs/research/sec-edgar.md`: submissions, companyfacts, ticker files, archive URL patterns, User-Agent rule, rate limit, 403 behaviour, older submissions files | Same as B02 | yes |
| B04-research-openrouter | general | – | openrouter.ai docs | `docs/research/openrouter.md`: chat and models endpoints, auth, error codes 401/402/429, pricing fields, key limits | Same as B02 | yes |
| B05-research-stack | general | – | Next, Playwright, FastAPI docs | Check the D5/D6 pins work together (Next 16 + TS 6, Tailwind 4, the dev proxy, `PLAYWRIGHT_BROWSERS_PATH`, Python 3.10–3.13) | Mismatches listed; owner amends D5/D6 | yes |
| B06-agents | general | – | B02 notes, the 4 starter reviewers | Keep and adapt `code-`, `security-`, `ux-` and `test-reviewer`. Add `product-architect`, `frontend-engineer`, `backend-engineer`, `design-lead`, `github-coach`, `test-engineer` and `docs-writer`. Touches `.claude/agents/` only. | Frontmatter matches B02 | with B07* and B08 |
| B07a-skills-product-ui | general | – | starter skills, B02 | `product-interview`, `design-interface`, `build-feature`, plus guides for requirements, accessibility, charts and forms | Valid frontmatter, workflow, examples, checks, failure handling | yes |
| B07b-skills-backend-ops | general | – | starter skills | `integrate-api`, `manage-data`, `add-accounts`, `add-payments`, `prepare-deploy`, `test-and-check`, `debug-issue`, `review-changes`, plus guides for CI, Docker and secrets | Same as B07a | yes |
| B07c-skills-process | general | – | B02, GOAL §8 | `orchestrate-steps`, `git-collaboration`, `.claude/skills/INDEX.md` | Same as B07a; the git skill has no destructive defaults | yes |
| B08-root-launchers | backend-engineer if B06 is committed, else general | `test-and-check` | D7, GOAL §4 | Root `package.json` and `scripts/{setup,dev,verify,demo}.mjs` with a generic template mode (`verify` = toolkit lint and link check), plus `scripts/lint-toolkit.mjs` | `npm ci && npm run setup && npm run verify` exit 0 twice in a row (idempotent); `setup` refuses Python 3.9 | yes |
| B09-root-docs | docs-writer | `git-collaboration` | B06, B07, B08 | `CLAUDE.md`, `AGENTS.md`, `START-HERE.md`, `AI-USAGE.md`, `PROMPTS.md`, `README`, `.clinerules` (Cline marked untested), `app-creator.config.json`, `docs/GITHUB-COLLABORATION.md`, `docs/SOURCES.md` (merged from B02–B05) | Links resolve under `npm run verify` | no |
| B10-toolkit-discovery | test-engineer | `test-and-check` | everything above | In a fresh `claude -p` session, confirm the skills and agents are found. Run `verify`. | Evidence saved under `runs/` | no |
| B11-review-toolkit | code-reviewer ∥ security-reviewer | `review-changes` | the toolkit diff | Read-only review | Findings saved | yes (2) |
| B12-repair-toolkit | as assigned | – | B11 findings | Fix the blocker and major findings | Reviewers' items closed or recorded | no |
| B13-interview-questions | product-architect | `product-interview` | GOAL, research notes | Write the interview questions only | Questions file | no |
| B14-interview-answers | delegated-product-owner | `product-interview` | B13, GOAL, PROGRESS | Answer each question, citing either a GOAL § or "delegated default" | Every question answered | no |
| B15-product-docs | product-architect | – | B14 | `docs/PRODUCT-DECISIONS.md` plus `milestones/` product, architecture, acceptance (criteria ids) and plan docs | Each decision traces to an answer | no |
| B16-milestone-prompts | product-architect | – | B15, B03, B04 | The five `PROMPT.md` files, each self-contained: starting ref, context, new work, design, architecture, defaults, tests, acceptance ids | Ref chain template-v1→m1→…→m4 | no |
| B17-review-prompts | project-orchestrator | – | B16, GOAL §4–7 | Check against GOAL: SEC rules, AI/key rules, nothing from later milestones leaking into earlier ones | accept / repair | no |
| B18-gate-template | orchestrator, then owner | – | – | Gate run; owner commits, creates the `template` branch and annotated `template-v1` tag | §3 below | no |

## 2. Running steps in parallel

- B02–B05 can all run together. Each writes only its own file under `docs/research/`.
- B06, B07a/b/c and B08 can run together:
  - B06 writes only `.claude/agents/`.
  - B07a/b/c each write only their named skill folders under `.claude/skills/`. Only B07c touches `INDEX.md`.
  - B08 writes only `package.json`, `package-lock.json` and `scripts/` (apart from `dispatch-step.mjs`).
- The B11 reviewers are read-only.
- Shared contracts:
  - Skill names are frozen to the list above. Agents refer to skills by name only.
  - `docs/SOURCES.md` and `runs/INDEX.md` are written only by the owner or the dispatch script.
  - `PROGRESS.md` is owner-only.

## 3. Gate for the template-v1 checkpoint

**Must be true:**
- In a clean worktree of the candidate commit: `npm ci && npm run setup && npm run verify` exit 0. `dev` and `demo` give a working generic flow or clear guidance (never a crash).
- B10 confirms skills and agents are found.
- All five `PROMPT.md` files exist, with hashes recorded in PROGRESS.
- `docs/PRODUCT-DECISIONS.md` exists.
- Every step from B01 onward has PROMPT, RESPONSE and RESULT files, or a missing-message marker.
- The B11 and B17 findings are closed or recorded.
- START-HERE explains `main` versus `template`.
- `template-v1` is an annotated tag and was not there before.

**Must NOT be present:**
- `examples/sec-analytics/{frontend,backend,fixtures}` code or data.
- Finance rules in the root `CLAUDE.md`/`AGENTS.md` or in generic skills.
- `.env`, keys, `app-starter.zip`, `node_modules`, `.venv`, `.cache`.
- The user's email anywhere in tracked files, including `runs/` transcripts. Check with grep before the commit.

## 4. Risks in GOAL.md for this phase

1. **Template contains SEC content.** GOAL wants the template to include the SEC prompts and `docs/PRODUCT-DECISIONS.md`, but also "no financial assumptions in generic starter". Proposed fix: SEC planning content goes only under `milestones/`, and `PRODUCT-DECISIONS.md` gets a heading that scopes it to the example. The owner should confirm this reading of D8.
2. **What `npm run` does in the template is undefined.** GOAL requires the commands to work "at EVERY milestone", but the template has no app. The generic mode needs to be defined in B08.
3. **Gap in the step records.** B01 started before its tooling was committed. B00 must record this; it must not be hidden.
4. **Self-reference.** The agents the toolkit creates don't exist yet during B02–B07, so those steps run under the default agent. Record this honestly per GOAL §8.
5. **Python default.** `python3` here is 3.9 (Anaconda), so setup must find 3.10+ explicitly. Students on Windows will hit the same problem.
6. **Secrets in transcripts.** Child sessions run with `bypassPermissions` (D4). Agents reading `.env` relies on deny rules that are not committed yet. B08 or B09 must commit `.claude/settings.json` before any implementation step.
7. **Version pins (D5/D6).** These are from registry metadata and still need B05 confirmation from official docs. TS 6 with Next 16 is the most likely to break.
8. **Interview order.** The interview should use the adapted `product-interview` skill (after B12), not the starter's version. Otherwise "actually used the toolkit" is weak.
9. **Owner-only items:** confirming D2's email handling (redaction patterns must include it), and the new-repo check, which is deferred to publication. Neither blocks bootstrap.

## Handoff
Changes: none (orchestrator is read-only)
Verification evidence: read GOAL.md (all 214 lines) and PROGRESS.md. `git log` shows one commit, 6e8314a. `git status` shows `.claude/`, `runs/` and `scripts/` untracked. Read the B01 RESULT.json and the header of `dispatch-step.mjs`. `AGENTS.md`, `app-creator.config.json` and the `orchestrate-steps` skill are absent. No checks were run (none exist yet).
Decision: plan
Remaining findings: risks 1–9; risks 1, 2 and 6 need the owner to decide before B08 or B09.
Next action: B00-commit-dispatch-tooling (owner), then B02–B05 in parallel (general agent, no `--agent`).
<!-- VERBATIM:END -->
