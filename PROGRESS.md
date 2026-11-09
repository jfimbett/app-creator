# PROGRESS — App Creator build

Resumable state for the autonomous build described in `GOAL.md`. Updated throughout. No secrets in this file.

## Current phase

**M4 complete (2026-11-09): tag `m4`, branch `milestone/04-comparative-analysis`; local `main` fast-forwarded to M4. Not pushed. M5 not started. Wait for the instructor.**

## M4 completion (2026-11-09, newest)

- Instruction: `runs/m4/m4-01-implement-main-session/PROMPT.md` ("ok push and start working on m4"). Results: its `RESULT.json`.
- Worktree `.worktrees/m4`, local branch `work/m4`, from `main` 6f6ab1d (tag `m3` plus one documentation commit).
- **Not pushed.** GitHub still shows `main` = M3. Pushing `main`, `milestone/04-comparative-analysis` and `m4` waits for the instructor.
- Open minor items: `milestones/plan.md` "Known problems" (M4 items).

## M3 completion (2026-11-09, newest; overrides the sections below where they differ)

- Instruction: `runs/m3/m3-04-finish-main-session/PROMPT.md` ("continue m3 … work autonomously"). Results: its `RESULT.json`.
- Machine: Windows 11 (earlier work was on macOS). Worktree `.worktrees/m3`, local branch `work/m3-finish`, started from `wip/m3-filing-intelligence-unverified` merged with `main`.
- Done: Windows fix for the offline-network test guard; six M3 Playwright journeys; screens looked at (1440 and 390 px); two screen fixes; one live SEC retrieval (NVIDIA filing list and 10-K, read and searched in the browser); independent security and test reviews (subagents), with their findings fixed and tested.
- **Pushed 2026-11-09** at the instructor's request: `main`, `milestone/03-filing-intelligence` and tag `m3` on GitHub.
- The published branch `wip/m3-filing-intelligence-unverified` is superseded by `m3`; deleting it on GitHub is the instructor's decision.
- No classroom app is running on this machine.

**Still deferred:** M4, M5; Cline and CI checks; permission hardening; the remaining final documents listed below.

## After the classroom freeze (newest; overrides the handoff below where they differ)

- **`main` contains M2 functionality** plus records and documents only. Student guide: `CLASSROOM.md`. Prompt index: `milestones/PROMPT-INDEX.md`. Freeze instruction: `runs/m3/m3-03-classroom-freeze/PROMPT.md`.
- **M3 partial work:** branch `wip/m3-filing-intelligence-unverified`, status in its `WIP-STATUS.md`. No `m3` tag and no `milestone/03-filing-intelligence` branch exist. Local worktree: `.worktrees/m3`. The local branch `work/m3` is the old starting point and is not published.
- **Remote:** `origin` is https://github.com/jfimbett/app-creator (public, created at the instructor's request). No cloud deployment. New commits use the GitHub noreply address, passed per commit; older commits keep the author email, as the instructor authorized. Git configuration was not changed.
- **Classroom app:** still the M2 process on 3200/8200 from the main checkout; it was not restarted.

**Deferred**

1. Finish M3: run `npm run setup` and `npm run verify` on the WIP branch, write `e2e/m3-filings.spec.ts`, inspect the screens, run the live journey, update the documents and statuses, then pass the gate and create `milestone/03-filing-intelligence` and `m3` at the verified commit.
2. M4 and M5.
3. Independent reviews; Windows, Cline and CI checks. GitHub CI results have not been assessed as evidence.
4. Permission hardening. `CLAUDE.md` still says "every other command asks", which does not match the instructor's settings.
5. Remaining final documents: ARCHITECTURE, TEACHING-GUIDE, CHANGELOG, FINAL-VERIFICATION, PROMPT-EXECUTION-LOG, SOURCES.
6. Decide whether to set the noreply address in the repository's git configuration.

## Handoff for a new session (written 2026-11-04, before a context clear)

Read this section first. The older sections below are history.

**Verified refs (do not move or rewrite)**

| Ref | Commit | State |
|---|---|---|
| `template-v1`, branch `template` | `d387e3d` | generic toolkit |
| `m1`, branch `milestone/01-foundation` | `bd8ab81` | M1 verified |
| `m2`, branch `milestone/02-financial-intelligence` | `4451d43` | M2 verified: clean worktree `npm ci`, setup, verify exit 0; pytest 320, Vitest 83, Playwright 24; live SEC checks passed separately |
| `main` | `6088a29` plus the handoff commit that adds this section (`git log -1 main` shows it) | `m2` plus records only; no application changes since `m2` |

Nothing has been pushed; there is no remote.

**Working directories**

- Main checkout: `/Users/[REDACTED:user]/Documents/app-creator`, branch `main`. The classroom app runs from here, so do not change app files here.
- M3 worktree: `.worktrees/m3` (git-ignored), branch `work/m3`, at the same commit as `main`, with a `.env` symlink to the root `.env`.
  It has no dependencies yet: run `npm ci` and `npm run setup` there first. Use separate ports, for example 3300/8300.

**Running services**

| Service | Address | Started by | Mode |
|---|---|---|---|
| Classroom app, verified M2, frontend | http://127.0.0.1:3200 | `npm run dev` from the main checkout, detached | Demo/Live selector, starts on Demo; live configured |
| Classroom app, backend | 127.0.0.1:8200 | same process | |
| Other services, not ours; leave them alone | ports 3000 and 8000 | unknown | the launcher refuses these ports |

Check with `curl -s http://127.0.0.1:3200/api/meta`. These processes may not survive a machine restart. Restart:

```bash
pkill -f 'scripts/dev.mjs'
cd /Users/[REDACTED:user]/Documents/app-creator
FRONTEND_PORT=3200 BACKEND_PORT=8200 npm run dev
```

`pkill -f 'scripts/dev.mjs'` stops every dev launcher, including one started from the M3 worktree, so check first. Offline only:
`npm run demo` with the same ports.

**Local configuration (no values recorded here)**

- Root `.env`, git-ignored, holds `SEC_USER_AGENT` only, created at the instructor's explicit request for live SEC. Never print it,
  read it or commit it. The project's deny rules block reads, and shell commands naming that file may be refused too: that is correct, so
  do not work around it. To check live configuration, use `live_configured` from `/api/meta`. Students use their own contact.
- Node 22.14 (floor 22.13). Python: `/opt/homebrew/bin/python3.10`, found automatically by `npm run setup`. No OpenRouter key exists, and
  none should be requested in chat.
- Chromium is project-local at `.cache/ms-playwright`, full Chromium via `channel: "chromium"`. The headless shell hung here.

**Permission settings: preserve them**

The instructor removed the Ask rules with `/permissions`. `.claude/settings.json` has `"ask": []` and 20 deny rules. Do not restore Ask rules,
overwrite the file or run `git restore` on it. `check-toolkit` checks deny rules only. Permission hardening is deferred, and only with the instructor's decision.

**Instructions and records**

- Goal: `GOAL.md`. Current M3 instruction, saved verbatim before any work: `runs/m3/m3-01-implement-main-session/PROMPT.md`. It includes a rule: on the classroom freeze
  instruction, stop adding features, preserve unfinished work and run the latest verified milestone.
- M3 brief: `milestones/03-filing-intelligence/PROMPT.md`. Criteria: `milestones/acceptance.md` (M3-AC1 to AC7, M3-E1 to E5). Decisions: `milestones/architecture.md`.
- M2 record: `runs/m2/m2-01-implement-main-session/` (prompt, result, evidence logs). M1: `runs/m1/`. Index: `runs/INDEX.md`. Setup guide: `docs/SETUP.md`.
- **Capture gaps:** for main-session steps, `RESPONSE.md` holds a marker instead of the final message. That message is only in the session transcript. A context clear does not recover it. Mark gaps this way; never reconstruct them.
- Session-local helpers in the old scratchpad (`mkstep.py`, `mkimpl.py`) are not in the repo and are not needed in main-session mode.

**M3 is next. Facts already read from the brief and fixtures (no implementation exists)**

- Starting point: `work/m3`, which descends from `m2`. Run `npm run verify` as the brief asks before changing anything.
- The fixtures have no filing documents yet. `capture_fixtures.py --filings` is to be added: latest original 10-K and 10-Q per company, 6 requests, stored gzip-compressed. Do not change existing fixture data files.
- **The recorded snapshot holds no 10-K/A or 10-Q/A rows**, so amendment labels rely on synthetic tests unless older pages supply some. Say so.
- The instructor's M3 instruction also asks that a recorded excerpt is never presented as the full document, and a recorded filing never as the latest live report.
- `beautifulsoup4==4.15.0` must be added to the backend lock (`html.parser`, no lxml).
- Switch the classroom app to M3 only after its gate passes. If M3 is blocked, leave M2 running. On a pass, create branch `milestone/03-filing-intelligence` and annotated tag `m3` at the verified commit.

**Deferred, do not start**

- M4 and M5: after class.
- Publication to GitHub. Before it, the instructor decides on the public commit email and permission hardening.
- Independent reviews; Windows, Cline and CI checks; the remaining final documents (ARCHITECTURE, TEACHING-GUIDE, CHANGELOG, FINAL-VERIFICATION, PROMPT-EXECUTION-LOG, SOURCES).
- `CLAUDE.md` still says "every other command asks", which no longer matches the instructor's settings. Fix only with toolkit work.
- Known M2 limitations: see `milestones/plan.md`, "Known problems".

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
| `milestone/01-foundation` / `m1` (annotated) | bd8ab814e35245a3dd9701f92910d541b5671892 | clean worktree npm ci → setup → verify exit 0 (2026-11-04 06:46Z): pytest 196, Vitest 70, Playwright 9; gate decided in the main session; same-session review only |
| `milestone/02-financial-intelligence` / `m2` (annotated) | 4451d43fd52f6e08c2db7a41b16434c4f078605e | clean worktree npm ci → setup → verify exit 0 (2026-11-04 07:14Z): pytest 320, Vitest 83, Playwright 24; live SEC checks passed separately; gate decided in the main session; same-session review only |

## Publication status

Published 2026-11-04 to https://github.com/jfimbett/app-creator after a secret and privacy review of the published refs. See "After the classroom freeze".

## Failures / blockers log

- **Correction (owner error).** The two `.claude/settings.json` "rewrites" at ~17:31Z and 17:37:09Z were the **user's own `/permissions` edits** (deleting Ask rules), not an unexplained writer. The owner wrongly reverted them twice with `git restore` and added a guard requiring an Ask rule. Fixed 2026-11-03 at the user's request: the effective sources were inspected (project `.claude/settings.json` was the only file that ever defined `Bash(git commit *)` / `Bash(git push *)` Ask rules; `.claude/settings.local.json` and `~/.claude/settings.json` define none; no managed policy file exists). The user's current file (`ask: []`) is kept as saved; no settings file needed editing. All deny rules (`.env` read/edit, force-push, `reset --hard`, `clean`) are intact. `check-toolkit` now checks only the deny rules, never Ask rules. Rule for the rest of the build: never restore or overwrite the user's settings changes.
- 2026-11-03 ~18:15–18:40Z: clean-worktree verify of the template candidate failed intermittently: `page.screenshot` timed out (30 s) after assertions passed (aa64ab4 run 1 fail, run 2 pass; a991929 all four attempts fail incl. retry). A first guess (cold start → `retries: 1`, a991929) was **wrong** and has been reverted. Diagnosis with a minimal script (scratchpad `shot-diag.mjs`): at the same moment, a trivial `<h1>` page screenshot hangs in Playwright's `chromium_headless_shell-1248` (any flags) but works in full Chromium new-headless (`channel: "chromium"`, ~1 s) and in installed Chrome. Fix: setup installs `--no-shell chromium` (project-local) and the Playwright config uses `channel: "chromium"`; `npm run verify` then passed under the same conditions. Underlying OS trigger (likely display sleep/idle state) not verified.

## M1 log

- m1-01 orchestrator plan (15 steps). Implementation steps embed `milestones/01-foundation/PROMPT.md` from `template-v1` verbatim (sha256 2984572…03ac) after a step scope (helper: scratchpad mkimpl.py).
- m1-02 skeleton 08642b2; m1-03/04/08/09 (assistant files, SEC client, design shell, frontend lib) b3879a0; m1-05 authentic fixtures (live SEC 2026-11-03, 7 requests; SEC_USER_AGENT passed via process env only, never written) + m1-07 periods 59571f0; m1-06 backend API c5dee9b; m1-07b overview 9fb82b8. Integrated `npm run verify` exit 0 after each group.
- m1-10 screens in progress.

## Classroom recovery (2026-11-04)

- Instructor request saved in `runs/recovery/R01-classroom-demo/`; worked in the main session with no dispatched agents.
- m1-11-e2e had hit its 60-minute timeout on 2026-11-03 (exit 143, no message, no spec written); cause not diagnosed. No project agents were still running.
- Demo: `FRONTEND_PORT=3200 BACKEND_PORT=8200 npm run demo` → http://127.0.0.1:3200 (ports 3000/8000 are held by unrelated services, left alone).
- Fixes: favicon, Next.js dev badge off, `frontend/AGENTS.md` git-ignored, browser journey `e2e/demo-journey.spec.ts`.
- Evidence: journey passes against the dev server at 1440 px; lint and typecheck exit 0; API values match the raw fixtures; three desktop screenshots inspected.

### Deferred until after class

1. Done (m1 gate).
2. Done at `m1` except independent reviews, which the instructor set aside for this mode: consider them before publication.
3. Diagnose the m1-11 stall before dispatching more long steps; give long steps smaller scopes.
4. M2–M5, final documentation set (SETUP, ARCHITECTURE, TEACHING-GUIDE, CHANGELOG, FINAL-VERIFICATION, PROMPT-EXECUTION-LOG, SOURCES), record audit.
5. Publication (nothing pushed; no remote exists). Open owner decisions first: public commit email (security #1) and `.claude/settings.json` deny hardening (security #2).
6. `CLAUDE.md` says "every other command asks", which no longer matches the owner's settings (Ask rules removed); correct the wording.
7. scratchpad helpers (mkimpl.py, mkreview.sh) are session-local; move them to `scripts/` if the recorded workflow resumes.

## M1 completion (2026-11-04)

- Instruction saved in `runs/m1/m1-16-complete-m1-main-session/` and `milestones/01-foundation/FOLLOWUPS.md`. It replaced planned steps m1-11 to m1-15.
- Added `e2e/m1-foundation.spec.ts`, removed the scaffold smoke spec, made the backend-down header message visible (a real M1-E1 defect), completed documents and statuses.
- Next, only on instruction: M2 from `m1`. Demo: `FRONTEND_PORT=3200 BACKEND_PORT=8200 npm run demo` → http://127.0.0.1:3200.

## M2 completion (2026-11-04)

- Instruction saved before work in `runs/m2/m2-01-implement-main-session/PROMPT.md` and in `milestones/02-financial-intelligence/FOLLOWUPS.md`.
- **SEC contact:** at the owner's request, a root `.env` holds their `SEC_USER_AGENT` (git-ignored, permissions 600, created once by the assistant; value not recorded). `AGENTS.md` says assistants never create `.env`: this was the owner's explicit exception.
- Live testing on real companies found four defects that fixtures could not show; all fixed with tests (see `milestones/plan.md`).
- Deviations: synchronous SEC client (brief's table says async), capex alternate outside `CAPTURE_CONCEPTS`, stricter debt rule. Recorded in the architecture decision log.
- Classroom app: `FRONTEND_PORT=3200 BACKEND_PORT=8200 npm run dev` → http://127.0.0.1:3200 (starts on Demo, Live selector available). Plain offline demo: `npm run demo`.
- **Deferred:** M3–M5, independent reviews, GitHub publication, commit-email decision, permission hardening, remaining final documents. Next, only on instruction: M3 from `m2`.
- Classroom switch done 2026-11-04: main fast-forwarded to the m2 records commit, `npm run dev` on 3200/8200, live journey passed against it, and 23 of the 24 offline journeys passed (the 24th asserts that a demo run has no selector, so it cannot apply in a dev run; it passed under `npm run demo` and in the gate). Temporary worktree `.worktrees/m2` and branch `work/m2` removed.
