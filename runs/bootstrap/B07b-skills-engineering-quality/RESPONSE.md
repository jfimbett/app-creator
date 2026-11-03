# RESPONSE — B07b-skills-engineering-quality

- From: docs-writer → to: owner (top-level Claude Code session)
- Captured by: scripts/dispatch-step.mjs from the `result` field of `claude -p --output-format json`
- Session id: d101536d-c024-4fc8-ad87-86c4a7e44b1f (local Claude Code transcript; not committed)
- Finished: 2026-11-03T17:34:32.395Z; exit code 0; status completed
- Redaction: only explicit [REDACTED:<kind>] markers were inserted; otherwise verbatim.

<!-- VERBATIM:BEGIN -->
I've adapted all eight engineering and quality skills. Each `SKILL.md` now has the required frontmatter and sections plus a short example, and I added the 11 guides you listed. One task is unfinished: the session's permissions blocked deleting the two old browser-check files, so they are still in `test-and-check/`.

**What the skills now share**
- **Paths** are written as `<backend>`, `<frontend>` and `<docs>`, taken from `app-creator.config.json`. Setting names go in the root `.env.example`.
- **Commands** run through the root contract (`npm run setup`, `dev`, `demo`, `verify`).
- **Delegated mode** rules from `docs/TOOLKIT.md` §4 are in `review-changes`. Accounts, payments and deployment say they are never routine decisions.
- **Content kept:** independent expected values, missing is not zero, the review stopping rule, the "Without subagents (Cline)" route, and the starter's tone.

**Which example code was actually run** (in throwaway folders outside the repo, with the scaffold's pinned versions):
- **HTTP client** (`http-client-patterns.md`): allowlist, redirect check, retries honouring `Retry-After`, request de-duplication, disk cache, plus a FastAPI route. 8 pytest tests passed (with `respx` mocking the HTTP calls) and ruff was clean with the scaffold's settings.
- **SQLite migrations** (`caching-and-storage.md`): 4 tests passed, including one showing a broken migration changes nothing.
- **Playwright journey** (`playwright-journeys.md`): run against a copy of the scaffold with the project-local browser. 4 passed, and typecheck and lint were clean. I looked at the 390 px and error-state screenshots; the layout fits and the error message is readable.
- **CSRF origin check** (`authn-authz.md`): the first version would have let a look-alike host through; I fixed it to an exact match and tested it.
- **Secret-search command** (`env-and-secrets.md`): the original pattern matched nothing because git's regex doesn't support `\s`. I fixed it and tested it on a fake sample; it finds nothing in the repo's tracked files.

**What is still unrun, and labelled so in the guides:** the sign-in/session code, the payment flow, the CI workflows (YAML parses, but they have not run on GitHub), the Docker files, and the dependency-audit commands. The action versions in `ci.md` are marked for checking before use.

**Things outside my folders that need attention**
- **Old files to delete:** `test-and-check/browser_check.py` and `browser-checks.md` are no longer linked from `SKILL.md`; everything useful from them is now in `playwright-journeys.md`. Remove them with `git rm`.
- **Stale references to the old files** remain in `AGENTS.md`, `START-HERE.md`, `.clineignore`, `product-interview/stacks.md` and `product-interview/templates/architecture.md`.
- **Node version conflict:** the scaffold's `package.json` requires Node ≥ 22.12, but `docs/TOOLKIT.md` §3 says ≥ 20.9. `ci.md` uses Node 22.
- **Warnings:** `check-toolkit` warns that `add-payments` and `review-changes` have no supporting guide. You didn't ask for guides there, so I added none.
- **Leftover folders:** throwaway folders remain in `/tmp` (`b07b-scratch`, `b07b-scaffold`, `b07b-grep`) because deleting needs approval. The temporary servers on ports 8765 and 3765 are stopped.

## Handoff
Changes: Rewritten `SKILL.md` in `.claude/skills/` integrate-api, manage-data, add-accounts, add-payments, test-and-check, debug-issue, review-changes, prepare-deploy. New guides: `integrate-api/http-client-patterns.md`, `manage-data/caching-and-storage.md`, `add-accounts/authn-authz.md`, `test-and-check/playwright-journeys.md`, `test-and-check/performance.md`, `debug-issue/refactoring.md`, `prepare-deploy/{ci,docker,env-and-secrets,security-checklist}.md`. Not deleted (permission denied): `test-and-check/browser_check.py`, `test-and-check/browser-checks.md`.
Verification evidence: `python3 /tmp/b07b-check.py` exit 0 (8/8 skills: name matches folder, descriptions 209–242 chars, all required sections present; 36 relative links resolve). Ruby YAML parse exit 0 (8 frontmatters, 3 YAML blocks). `node scripts/check-toolkit.mjs` exit 0 (32 ok, 3 warnings, 0 failures, 137 links). Example code: pytest 8 passed + 4 passed, ruff clean; Playwright 4 passed, `tsc` and `eslint` exit 0; CSRF check prints `[200, 403, 200, 403, 403]` as expected; secret search fixed and checked on a fake sample.
Remaining findings: the 2 old files to `git rm`; stale references in `AGENTS.md`, `START-HERE.md`, `.clineignore`, `product-interview/stacks.md` and `product-interview/templates/architecture.md`; Node ≥ 22.12 (scaffold) vs ≥ 20.9 (TOOLKIT); unrun: sign-in/session and payment sketches, CI workflows, Docker files, audit commands, action versions; leftover `/tmp/b07b-*` folders.
Next action: Owner runs `git rm` on the two old browser-check files, updates the 5 stale references, then reviews and commits B07b.
<!-- VERBATIM:END -->
