# Milestone and prompt index

Each milestone was built from its brief **and** from later instructions. **A brief alone is not the full set of instructions actually used**: read its follow-ups and its `runs/` records too.

How to read the records:

- **Captured response:** the agent's final message, saved unchanged except for explicit `[REDACTED:<kind>]` markers.
- **Marker (gap):** the step ran in the top-level session, so its final message exists only in the session transcript. The file says so. These messages are not reconstructed, and the running updates between tool calls are not recorded either.

## Template (`template-v1`, branch `template`)

The toolkit: rules, skills, agents, launchers, scaffold and the five milestone briefs. Records: [`runs/bootstrap/`](../runs/bootstrap), listed in [the steps index](../runs/INDEX.md).

## M1 Foundation (tag `m1`, branch `milestone/01-foundation`)

**What changed.** Dark shell, keyboard search over three demo companies, company profile, and annual revenue and net income from authentic recorded SEC data, with source labels.

- Brief: [01-foundation/PROMPT.md](01-foundation/PROMPT.md)
- Follow-ups: [01-foundation/FOLLOWUPS.md](01-foundation/FOLLOWUPS.md)
- Results and how to inspect: [01-foundation/README.md](01-foundation/README.md)

| Step (prompt) | What it did | Response | Result |
|---|---|---|---|
| [m1-01-plan](../runs/m1/m1-01-plan/PROMPT.md) | project plan for M1, 15 steps | [response](../runs/m1/m1-01-plan/RESPONSE.md) | [result](../runs/m1/m1-01-plan/RESULT.json) |
| [m1-02-skeleton](../runs/m1/m1-02-skeleton/PROMPT.md) | app skeleton | [response](../runs/m1/m1-02-skeleton/RESPONSE.md) | [result](../runs/m1/m1-02-skeleton/RESULT.json) |
| [m1-03-assistant-files](../runs/m1/m1-03-assistant-files/PROMPT.md) | rules and skill for this example | [response](../runs/m1/m1-03-assistant-files/RESPONSE.md) | [result](../runs/m1/m1-03-assistant-files/RESULT.json) |
| [m1-04-sec-client](../runs/m1/m1-04-sec-client/PROMPT.md) | SEC client | [response](../runs/m1/m1-04-sec-client/RESPONSE.md) | [result](../runs/m1/m1-04-sec-client/RESULT.json) |
| [m1-05-capture-fixtures](../runs/m1/m1-05-capture-fixtures/PROMPT.md) | authentic recorded SEC data | [response](../runs/m1/m1-05-capture-fixtures/RESPONSE.md) | [result](../runs/m1/m1-05-capture-fixtures/RESULT.json) |
| [m1-06-backend-api](../runs/m1/m1-06-backend-api/PROMPT.md) | backend API | [response](../runs/m1/m1-06-backend-api/RESPONSE.md) | [result](../runs/m1/m1-06-backend-api/RESULT.json) |
| [m1-07-periods](../runs/m1/m1-07-periods/PROMPT.md) | annual period selection | [response](../runs/m1/m1-07-periods/RESPONSE.md) | [result](../runs/m1/m1-07-periods/RESULT.json) |
| [m1-07b-overview](../runs/m1/m1-07b-overview/PROMPT.md) | overview data | [response](../runs/m1/m1-07b-overview/RESPONSE.md) | [result](../runs/m1/m1-07b-overview/RESULT.json) |
| [m1-08-design-shell](../runs/m1/m1-08-design-shell/PROMPT.md) | dark shell and design tokens | [response](../runs/m1/m1-08-design-shell/RESPONSE.md) | [result](../runs/m1/m1-08-design-shell/RESULT.json) |
| [m1-09-frontend-lib](../runs/m1/m1-09-frontend-lib/PROMPT.md) | frontend API client and helpers | [response](../runs/m1/m1-09-frontend-lib/RESPONSE.md) | [result](../runs/m1/m1-09-frontend-lib/RESULT.json) |
| [m1-10-screens](../runs/m1/m1-10-screens/PROMPT.md) | screens | [response](../runs/m1/m1-10-screens/RESPONSE.md) | [result](../runs/m1/m1-10-screens/RESULT.json) |
| [m1-11-e2e](../runs/m1/m1-11-e2e/PROMPT.md) | browser tests; **failed**: 60-minute timeout, no message, no spec written, cause not diagnosed | [record of the failure](../runs/m1/m1-11-e2e/RESPONSE.md) | [result](../runs/m1/m1-11-e2e/RESULT.json) |
| [R01-classroom-demo](../runs/recovery/R01-classroom-demo/PROMPT.md) | classroom recovery, top-level session | **gap:** [marker](../runs/recovery/R01-classroom-demo/RESPONSE.md) | [result](../runs/recovery/R01-classroom-demo/RESULT.json) |
| [m1-16-complete-m1-main-session](../runs/m1/m1-16-complete-m1-main-session/PROMPT.md) | finished M1 in the top-level session | **gap:** [marker](../runs/m1/m1-16-complete-m1-main-session/RESPONSE.md) | [result](../runs/m1/m1-16-complete-m1-main-session/RESULT.json) |

Planned steps m1-11 to m1-15 were replaced by m1-16 at the instructor's request, so m1-12 to m1-15 have no records. The planned independent reviews did not run.

## M2 Financial intelligence (tag `m2`, branch `milestone/02-financial-intelligence`)

**What changed.** Backend SEC adapters with a cache and throttling, a Demo/Live selector, live lookup, 5 to 10 years of normalized statement summaries, ratios, a metric explorer, reported or derived labels, and provenance details.

- Brief: [02-financial-intelligence/PROMPT.md](02-financial-intelligence/PROMPT.md)
- Follow-ups: [02-financial-intelligence/FOLLOWUPS.md](02-financial-intelligence/FOLLOWUPS.md)
- Results and how to inspect: [02-financial-intelligence/README.md](02-financial-intelligence/README.md)

| Step (prompt) | What it did | Response | Result |
|---|---|---|---|
| [m2-01-implement-main-session](../runs/m2/m2-01-implement-main-session/PROMPT.md) | built M2 in the top-level session | **gap:** [marker](../runs/m2/m2-01-implement-main-session/RESPONSE.md) | [result](../runs/m2/m2-01-implement-main-session/RESULT.json) |

Evidence in the same folder: `verify-clean-worktree.log`, `live-evidence.log`, `review-checks.log`. No independent review ran; M2 used adversarial live checks and read-only checks.

## M3 Filing intelligence: tag `m3`, branch `milestone/03-filing-intelligence`

Partly built on 2026-11-04 (m3-02), stopped by the classroom freeze (m3-03), then finished, reviewed and verified on 2026-11-09 (m3-04).
Changes: a Filings tab with the latest 10-K and 10-Q, a 10-year history with amendment labels, a sanitized reader with detected sections,
text search and sec.gov links, and recorded documents for offline use. [Milestone README](03-filing-intelligence/README.md).

- Brief: [03-filing-intelligence/PROMPT.md](03-filing-intelligence/PROMPT.md)
- Follow-ups: [03-filing-intelligence/FOLLOWUPS.md](03-filing-intelligence/FOLLOWUPS.md)

| Step (prompt) | What it did | Response | Result |
|---|---|---|---|
| [m3-01-implement-main-session](../runs/m3/m3-01-implement-main-session/PROMPT.md) | earlier instruction, saved but never executed | none | none |
| [m3-02-implement-main-session](../runs/m3/m3-02-implement-main-session/PROMPT.md) | partial implementation; **not verified** | **gap:** [marker](../runs/m3/m3-02-implement-main-session/RESPONSE.md) | [result](../runs/m3/m3-02-implement-main-session/RESULT.json) |
| [m3-03-classroom-freeze](../runs/m3/m3-03-classroom-freeze/PROMPT.md) | stopped M3; chose M2 for class; published this repository | **gap:** [marker](../runs/m3/m3-03-classroom-freeze/RESPONSE.md) | none |
| [m3-04-finish-main-session](../runs/m3/m3-04-finish-main-session/PROMPT.md) | finished M3: Windows test fix, browser journeys, screen fixes, live check, independent security and test reviews and their fixes, gate | **gap:** [marker](../runs/m3/m3-04-finish-main-session/RESPONSE.md) | [result](../runs/m3/m3-04-finish-main-session/RESULT.json) |

## M4 Comparative analysis: tag `m4`, branch `milestone/04-comparative-analysis`

Built, reviewed and verified on 2026-11-09 in one main session (m4-01). Changes: the Compare screen and `/api/compare`,
`/api/compare.csv` with indexing, fiscal-year and currency warnings, charts and CSV export. [Milestone README](04-comparative-analysis/README.md).

- Brief: [04-comparative-analysis/PROMPT.md](04-comparative-analysis/PROMPT.md)
- Follow-ups: [04-comparative-analysis/FOLLOWUPS.md](04-comparative-analysis/FOLLOWUPS.md)

| Step (prompt) | What it did | Response | Result |
|---|---|---|---|
| [m4-01-implement-main-session](../runs/m4/m4-01-implement-main-session/PROMPT.md) | built M4, live check, independent security and test reviews and their fixes, gate | **gap:** [marker](../runs/m4/m4-01-implement-main-session/RESPONSE.md) | [result](../runs/m4/m4-01-implement-main-session/RESULT.json) |

## M5 AI financial analyst: tag `m5`, branch `milestone/05-ai-financial-analyst`

Built, reviewed and verified on 2026-11-09 (m5-01) with a mocked AI service; live AI not verified (N1). The frontend was built
by a frontend-engineer subagent briefed in the same session (its brief and final report are in the step record's notes).
Changes: the OpenRouter boundary, grounded chat with checked citations, the Analyst panel and AI settings.
[Milestone README](05-ai-financial-analyst/README.md).

- Brief: [05-ai-financial-analyst/PROMPT.md](05-ai-financial-analyst/PROMPT.md)
- Follow-ups: [05-ai-financial-analyst/FOLLOWUPS.md](05-ai-financial-analyst/FOLLOWUPS.md)

| Step (prompt) | What it did | Response | Result |
|---|---|---|---|
| [m5-01-implement-main-session](../runs/m5/m5-01-implement-main-session/PROMPT.md) | built M5 (backend in the session, frontend by a subagent), reviews and fixes, gate | **gap:** [marker](../runs/m5/m5-01-implement-main-session/RESPONSE.md) | [result](../runs/m5/m5-01-implement-main-session/RESULT.json) |

All five milestones now have tags.
