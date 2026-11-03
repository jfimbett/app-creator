# RESPONSE — B12-decisions-and-plan

- From: product-architect → to: owner (top-level Claude Code session)
- Captured by: scripts/dispatch-step.mjs from the `result` field of `claude -p --output-format json`
- Session id: ca88387e-1f0d-427c-b7b1-98f2c56f921b (local Claude Code transcript; not committed)
- Finished: 2026-11-03T17:49:25.264Z; exit code 0; status completed
- Redaction: only explicit [REDACTED:<kind>] markers were inserted; otherwise verbatim.

<!-- VERBATIM:BEGIN -->
I wrote the six planning files for the SEC Analytics example: the decisions record, the four planning documents and the milestones README. All 44 questions are recorded, and `npm run check-toolkit` passes. Nothing is committed.

**Decisions file (`docs/PRODUCT-DECISIONS.md`).** A script copied each question and the delegate's answer word for word from the B10 and B11 records, so nothing was retyped. Each row also gives the basis class and its source in GOAL.md or a recorded decision. Three items are not delegable:
- **N1:** the paid live check of the AI analyst. It needs money and a key, and no test key exists, so only the mocked version is verified.
- **N2:** the SEC contact used for live requests. It is personal data and stays only in your local environment.
- **N3:** publishing the repository. This interview does not cover it; GOAL.md already covers it.

**The four planning documents** (in `milestones/`) all say "agreed on 2026-11-03 (delegated…)":
- **Product:** the five milestones as features, screens, labels for demo, live, cached and missing data, and what is out of scope.
- **Architecture:** the frontend, backend and fixture folders, and the API endpoints for each milestone with their request and response shapes. It also has the SEC fetch rules (allowed hosts and paths, cache, 1 request per second), how annual periods and restatements are chosen, and how the user's OpenRouter key passes through the backend without being stored.
- **Acceptance:** criteria grouped per milestone (M1-AC1 … M5-AC9) and the edge cases you asked for. The worked calculations CALC1–CALC11 use round, made-up "Example Co" numbers, labelled as not real SEC values.
- **Plan:** each milestone split into slices, each with its criteria, owning agent, skills, and the files it may and may not touch.

**`milestones/README.md`** explains the five cumulative releases, the tag chain `template-v1` → `m1` → … → `m5`, and that a finished checkout is for inspecting, not for re-running its own prompt.

Things you should know:
- **Unconfirmed guesses about SEC data:** the SEC field names behind each metric, the fiscal-year labels and each company's year-end date are marked `[verify against fixtures]`. They must be checked against the real SEC data captured in M1 before the M2 calculation tests are finalized.
- **No links to the milestone folders yet:** the README names them as plain paths. Links would fail the check until the next step creates the `PROMPT.md` files.
- **Delegate's Node version concern is stale:** PROGRESS.md D5b already ends at 22.13, so there is no conflict. I noted this in the decisions file and did not edit PROGRESS.md.
- **Four companies only in tests and live mode:** the offline demo has three companies, so the four-company comparison can only be shown in tests and in live mode.

## Handoff
Changes: created `docs/PRODUCT-DECISIONS.md`, `milestones/product.md`, `milestones/architecture.md`, `milestones/acceptance.md`, `milestones/plan.md`, `milestones/README.md`; no other files touched (`git status --short` shows only these plus the pre-existing `runs/bootstrap/B12-decisions-and-plan/`).
Verification evidence: `grep` loop for `| Q1 |`…`| Q44 |` found 0 missing and counted 44 rows. Script check: 0 of the 44 B10 questions and 0 of the 44 B11 answers are missing verbatim from the decisions file. Email-pattern grep over the six files found none. `npm run check-toolkit` exit 0 (34 ok, 3 pre-existing skill warnings, 0 failures; markdown links: 209 relative links in 84 files resolve).
Remaining findings: N1 (paid live AI validation) is blocked with no test key. N2 (SEC contact in the build environment) is open per session. Concept mapping, fiscal-year labels and year-end dates are `[verify against fixtures]`. The stale Node 22.12 note needs no change. The four-company comparison is shown only in tests and live mode.
Next action: B13 writes the five `milestones/0*/PROMPT.md` briefs from these documents, then commit B12's files.
<!-- VERBATIM:END -->
