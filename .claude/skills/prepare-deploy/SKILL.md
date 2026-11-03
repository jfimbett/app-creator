---
name: prepare-deploy
description: Use when the app must run somewhere other than the owner's laptop, be shared with users or a jury, be handed over or submitted, needs CI, Docker or a security pass before release, or when someone else cannot install or run it from the README.
---

# Prepare deployment and handoff

Make the app runnable by someone else from the repository alone, checked automatically, and ready for a host the
owner chooses. This skill **prepares**; it does not deploy, push, create accounts or buy anything. Publication is
never a routine decision, not even in delegated mode (`docs/TOOLKIT.md` §4): the owner performs the deployment.

Paths: `<backend>`, `<frontend>`, `<docs>` come from `app-creator.config.json`. Guides:
[ci.md](ci.md) (GitHub Actions), [docker.md](docker.md) (optional containers),
[env-and-secrets.md](env-and-secrets.md) (settings, rotation, leaked keys),
[security-checklist.md](security-checklist.md) (headers, CORS, binding, audit, logging).

## Inputs

- `<docs>/architecture.md` (stack, services, settings), `<docs>/product.md` (who must reach it), `<docs>/plan.md`
  (known problems), the root `README.md` and the app's README.
- The hosting option the owner wants, or none yet. If a host is chosen, read its official documentation for the
  stack (build and start commands, environment variables, database, free-tier limits, where logs go).

## Actions

1. **Readiness check** (report each item as ok / missing):
   - pinned dependencies: `<frontend>/package-lock.json` and `<backend>/requirements.lock`; a fresh `npm ci && npm
     run setup` installs them;
   - the root contract works: `npm run setup`, `npm run dev`, `npm run demo` (offline, no keys), `npm run verify`;
   - every setting listed in the root `.env.example` with placeholders; no secret in the code or the git history
     ([env-and-secrets.md](env-and-secrets.md), "Search for leaked secrets"); if one was ever committed, it must be
     revoked and replaced, not only deleted;
   - the security checklist ([security-checklist.md](security-checklist.md)): debug off by default, a
     development-only secret accepted only with debug on **and** a local host (test both refusals), CORS and
     allowed hosts restricted, security headers, secure cookies if accounts exist, backend bound to 127.0.0.1
     unless the host requires otherwise, dependency audit reviewed;
   - errors are logged without secrets or personal data; users see a friendly error page;
   - database migrations run as a documented step (or automatically at start-up); no database or cache files
     committed;
   - test-mode payment keys only (course projects);
   - `npm run verify` passes; the review blockers are closed (`review-changes`).
2. **Fresh-copy test:** clone the repository into a temporary folder (`git clone <repo> /tmp/fresh-copy`, or copy
   it without `node_modules`, `.venv`, `.cache` and `.env`), then follow the README exactly: `npm ci`, `npm run
   setup`, the owner's `cp .env.example .env` step if live mode needs it, `npm run verify`, `npm run demo`. Fix the
   README or the setup where it fails.
3. **CI** (if the repository is on GitHub or the owner asks): add `.github/workflows/verify.yml` from
   [ci.md](ci.md) so every push and pull request runs `npm ci && npm run setup && npm run verify` offline, with no
   secrets. Proposing the file is local work; the first run happens only when the owner pushes.
4. **Host configuration** (only if the owner chose a host): add the files the host's documentation requires (a
   start command, or a container file from [docker.md](docker.md) when the host runs containers), list the
   environment variables the owner must set in the host's dashboard, and the migration step. Do not run any
   deployment command; give the owner the exact steps.
5. **Handoff documents:**
   - README: what it does, who it is for, prerequisites (Node, Python 3.10–3.13), install (`npm ci`, `npm run
     setup`), settings (names only), run (`npm run dev`, `npm run demo`), test (`npm run verify`), data sources and
     their terms, known limitations;
   - `<docs>/plan.md`: final status of each slice and the open problems;
   - `<docs>/acceptance.md`: statuses current;
   - `AI-USAGE.md`: complete (tools, how they were used, an example where the AI was wrong and how it was caught,
     what was checked by hand).
6. **Demo checklist** for the presentation: the main journey step by step, `npm run demo` as the offline fallback,
   the test data or test accounts to use, and screenshots from `<frontend>/test-results/` as a last resort.

## Outputs

Readiness report, fixes to setup and README, CI workflow (if wanted), host configuration files and steps (if
chosen), updated handoff documents, demo checklist, a change report.

## Verification

- The fresh-copy test passed (state the folder used, the commands run and their exit codes), or the failures are
  listed.
- No secret found in the files or history (state the search done).
- CI: the workflow file passes a YAML parse locally; its first real run is reported as **not verified** until the
  owner pushes and shares the result.
- After the owner deploys, the main journey works at the public address: the owner confirms, or it is reported as
  not verified.

## Stop when

- The readiness report has no `missing` items, or the remaining ones are listed with the reason.
- **Stop and ask** before anything that costs money, creates accounts, pushes or publishes, exposes personal data
  to the internet, or uses live payment keys.

## Common mistakes

- "It works on my laptop" without a fresh-copy test.
- Setting secrets in a committed file "for the demo", or in a `NEXT_PUBLIC_` variable.
- Deploying with debug mode on, which can show code and settings to visitors.
- CI that needs secrets or the live network to pass.
- Making Docker a prerequisite for running the app.

## Example

Before a jury demo: readiness report shows `missing` for "CORS allows `*`" and "README lacks `npm run demo`".
Fix both (CORS limited to the frontend origin from a setting, test added; README updated). Fresh copy in
`/tmp/fresh-copy`: `npm ci` exit 0, `npm run setup` exit 0, `npm run verify` exit 0, `npm run demo` serves the
fixture journey. Add `.github/workflows/verify.yml`; tell the owner it runs after they push. Demo checklist:
open the home page, choose an item, show the chart, then show the error state by stopping the backend. Report:
"Deployment not done (owner's step); no host chosen; CI first run not verified."
