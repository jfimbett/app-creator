---
name: product-interview
description: Use when starting a new application in this folder, when docs/product.md does not exist yet, or when the student wants to change who the product is for, what the MVP includes, or which stack it uses.
---

# Product interview and project setup

Turn a rough idea into four short, agreed documents and a running skeleton, before any feature code is written.

## Inputs

- The student's idea, in their own words.
- Existing documents, if any: `docs/product.md`, `docs/architecture.md`, `docs/acceptance.md`, `docs/plan.md`.
  **Read them first.** Never ask a question these documents already answer; confirm it in one line instead.
- [stacks.md](stacks.md): the stack options, how to choose, and how to set up the environment.
- [financial-visuals.md](../design-interface/financial-visuals.md): which cards, charts and tables to propose.
- The templates: [product](templates/product.md), [architecture](templates/architecture.md),
  [acceptance](templates/acceptance.md), [plan](templates/plan.md).

## Actions

### 1. Interview: a few questions at a time

Ask **at most three questions per message**, in plain language, and wait for the answers. Offer examples or a
suggested answer when the student seems unsure. Cover these rounds, skipping anything already answered:

1. **Customers and problem.** Who exactly uses it? What painful task does it replace today? How will you know
   it helped?
2. **Main user journey.** Walk through one visit, from opening the app to getting the result. What does the
   user enter, and what do they take away?
3. **What users see and do.** For the main screens: the first thing the user should see (a key number, a list, a
   form?); whether they expect *a table of figures* or *a dashboard with summary cards and charts* (offer this
   choice with a one-line sketch of each); which interactions matter (choose a company, change a period, filter,
   compare, download); and any visual reference (a site, report or app whose look they like, described in
   words or a screenshot they add to `docs/`). Also: will it be used on a phone?
4. **MVP features and exclusions.** The three to five features without which the product is useless. Then what is
   explicitly *not* in the MVP.
5. **Data and calculations.** Where the data comes from (files, uploads, a public API, manual entry), how fresh it
   must be, and which numbers the app computes. For each important number: its formula, units and currency.
6. **Accounts, saved data, uploads, payments.** Do users sign in? Do they see only their own data? Is anything saved
   between visits? Do users upload files? Does anyone pay, and for what?
7. **The team and constraints.** Programming experience, hours available until the deadline, budget (zero is a
   valid answer), whether it must be online for others or only run on a laptop for a demo, and any course or
   client rules.

If the student answers several rounds at once, move on. Stop asking once you can fill the templates.

**When the product shows financial numbers or a dashboard is wanted,** propose the visuals in one short list
before the documents: the summary cards (value, unit, period, comparison), each chart (what question it answers,
chart type, series, units, periods, how gaps and negatives are shown), and the tables. Use
[financial-visuals.md](../design-interface/financial-visuals.md). Ask the student to agree, change or drop each
item. Charts are optional: a table-only product is fine when the student prefers it. Do not list charts under
"not in the MVP" unless the student chose that.

### 2. Recommend a stack

Read [stacks.md](stacks.md). Recommend **one** path and stack, and name one alternative. Explain the tradeoffs in plain
language (what is easier, what becomes harder later, what it costs). Say which capabilities are needed now
(accounts, storage, payments) and which are deliberately left out.

### 3. Write the four documents (drafts)

Fill the templates into `docs/product.md`, `docs/architecture.md`, `docs/acceptance.md` and `docs/plan.md`. Keep
each one short (one to two screens). Mark anything the student has not confirmed as `[to confirm]`. Every
acceptance criterion must be something a person or a test can check (an input, an action, an expected result).
The plan is a list of small slices; the first slice is always a **walking skeleton**: the app starts, shows one
page, and one test runs.

### 4. Get agreement

Show a summary: the user journey, the screens and agreed visuals, the MVP features and exclusions, the stack and
why, and the first three slices.
Ask the student to agree or change it. **Do not create application code before the student agrees on scope and
architecture.** Record the agreement (date, what was agreed) in the decision log of `docs/architecture.md`.

### 5. Set up the project (after agreement)

- If this folder is not a git repository, ask to run `git init`, then commit the starter files ("chore: start from
  the app starter").
- **Environment** (Python stacks; follow [stacks.md](stacks.md), "Setting up the environment"): find which Python
  versions are installed, choose the newest one that the chosen framework officially supports, and create an
  isolated virtual environment in `app/.venv` with it. From then on, call that environment's Python for
  everything; never install into a base Anaconda, system or global Python. Write the exact commands, for
  macOS/Linux and Windows, into `app/README.md`.
- **Settings and `.env`:** list every setting in `app/.env.example` with placeholders or safe development values
  (no real secret). Design the settings so that: the tests run without any `.env`; nothing unsafe is the default
  (debug mode off unless set; a development-only secret key accepted only with debug on *and* a local host); the
  student creates `app/.env` themselves with `cp .env.example .env` (Windows: `copy .env.example .env`), listed as
  an install step in `app/README.md`; and for your own runs you pass non-secret settings inline (for example
  `DEBUG=1 .venv/bin/python ...`). You never create, read or edit `app/.env`.
- Create the walking skeleton in `app/` exactly as `docs/architecture.md` says: dependency file, the app entry
  point, one test, `app/README.md` (install, run, test, checks, and what to do if the port is busy), and
  `app/.env.example` if the stack needs settings. Fill the "This project" section of `AGENTS.md`.
- **Permissions:** in Claude Code, propose the narrow allow rules for this stack's test and check commands from
  [stacks.md](stacks.md) ("Permissions for the chosen stack") and add them to `.claude/settings.json` only if the
  student agrees (Claude Code asks before that file changes). Cline has no per-command allow list: tell the
  student which commands are the routine test and check commands, so they know what they are approving.
- Run the test and start the app. Check that the first page loads (see `test-and-check` for how).
- Add a first entry to `AI-USAGE.md`.
- Propose a checkpoint commit.

## Outputs

`docs/product.md` (including agreed screens and visuals), `docs/architecture.md`, `docs/acceptance.md`, `docs/plan.md`
(agreed), the virtual environment and walking skeleton in `app/`, the "This project" section of `AGENTS.md` filled in, and a first `AI-USAGE.md` entry.

## Verification

- Every acceptance criterion is checkable; every MVP feature has at least one criterion.
- Each important calculation has a formula, units and an example with a known answer and its written hand working
  in `docs/acceptance.md` (see `test-and-check`).
- Each main screen has its content, interactions and visuals (or "table only") agreed in `docs/product.md`.
- The tests run in the project's virtual environment without an `app/.env` file.
- The skeleton's test passes and the first page was seen to load (or the gap is stated).

## Stop when

- The student agrees to the documents and the skeleton runs: hand over to `build-feature` for slice 2.
- **Stop and ask** if the student's requirements contradict each other (for example "no budget" and "a paid
  data feed"), if the idea needs something the stack cannot do, or if a requirement involves real customers'
  money or personal data that the team cannot protect yet. Explain the problem and offer a smaller option.

## Common mistakes

- Asking ten questions at once, or re-asking what `docs/product.md` already says.
- Choosing a customer-facing stack with accounts when a single-user dashboard would prove the idea.
- Acceptance criteria such as "the app is user-friendly" (not checkable).
- Never asking what the screens should look like, then building a plain table when the student expected a
  dashboard; or the opposite, adding charts nobody asked for.
- Using whatever `python` is first on the PATH, which may be too old or a shared base installation.
- Writing feature code during the interview.
