# RESPONSE — B15b-review-toolkit-security

- From: security-reviewer → to: owner (top-level Claude Code session)
- Captured by: scripts/dispatch-step.mjs from the `result` field of `claude -p --output-format json`
- Session id: bfc20769-5511-418d-a4bd-d3c1b43c1e84 (local Claude Code transcript; not committed)
- Finished: 2026-11-03T17:52:49.492Z; exit code 0; status completed
- Redaction: only explicit [REDACTED:<kind>] markers were inserted; otherwise verbatim.

<!-- VERBATIM:BEGIN -->
# Security reviewer report: App Creator toolkit, all tracked files and history (template mode, `"app": null`)

**Verdict: pass with minor issues.** There are no blockers. No secret, key, `.env` or other forbidden file is tracked now or in history. Two major issues should be decided before publishing: your personal email is in every commit's metadata, and the `.env` protections are weak when steps run in bypass mode.

**Checks run:**
- `npm run verify -- --quick`: exit 0. Toolkit checks passed, and the scaffold passed ruff, pytest, frontend lint, typecheck and unit tests.
- `git ls-files` searched for `.env`, `node_modules`, `.venv`, `.cache`, `app-starter.zip` and key files: only `.env.example` is tracked.
- `git log --all --diff-filter=A` searched for the same files across history: only `.env.example` was ever added.
- `git grep` and `git log -p --all` searched for provider key prefixes (`sk-or-v1-`, `sk-ant-`, `ghp_`, `github_pat_`, `AKIA`, `AIza`, `xox*`, private keys) and for key or password assignments: nothing found.
- Searched tracked files and `runs/` for email addresses: none found. The only email domains in history are the commit metadata (gmail.com) and `anthropic.com` (Co-Authored-By trailer).
- Searched tracked files for home-folder paths: found (finding 3).

| # | Severity | Status | File:line | Finding | Evidence / reproduction | Suggested correction |
|---|---|---|---|---|---|---|
| 1 | major | verified | git history: all 10 commits (author and committer) | Every commit's author and committer email is a personal gmail.com address. Publishing the repo publishes that address. | `git log --all --format='%ae %ce'` with the address masked: 10 of 10 commits use a gmail.com address. | Owner decision. Before the first push, set `git config user.email <id>+<login>@users.noreply.github.com`. If the address must not be public, rewrite the unpublished history's author metadata, for example with `git filter-repo --mailmap`. This needs your explicit go-ahead and must happen before `template-v1` is tagged. |
| 2 | major | verified | .claude/settings.json:24-45; runs/*/RESULT.json | 16 of 18 recorded steps ran with `permissionMode: bypassPermissions`. In that mode only the deny rules stop anything. The Bash deny rules only catch `cat *.env` and `cat */.env`, so commands like `head .env`, `grep . .env`, `sed -n p .env`, `node -e "…readFileSync('.env')"` or `python -c` can still read it. The Read deny list also misses `.env.development`, `.env.test` and `.env.staging`. Force-push deny can be dodged with `git push origin main --force` or `git push origin +main`. | `grep -h '"permissionMode"' runs/*/*/RESULT.json` prints 16× bypassPermissions and 2× default. Read the `deny` array in `.claude/settings.json`. `docs/research/claude-code-and-cline.md:90-94` confirms deny rules are the only guard under bypass. | Add `"Read(./**/.env.*)"` (keeping `.env.example` readable is fine), and Bash deny rules such as `Bash(* .env)`, `Bash(* .env *)`, `Bash(*/.env*)` and `Bash(git push * --force*)`. Consider adding `"disableBypassPermissionsMode": "disable"`. In `step-records.md`, keep `acceptEdits` as the default and say that deny rules are a guardrail, not a boundary. |
| 3 | minor | verified | runs/bootstrap/B02…B12/stderr.log:1 (14 files); PROGRESS.md:13 | Tracked step records contain an absolute home path that shows your macOS username. `redact()` does not cover home paths. | Searching tracked files for `/Users/[A-Za-z]+` matches all 14 `stderr.log` files at line 1, plus `PROGRESS.md:13`. | In `redact()`, add `.replace(/(\/Users\/|\/home\/|C:\\Users\\)[^\/\\\s"]+/g, '$1[REDACTED:user]')`. Redact the existing logs and `PROGRESS.md:13` before publishing, or accept them knowingly. |
| 4 | minor | verified | scripts/dispatch-step.mjs:37-45 | The redaction list misses common key formats: OpenAI-style `sk-…`/`sk-proj-…`, `github_pat_…`, AWS `AKIA…`, Google `AIza…`, Slack `xox?-…` and PEM private keys. `PROMPT.md` is never redacted, and nothing checks it before dispatch. | Read the code: only the OpenRouter, Anthropic, `gh?_`, Bearer and email patterns are handled. | Add `/\bsk-(proj-)?[A-Za-z0-9_-]{20,}/`, `/\bgithub_pat_[A-Za-z0-9_]{20,}/`, `/\bAKIA[0-9A-Z]{16}\b/`, `/\bAIza[0-9A-Za-z_-]{30,}/`, `/\bxox[abprs]-[A-Za-z0-9-]{10,}/` and `/-----BEGIN [A-Z ]*PRIVATE KEY-----[\s\S]*?-----END [A-Z ]*PRIVATE KEY-----/`. Refuse to dispatch if `redact(dispatched) !== dispatched`. |
| 5 | minor | verified | scripts/lib.mjs:125-127, 310; scripts/verify.mjs:66-72, 89 | `mergedEnv()` passes the whole root `.env` to every child process: ruff, pytest, Next.js and Playwright. The `demoEnv` override only reaches the build and the browser test. So if a student's `.env` holds `DATA_MODE=live` and a real key, `npm run verify` can make live, possibly paid, calls from a test that isn't isolated. This conflicts with "verify passes with no `.env`" (integrate-api/SKILL.md:90). Backend secrets also reach the Next.js process, though integrate-api/SKILL.md:14 says the `.env` goes "to the backend". | Read the code path: `run(spec, { env = mergedEnv() })` is the default for pytest (verify.mjs:69). `mergedEnv` is `{...loadDotEnv(), ...process.env, ...}`. | In `verify.mjs`, build the test env without `loadDotEnv()` (keep `process.env` + `demoEnv`), or always apply `demoEnv` to every check step. Also consider passing `.env` keys only to the backend service in `startApp`. |
| 6 | minor | verified | .claude/skills/integrate-api/http-client-patterns.md:17, 103-110, ~200 | The reference client calls `r.json()` with no limit on response size. It describes `httpx.Timeout(10.0, connect=5.0)` as "10 s overall per request", but in httpx it is a per-operation timeout, so a slow-drip response can run much longer. `_check` compares scheme and host but not port. | Searched the file for `size`, `max_bytes`, `content-length` and `aiter_bytes`: none found. Line 128 compares only `scheme` and `host`. | Stream the response with `client.stream(...)` and stop after a `max_bytes` cap (for example 5 MB), raising `BadData`. Wrap each attempt in `asyncio.timeout(15)` for a real overall limit. Add `url.port != self._base.port` to `_check`. Add size limits to the table and to SKILL.md step 4. |
| 7 | minor | verified | .github/workflows/verify.yml:19-37 | Third-party actions are pinned to major-version tags (`@v5`, `@v4`), not commit SHAs. This matters once the repo is public and forks open pull requests. Risk is low because `permissions: contents: read` is set and no secrets are used. | Read the workflow file. | Pin `actions/checkout`, `setup-node`, `setup-python` and `upload-artifact` to full commit SHAs with a version comment, and record this in prepare-deploy/ci.md. |
| 8 | minor | suspected | scripts/lib.mjs:460-468 | The `copyTree` skip list used by create-app and the verify scaffold copy does not exclude `.env`, `.env.*` or `*.pem`. A stray local `scaffold/.env` would be copied into `app/`. It stays git-ignored, so it would not be committed. | Read the code: `COPY_SKIP` has no `.env` entry. To confirm: put an ignored dummy file at `scaffold/.env` in a scratch clone and run `npm run create-app -- --dry-run` (not done, to avoid writing files). | Add `.env`, and a check for files whose name starts with `.env.` other than `.env.example`, to the copy filter. |

**Confirmed OK (no finding):**
- `.env`, `.env.*` (except `.env.example`), `*.pem`, `*.key`, `.venv/`, `node_modules/`, `.cache/`, `.logs/` and `app-starter.zip` are in `.gitignore`.
- `.clineignore` mirrors these and says it is not a security boundary.
- Root `.env.example` contains only commented, non-secret settings.
- The launchers bind uvicorn and Next.js to `127.0.0.1` (app-tasks.mjs:118, 123-124).
- The browser only fetches `/api/health`, and Next.js rewrites `/api/*` to `BACKEND_URL`.
- The scaffold has no CORS, no debug endpoints, no `dangerouslySetInnerHTML` and no `0.0.0.0`.
- Dependencies are pinned exactly (`save-exact`, `requirements.lock`).
- CI uses no secrets and has read-only permissions.
- The security guidance is sound: user-supplied keys are used for one request only, URLs come from an allowlist, redirects are re-checked, CORS is limited to named origins, and there is no `NEXT_PUBLIC_` key.

**Not checked:**
- The untracked `runs/bootstrap/B13…B15b` folders were only scanned for emails and tokens: none found.
- Whether Claude Code applies `Edit(...)` deny rules to the `Write` tool, and whether deny rules apply in an untrusted workspace (the stderr logs show allow rules were ignored there). Both need a live check.
- The full `npm run verify` (production build and browser test) was not run. `--quick` was enough for a security review in template mode.
- Account, payment and permission rules don't apply: there is no app and no `acceptance.md`.

## Handoff
Changes: none. This was a read-only review. `npm run verify -- --quick` wrote only git-ignored output to `.logs/` and `.cache/`.
Verification evidence: `npm run verify -- --quick` exited 0. The `git ls-files`, `git grep` and `git log -p --all` secret and email searches found no secrets, no tracked `.env` and no forbidden files. `git status` shows only the 3 untracked `runs/` folders.
Remaining findings: Major: your personal email is in all 10 commits' metadata (1), and the `.env` deny rules are weak while steps run in bypass mode (2). Minor: your username in tracked `stderr.log` files and `PROGRESS.md` (3), gaps in the redaction list (4), verify passing the root `.env` into tests (5), no response size cap in the client guide (6), actions not pinned to SHAs (7), the copy filter not skipping `.env` (8).
Next action: You decide on finding 1 (noreply address or history rewrite) and finding 2 (hardening the deny rules) before tagging `template-v1`. The main session then fixes 3–8.
<!-- VERBATIM:END -->
