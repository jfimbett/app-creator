---
name: prepare-deploy
description: Use when the application must run somewhere other than the student's laptop, be shared with users or a jury, be handed over or submitted, or when someone else cannot install or run it from the README.
---

# Prepare deployment and handoff

Make the app runnable by someone else from the repository alone, and ready for a host the student chooses. This
skill prepares; it does not deploy, create accounts or buy anything. The student performs the deployment.

## Inputs

- `docs/architecture.md` (stack, services, settings), `docs/product.md` (who must reach it), `docs/plan.md` (known
  problems).
- The hosting option the student wants, or none yet. If a host is chosen, read its official documentation for the
  stack (build command, start command, environment variables, database, free-tier limits).

## Actions

1. **Readiness check** (report each item as ok / missing):
   - one dependency file with pinned or bounded versions; installs into a fresh environment;
   - a single start command; the app reads its port and host from settings when the host requires it;
   - every setting listed in `app/.env.example`; no secret in the code or the git history (`git log -p` search for
     key-like strings; if one was ever committed, it must be revoked and replaced, not only deleted);
   - debug mode off unless explicitly set; a development-only secret key accepted only with debug on **and** a
     local host, and refused everywhere else (test both refusals); allowed hosts or CORS restricted; secure
     cookies if accounts exist;
   - errors are logged (to the console or the host's logs) without secrets or personal data; users see a friendly
     error page;
   - database migrations run as a documented step; no local database file committed;
   - test-mode payment keys only (course projects);
   - the full test command passes; the review blockers are closed (`review-changes`).
2. **Fresh-copy test:** clone or copy the repository into a temporary folder, follow `app/README.md` exactly
   (new virtual environment, the student's `cp .env.example .env` step, migrations), run the tests, start the
   app and run the browser check if the project has one. Fix the README or the setup where it fails.
3. **Host configuration** (only if the student chose a host): add the files the host's documentation requires
   (for example a start command or a container file), list the environment variables the student must set in the
   host's dashboard, and the migration step. Do not run any deployment command; give the student the exact steps.
4. **Handoff documents:**
   - `app/README.md`: what it does, who it is for, prerequisites, install, settings (names only), run, test, data
     sources and their terms, known limitations;
   - `docs/plan.md`: final status of each slice and the open problems;
   - `docs/acceptance.md`: statuses current;
   - `AI-USAGE.md`: complete (tools, how they were used, an example where the AI was wrong and how it was caught,
     what was checked by hand).
5. **Demo checklist** for the presentation: the main journey step by step, the test data or test accounts to use,
   and a fallback (screenshots or a local run) if the network fails.

## Outputs

Readiness report, fixes to setup and README, host configuration files and steps (if chosen), updated handoff
documents, demo checklist, a change report.

## Verification

- The fresh-copy test passed (state the folder used and the commands run), or the failures are listed.
- No secret found in the files or history (state the search done).
- After the student deploys, the main journey works at the public address: the student confirms, or it is reported
  as not verified.

## Stop when

- The readiness report has no `missing` items, or the remaining ones are listed with the reason.
- **Stop and ask** before anything that costs money, creates accounts, exposes personal data to the internet, or uses
  live payment keys.

## Common mistakes

- "It works on my laptop" without a fresh-copy test.
- Setting secrets in a committed file "for the demo".
- Deploying with debug mode on, which can show code and settings to visitors.
