---
name: product-interview
description: Use when starting a new app, when the app's product.md is missing or not agreed, or when the owner wants to change who the product is for, what the MVP includes or which stack it uses. Also when a written brief (delegated mode) must answer the interview.
---

# Product interview and project setup

Turn a rough idea into four short, agreed documents and a running walking skeleton, before any feature code is
written.

**Paths.** `<docs>`, `<frontend>` and `<backend>` mean `app.docsDir`, `app.frontendDir` and `app.backendDir` in
`app-creator.config.json`. After `npm run create-app` they are `app/docs`, `app/frontend` and `app/backend`.
If `"app"` is still `null`, no app exists yet (template mode): step 5 creates it. Conventions, root commands and
approval rules: [docs/TOOLKIT.md](../../../docs/TOOLKIT.md).

## Inputs

- The owner's idea, in their own words. In **delegated mode** the brief replaces the conversation (see below).
- Existing documents, if any: `<docs>/product.md`, `architecture.md`, `acceptance.md`, `plan.md`, and the
  decisions file. **Read them first.** Never ask a question they already answer; confirm it in one line instead.
- [requirements-and-acceptance.md](requirements-and-acceptance.md): how to write MVP features, exclusions,
  checkable acceptance criteria and known-answer calculations. Use it in steps 1 and 3.
- [stacks.md](stacks.md): the standard stack, when to deviate, the root commands and how setup finds Python.
- [charts-and-data-display.md](../design-interface/charts-and-data-display.md): which summary cards, charts and
  tables to propose.
- The templates: [product](templates/product.md), [architecture](templates/architecture.md),
  [acceptance](templates/acceptance.md), [plan](templates/plan.md), and for delegated mode
  [decisions](templates/decisions.md).

## Actions

### 1. Interview: a few questions at a time

Ask **at most three questions per message**, in plain language, and wait for the answers. Offer examples or a
suggested answer when the owner seems unsure. Cover these rounds, skipping anything already answered:

1. **Customers and problem.** Who exactly uses it? What painful task does it replace today? How will you know
   it helped (an observable result)?
2. **Main user journey.** Walk through one visit, from opening the app to getting the result. What does the
   user enter, and what do they take away?
3. **What users see and do.** For the main screens: the first thing the user should see (a key number, a list, a
   form?); whether they expect *a table* or *a dashboard with summary cards and charts* (offer this choice with a
   one-line sketch of each); which interactions matter (search, choose an item, change a period, filter,
   compare, download); any visual reference (a site or app whose look they like, described in words or a
   screenshot added to `<docs>`); dark or light theme; will it be used on a phone?
4. **MVP features and exclusions.** The three to five features without which the product is useless. Then what is
   explicitly *not* in the MVP.
5. **Data and calculations.** Where the data comes from (files, uploads, a public API, manual entry), how fresh it
   must be, whether it must work offline for a demo, and which numbers the app computes. For each important
   number: its formula, units, and one example with a known answer.
6. **Accounts, saved data, uploads, payments.** Do users sign in? Do they see only their own data? Is anything
   saved between visits? Do users upload files? Does anyone pay, and for what?
7. **The team and constraints.** Programming experience, hours until the deadline, budget (zero is a valid
   answer), whether it must be online for others or only run on a laptop for a demo, and any course or client
   rules (data terms, AI policy).

If the owner answers several rounds at once, move on. Stop asking once you can fill the templates.

**When the product shows numbers or a dashboard is wanted,** propose the visuals in one short list before the
documents: the summary cards (value, unit, period, comparison), each chart (the question it answers, chart type,
series, units, periods, how gaps and negatives are shown), and the tables. Use
[charts-and-data-display.md](../design-interface/charts-and-data-display.md). Ask the owner to agree, change or
drop each item. Charts are optional: a table-only product is fine. Do not list charts under "not in the MVP"
unless the owner chose that.

### 2. Recommend a stack

Read [stacks.md](stacks.md). The default is the standard stack, because the root commands (`npm run setup`,
`dev`, `verify`, `demo`) support it. Recommend it unless the product clearly needs something else; name one
alternative and explain the tradeoff in plain language. Say which capabilities are needed now (storage,
accounts, payments, background jobs) and which are deliberately left out. Architecture detail (parts, API,
storage, errors) is decided with `plan-architecture` in step 3.

### 3. Write the four documents (drafts)

Fill the templates into `<docs>/product.md`, `architecture.md`, `acceptance.md` and `plan.md`. Keep each one
short (one to two screens). Mark anything not confirmed as `[to confirm]`. Follow
[requirements-and-acceptance.md](requirements-and-acceptance.md):

- every MVP feature has an id (`F1`), a reason, and at least one acceptance criterion;
- every acceptance criterion is Given / When / Then with a concrete input and a visible or testable result;
- every important calculation has a formula, units, an example with **known answer and written hand working**,
  and the edge cases (missing, zero, negative, not comparable);
- the plan is a list of small slices; slice 1 is always the **walking skeleton** (the app starts, shows one page,
  one test runs, `npm run verify` passes).

For `architecture.md`, use `plan-architecture` (parts and boundaries, API, storage, errors, settings).

### 4. Get agreement

Show a summary: the user journey, the screens and agreed visuals, the MVP features and exclusions, the stack and
why, and the first three slices. Ask the owner to agree or change it. **Do not create application code before
scope and architecture are agreed.** Record the agreement (date, what was agreed, by whom) in the decision log of
`<docs>/architecture.md`, and set `Status: agreed on <date>` in `product.md` and `architecture.md`.

### 5. Set up the project (after agreement)

1. If this folder is not a git repository, ask to run `git init` and commit the starter files
   (`chore: start from App Creator`).
2. From the repository root: `npm ci` (once), then `npm run create-app -- --name "<App name>"` (add
   `--dir <path>` for another folder; `-- --dry-run` shows what it would do). It copies `scaffold/` and sets
   `app-creator.config.json`. It refuses to overwrite an existing folder.
3. Move the drafted documents into the new `<docs>` folder if you wrote them elsewhere.
4. `npm run setup`. It checks Node, finds a supported Python (see [stacks.md](stacks.md)), creates
   `<backend>/.venv`, installs the locked dependencies and the project-local Playwright browser. If it picks the
   wrong Python, the owner sets `APP_PYTHON` (stacks.md shows how). Never install into a base Anaconda,
   system or global Python.
5. **Settings:** add every new setting name to the root `.env.example` with a placeholder or a safe development
   value, never a real secret. Tests and `npm run demo` must work without any `.env`. The owner creates `.env`
   themselves (`cp .env.example .env`, Windows `copy .env.example .env`); you never create, read or edit it.
6. `--name` already set `APP_NAME` in `<backend>/app/main.py` and `<frontend>/lib/site.ts`; check both. Fill the
   "This project" section of `AGENTS.md` with the stack and the four root commands.
7. Run `npm run verify` and `npm run dev`; open http://127.0.0.1:3000 and check the page shows **Backend status:
   OK**. Look at the Playwright screenshots in `<frontend>/test-results/`.
8. Add a first entry to `AI-USAGE.md`. Propose a checkpoint commit (`chore: walking skeleton for <App name>`); in
   delegated mode commit it if the delegation covers commits (TOOLKIT §4).

### Delegated mode (the owner wrote a brief instead of being interviewed)

Use it only when the owner has **explicitly** delegated routine product decisions in a written brief (for
example `GOAL.md`). Otherwise use the interactive interview above.

1. **Write the questions.** Go through the seven rounds. For every point the brief or the decisions file does not
   already settle, write one numbered question, phrased so it can be answered in a sentence. Do not ask what is
   already decided.
2. **Get the answers from `delegated-product-owner`.** Send it the questions, the path of the brief and the path
   of the decisions file. In Claude Code it runs as a read-only subagent; without subagents (Cline), read
   `.claude/agents/delegated-product-owner.md` and answer as it instructs, in a separate, clearly marked step.
   You never answer your own questions silently.
3. **Record them** in the decisions file (default `docs/PRODUCT-DECISIONS.md`, or the path the brief names),
   using [templates/decisions.md](templates/decisions.md): each question verbatim, the **exact answer**, and its
   basis:
   - **Explicit**: the brief says it (quote the shortest phrase and the section, e.g. `GOAL.md §5`);
   - **Delegated assumption**: routine and reversible; the one-line reason;
   - **Not delegable**: scope, money, publication, personal data, secrets or a contradiction in the brief. Record
     it as a blocker with what can continue meanwhile; never decide it yourself.
4. **Fill the four documents** from the brief and the recorded answers. In each document, mark assumptions with
   `(assumption D<n>)` pointing to the decisions-file row, so a reader can see what the owner did not say.
5. **Agreement:** the recorded delegation counts as agreement for routine items. Write in the decision log of
   `architecture.md`: date, "agreed under delegation (`<brief>` §n)", and the list of blockers still open. Then
   continue with step 5 above. The `project-orchestrator` gates the next steps (`orchestrate-steps`).

## Outputs

`<docs>/product.md` (including agreed screens and visuals), `architecture.md`, `acceptance.md`, `plan.md` (all
agreed), the decisions file in delegated mode, the walking skeleton created by `npm run create-app` and set up by
`npm run setup`, the "This project" section of `AGENTS.md`, a first `AI-USAGE.md` entry, a proposed (or, under
delegation, made) checkpoint commit.

## Verification

- Every MVP feature has at least one acceptance criterion; every criterion has a concrete input and an
  observable result (the checklist in [requirements-and-acceptance.md](requirements-and-acceptance.md)).
- Each important calculation has a formula, units, a known-answer example with written hand working, and its
  missing/zero/negative cases in `<docs>/acceptance.md`.
- Each main screen has its content, interactions, states and visuals (or "table only") in `product.md`.
- Delegated mode: every question in the decisions file has an answer and a basis; no "Not delegable" item was
  decided; every `(assumption D<n>)` points to an existing row.
- `npm run verify` exits 0 on the skeleton, and the page was seen to show "Backend status: OK" (or the gap is
  stated with the exact error).

## Stop when

- The documents are agreed and the skeleton passes `npm run verify`: hand over to `build-feature` for slice 2.
- **Stop and ask** if requirements contradict each other (for example "no budget" and "a paid data feed"), if
  the idea needs something the stack cannot do, or if a requirement involves real customers' money or personal
  data that the team cannot protect yet. Explain the problem and offer a smaller option.
- `npm run setup` fails twice after two different fixes (wrong Python, network, proxy): stop, report the exact
  message and the fixes tried, and use `debug-issue`.
- In delegated mode, a blocker that stops the walking skeleton itself: record it and report; continue only with
  work that does not depend on it.

## Common mistakes

- Asking ten questions at once, or re-asking what `product.md` or the decisions file already says.
- Acceptance criteria such as "the app is user-friendly" or "charts look good" (not checkable).
- A calculation example whose expected value was copied from the app's own output.
- Never asking what the screens should look like, then building a plain table when the owner expected a
  dashboard; or adding charts nobody asked for.
- Choosing accounts, a database or background jobs "for later" when the MVP does not need them.
- Running a global `pip install` or `npm install -g`, or creating the venv by hand with whatever `python` is first
  on the PATH, instead of `npm run setup`.
- In delegated mode: answering your own questions, recording a paraphrase instead of the exact answer, or
  treating "the brief does not forbid it" as permission for new scope.
- Writing feature code during the interview.

## Example

Owner: "A tool for our running club to log weekly distances and see who improved."

- Round 1 answer: "Club coach, 30 members; today a shared spreadsheet that breaks every month."
- MVP: F1 enter a run (member, date, km), F2 weekly totals table per member, F3 "most improved" card (this week
  vs last week). Not in the MVP: accounts (the coach enters all runs), mobile app, Strava import.
- Criterion: *Given* runs of 5 km and 7 km for Ana in week 12 and 10 km in week 11, *When* the coach opens the
  weekly table for week 12, *Then* Ana's row shows `12.0 km` and a change of `+2.0 km`.
- Calculation CALC1, weekly total: 5 + 7 = 12 km; change 12 − 10 = +2 km. Missing week 11 → change shown as
  "n/a (no runs last week)", never `+12.0`.
- Stack: standard (Next.js + FastAPI), SQLite because runs are saved between visits (`manage-data`).
