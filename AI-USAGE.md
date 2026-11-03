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
