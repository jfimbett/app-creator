---
name: build-feature
description: Use when the student asks to add, change or continue a feature, or to work on the next slice of docs/plan.md, in an application whose product and architecture documents are agreed.
---

# Plan and build one feature slice

One slice at a time: plan it, build it in small steps, check it like a user would, then report and checkpoint.

## Inputs

- `docs/product.md`, `docs/architecture.md`, `docs/acceptance.md`, `docs/plan.md`. If `docs/product.md` or
  `docs/architecture.md` is missing or not agreed, use `product-interview` first.
- The student's request, or the next `todo` slice in `docs/plan.md`.
- The actual code in `app/`: read the files the slice touches before planning.

## Actions

1. **Plan the slice** in a short message:
   - what the user will be able to do afterwards, and which acceptance criteria it covers (add new criteria to
     `docs/acceptance.md` if the request is new);
   - the files to create or change, one line each;
   - the checks you will run (from `test-and-check`: which tests, and how the journey will be checked);
   - risks or decisions the student must make.
   If the request changes scope (a new MVP feature, an exclusion, a new capability such as accounts or payments),
   say so and ask before planning further. If the slice needs more than about 5 files or one sitting, split it.
2. **Wait for the student's go-ahead** on the plan. Routine edits inside the agreed plan do not need separate
   approval.
3. **Build in small steps.** Logic first, with tests (`test-and-check`), then the interface (`design-interface`),
   then wiring. Keep calculations out of interface and chart code: the shared logic layer prepares every value
   that cards, charts and tables show. If the slice adds a screen whose visuals are not yet agreed in
   `docs/product.md`, propose them first (`design-interface`). Use the specialised skill when the slice touches its area:
   `integrate-api`, `manage-data`, `add-accounts`, `add-payments`.
4. **Run the checks** after each step: the relevant tests, then the full test command from `AGENTS.md`.
5. **Check the user journey** for this slice: start the app and exercise it (see `test-and-check`, "Checking the
   journey"); for screens, run the project's browser check at both widths and look at the screenshots. If you
   cannot run it, say exactly what the student should click and what they should see.
6. **Update the documents:** slice status and progress log in `docs/plan.md`; acceptance criteria status in
   `docs/acceptance.md`; any decision in `docs/architecture.md`; a line in `AI-USAGE.md` if the AI contributed
   something meaningful (design, code, a fix).
7. **Report and checkpoint** using the change report format in `AGENTS.md`, then propose a commit with a clear
   message. Once the slice is complete and committed, offer `review-changes` on that commit for larger slices and
   for any change to calculations, accounts, payments or secrets.

## Outputs

Working code for the slice, tests, updated `docs/plan.md` and `docs/acceptance.md`, a change report, a proposed
commit.

## Verification

- The tests that cover the slice fail without the change and pass with it (when you wrote new tests, show one
  failing first).
- The full test command passes.
- The journey for the slice was exercised, or the gap is stated with manual steps.

## Stop when

- The slice's criteria pass and the report is given. Do not start the next slice without the student.
- **Stop and ask** when: the plan needs a decision only the student can make; a check fails twice after two
  different fix attempts (switch to `debug-issue`); the change needs a new paid service, new personal data, or a
  new secret; or the code you find contradicts `docs/architecture.md`.

## Common mistakes

- Building three features in one go, so nothing can be reviewed.
- Reporting "done" because the code was written or the app started: done means the criteria were checked.
- Silently adding features that are listed under "Explicitly not in the MVP".
