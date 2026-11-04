# AI usage

How AI tools were used in this project. The assistant adds entries as the work happens; the owner (student, team or
instructor) reviews them and completes the summary before hand-in.

## Summary (complete before hand-in)

- **Tools:** <e.g. Claude Code (model shown by `/model`), Cline with <model>, any chat assistant>
- **What AI did:** <code, tests, debugging, design proposals, documents>
- **What we decided ourselves:** <product scope, stack choice, acceptance criteria, ...>
- **How we checked AI output:** <tests, `npm run verify`, reviewer agents, hand checks of numbers, trying the app>
- **One example where the AI was wrong or misleading, and how we caught it:** <...>

## Log

| Date | Who asked | What the AI contributed | How it was checked | Accepted / changed / rejected |
|---|---|---|---|---|
| 2026-11-03 | owner (instructor) | Claude Code (Opus 5.5) built the App Creator toolkit (rules, skills, agents, launchers, scaffold, docs) via recorded steps in `runs/` ([index](runs/INDEX.md)) | toolkit checks (`npm run check-toolkit`, `npm run verify`) and reviews, per step record | accepted or changed per step, as recorded in `runs/` |
| 2026-11-03 | owner (instructor) | B16: Claude Code (Opus 5.5) repaired the B15a/B15b review findings: verify and demo no longer pass the root `.env` to child processes; dispatcher error/timeout handling, wider redaction (credentials, home paths) with counts and a redacted-text hash in RESULT.json, refusal to send prompts containing credentials; PowerShell/cmd hints; client guide size cap, overall timeout and port check; CI actions pinned to SHAs. Caught its own mistakes along the way: a home-path pattern that would have rewritten a quoted regex, and over-long lines in the guide code | throwaway tests under `.cache/` (redaction, dispatcher failure/timeout/success paths with a fake `claude`, launcher helpers), the guide's 11 example tests + ruff, `npm run check-toolkit`, full `npm run verify` exit 0 | pending owner review |
| 2026-11-04 | owner (instructor) | M1: Claude Code (Opus 5.5) built the SEC Analytics foundation through recorded steps, then finished it in the main session at the owner's request. Mistakes caught: the assistant reverted the owner's `/permissions` edits twice; a first diagnosis of a browser hang (cold start) was wrong; a test passed while the backend-down message was visible only to screen readers | pytest, Vitest, Playwright, known answers quoted by hand from the fixtures, a separate fixture cross-check, screenshots; review in the same session, not independent | accepted, with the corrections listed |
