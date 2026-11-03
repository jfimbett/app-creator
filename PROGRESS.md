# PROGRESS — App Creator build

Resumable state for the autonomous build described in `GOAL.md`. Updated throughout. No secrets in this file.

## Current phase

M1 Foundation (template-v1 created at d387e3d)

## Audit (2026-11-03)

| Item | Finding |
|---|---|
| Folder | `/Users/[REDACTED:user]/Documents/app-creator`; contained only `GOAL.md` and `app-starter.zip`; was **not** a git repo; no parent repo |
| Git | 2.45.2; repo initialised here on `main`; commit identity from the user's existing global config (not invented) |
| GitHub CLI | 2.72.0; authenticated as personal account `jfimbett` (scopes include `repo`, `workflow`) |
| Remote | `jfimbett/app-creator` query returned "Could not resolve to a Repository" (GraphQL, authenticated) → name appears free; re-check before creation |
| Node / npm | v22.14.0 / 11.17.0 |
| Python | PATH `python3` = Anaconda base 3.9.19 (too old for FastAPI 0.150, base install must not be modified); `/opt/homebrew/bin/python3.10` (3.10.x) on PATH; conda envs with 3.11/3.12 exist (not used by default) |
| Browser | Playwright cache in `~/Library/Caches/ms-playwright` exists (not relied upon; project-local browsers are installed by setup) |
| Claude Code | 2.1.317; `claude -p --agent <name> --output-format json` available (used for step dispatch + verbatim capture) |
| Cline | CLI 3.0.47 installed at `~/.nvm/.../bin/cline`; not configured for this project → Cline compatibility **untested** |
| User skills | `~/.claude/skills`: critique-discussion, graphify, synced (unrelated; untouched) |
| Credentials | `OPENROUTER_API_KEY` not set → live AI validation will not be run; SEC contact not set in env |
| SEC network | `data.sec.gov` reachable (HTTP 200) |
| Starter ZIP | `app-starter.zip` present and inspected (extracted to session scratchpad only). Version 0.3.0: 11 skills, 4 read-only reviewer agents, `.claude/settings.json`, `.clinerules/cline.md`, `.clineignore`, `.gitignore`, `.gitattributes`, AGENTS/CLAUDE/START-HERE/PROMPTS/AI-USAGE. Preserved and adapted (not reconstructed). The ZIP itself is kept locally and git-ignored. |

## Decisions

| # | Decision | Basis |
|---|---|---|
| D1 | Repo at the existing folder; `main` default branch | GOAL §2/§3; folder not inside another repo |
| D2 | SEC User-Agent contact = the user's email, only in ignored local `.env` / process env, never committed | Explicit user answer in chat, 2026-11-03 |
| D3 | Dispatch every delegated step with `node scripts/dispatch-step.mjs` → `claude -p --agent <role> --output-format json`; RESPONSE.md is copied from the JSON `result` field (verbatim), session id recorded | GOAL §8 exact records; avoids hand transcription |
| D4 | Child sessions for implementation run with `--permission-mode bypassPermissions` (same mode the user started this session in); project `.claude/settings.json` deny rules for `.env` stay in place; reviewer agents restricted by their `tools` frontmatter | user-authorised unattended build |
| D5 | Frontend pins (newest stable ≥ 2 weeks old on 2026-11-03): next 16.4.2, react/react-dom 19.3.1, tailwindcss 4.3.3, recharts 3.10.1, @playwright/test 1.64.1, typescript 6.0.3 (TS 7 avoided until Next documents support), eslint 10.13.0, eslint-config-next 16.4.2, vitest 4.1.12 | npm registry `time` metadata |
| D6 | Backend pins: fastapi 0.150.0, uvicorn 0.54.0, httpx 0.28.1, pydantic 2.14.1, pytest 9.1.1, ruff 0.17.1, respx 0.23.1, beautifulsoup4 4.15.0; supported Python 3.10–3.13 | PyPI metadata |
| D7 | Root launcher has no runtime npm dependencies (portable `node:` built-ins); root `npm ci` still documented | GOAL §4 portability |
| D5b | Amended after B05: Node floor **22.12**, then **22.13** after B08 (eslint 10 engines) (vitest 5 + eslint 10 + Playwright support 22/24/26; Node 20 is EOL); vitest **5.0.5**; TS 6.0.3 kept because typescript-eslint peer is `<6.1.0`; add pins @tailwindcss/postcss 4.3.3, postcss, react-is 19.3.1, @types/*, vite 8.x, @vitejs/plugin-react, jsdom, @testing-library/*; shadcn components generated once and committed (CLI never runs at student install) | runs/bootstrap/B05-research-stack, docs/research/stack-versions.md |
| D8 | SEC planning docs (product/architecture/acceptance/plan) live in `milestones/`; generic app docs default to `app/docs/` (configurable in `app-creator.config.json`) | template must contain prompts but no SEC implementation |

## Phase log

- B01 orchestrator plan (accepted); B00 tooling commit 10e8c6f; starter import 47dbf85; B02–B05 research done (docs/research/).
- Incident: an unquoted heredoc expanded backticks while writing B07 prompts (ran harmless failing `npm ci`/usage commands; no files changed). Corrupted undispatched prompts deleted and regenerated with quoted heredocs.

- B06 agents (13) committed 2dd841e. B08 launcher/scaffold + B07c2 process skills committed a9f221e. Node floor raised to 22.13 (eslint 10 engines) b127968.
- B07c dispatched to github-coach by mistake (no write tools) → terminated (exit 143), recorded as failed; same text re-dispatched as B07c2 to docs-writer (completed).
- Live discovery evidence: this running session listed newly created project skills and agents without restart (system notices after B06/B07).
- Local note: other services (not ours) occupy ports 3000/8000 on this machine; `npm run dev` refuses them by design; use BACKEND_PORT/FRONTEND_PORT.

- B09 root docs, CI (de1627f). B10 questions (44) → B11 delegated answers → B12 decisions + planning docs (49dd630). B13 milestone prompts (23e9a15). B15a/B15b toolkit reviews: pass with minor issues, no blockers; B16 repaired code #1–#12 and security #3–#8 (6727dc2). B14 orchestrator review: M1/M4 accept, M2/M3/M5 repair → B17 applied all edits; owner fixed 2 stale lines B17 flagged (M1 prompt line 451, product.md line 106). B18 fresh-session discovery: all 15 project skills and 13 agents loaded.
- Home paths in tracked records redacted with `[REDACTED:user]` (scripts/redact-records.mjs). One over-match (a regex quoted in B15b's response) was reverted to verbatim and the pattern tightened.
- **Open owner decisions (not delegable, reported, not changed):** security #1, the commit author email (the user's own global git identity) becomes public on push; security #2, harden `.claude/settings.json` deny rules (e.g. `Read(./**/.env.*)`, `Bash(* .env*)`). The file belongs to the user, so it is left unchanged.
- Prompt hashes (sha256) at template candidate: M1 2984572…03ac, M2 35112cc…45b, M3 a1b6939…20f7, M4 47af2b5…0b32, M5 c3caadf…8c99 (full values in runs/bootstrap/B19 RESULT and docs/PROMPT-EXECUTION-LOG.md later).

## Next actions

1. m1-01 orchestrator plans M1 from milestones/01-foundation/PROMPT.md. 2. Implementation steps embed the brief verbatim plus a step scope. 3. Reviews, repairs, clean verify, gate → `milestone/01-foundation` + `m1`.

## Checkpoints

| Ref | SHA | Verified |
|---|---|---|
| `template` / `template-v1` (annotated) | d387e3d82f55a3ef385eade69598784fff0cf148 | clean worktree npm ci → setup → verify exit 0 (2026-11-03 18:23Z); orchestrator gate-pass (B19) |

## Publication status

Not started.

## Failures / blockers log

- **Correction (owner error).** The two `.claude/settings.json` "rewrites" at ~17:31Z and 17:37:09Z were the **user's own `/permissions` edits** (deleting Ask rules), not an unexplained writer. The owner wrongly reverted them twice with `git restore` and added a guard requiring an Ask rule. Fixed 2026-11-03 at the user's request: the effective sources were inspected (project `.claude/settings.json` was the only file that ever defined `Bash(git commit *)` / `Bash(git push *)` Ask rules; `.claude/settings.local.json` and `~/.claude/settings.json` define none; no managed policy file exists). The user's current file (`ask: []`) is kept as saved; no settings file needed editing. All deny rules (`.env` read/edit, force-push, `reset --hard`, `clean`) are intact. `check-toolkit` now checks only the deny rules, never Ask rules. Rule for the rest of the build: never restore or overwrite the user's settings changes.
- 2026-11-03 ~18:15–18:40Z: clean-worktree verify of the template candidate failed intermittently: `page.screenshot` timed out (30 s) after assertions passed (aa64ab4 run 1 fail, run 2 pass; a991929 all four attempts fail incl. retry). A first guess (cold start → `retries: 1`, a991929) was **wrong** and has been reverted. Diagnosis with a minimal script (scratchpad `shot-diag.mjs`): at the same moment, a trivial `<h1>` page screenshot hangs in Playwright's `chromium_headless_shell-1248` (any flags) but works in full Chromium new-headless (`channel: "chromium"`, ~1 s) and in installed Chrome. Fix: setup installs `--no-shell chromium` (project-local) and the Playwright config uses `channel: "chromium"`; `npm run verify` then passed under the same conditions. Underlying OS trigger (likely display sleep/idle state) not verified.

## M1 log

- m1-01 orchestrator plan (15 steps). Implementation steps embed `milestones/01-foundation/PROMPT.md` from `template-v1` verbatim (sha256 2984572…03ac) after a step scope (helper: scratchpad mkimpl.py).
- m1-02 skeleton 08642b2; m1-03/04/08/09 (assistant files, SEC client, design shell, frontend lib) b3879a0; m1-05 authentic fixtures (live SEC 2026-11-03, 7 requests; SEC_USER_AGENT passed via process env only, never written) + m1-07 periods 59571f0; m1-06 backend API c5dee9b; m1-07b overview 9fb82b8. Integrated `npm run verify` exit 0 after each group.
- m1-10 screens in progress.
