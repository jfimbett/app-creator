---
name: design-interface
description: Use when creating or changing a screen, page, form, table, chart, dashboard or navigation, when the student says the app looks confusing or cluttered, or when a user cannot find or understand something.
---

# Design an interface people can use

The interface serves the main user journey in `docs/product.md`. Clarity beats decoration.

## Inputs

- `docs/product.md` (customer, main journey, **Screens and visuals**), `docs/acceptance.md` (what must be visible
  and checked), `docs/architecture.md` (interface framework, where the shared calculation layer lives).
- The current screens: read the interface code, and run the app to see them when possible.
- For numbers, cards or charts: [financial-visuals.md](financial-visuals.md).

## Actions

1. **Sketch before coding.** For each screen of the change, in a few lines: its purpose (one sentence), what the
   user sees first, the inputs, the main action, the cards, charts and tables with their units and periods, and
   what the user sees while **loading**, with **no data**, and on an **error**. Show it to the student when the
   change is more than a small tweak. If `docs/product.md` has no agreed visuals for this screen and it shows
   numbers, propose them (cards, charts or a table, from [financial-visuals.md](financial-visuals.md)) and get an
   explicit yes; then record them in "Screens and visuals". Never add charts nobody asked for.
2. **Build with these rules:**
   - One primary action per screen; the most important number or result is the most visible.
   - Plain labels in the customer's words; units and currency on every number (`USD m`, `%`), consistent decimals,
     dates in one format.
   - Every input has a visible label, sensible default and validation with a message that says how to fix it.
   - Loading, empty and error states are designed, not left to blank areas or stack traces: a loading message for
     anything slower than about a second, an empty state that says what to do next, an error message in plain
     words with a next step. Never show raw exceptions, keys or internal ids to users.
   - **Responsive:** usable at a phone width (390 px) and a laptop width (1366 px): no sideways scrolling, cards
     wrap, tables scroll inside their own box or drop secondary columns, charts resize and keep readable labels.
   - Tables: right-align numbers, keep headers visible, limit columns to what the journey needs.
   - Charts follow the honesty checklist in [financial-visuals.md](financial-visuals.md). Interface and chart code
     only display values prepared by the shared, tested layer; they never compute or round financial numbers.
   - Show where numbers come from (source and date) when the product depends on trusted data.
3. **Accessibility basics** (check each one):
   - text contrast at least 4.5:1 against its background (large text 3:1);
   - every image and chart has alternative text and an adjacent text summary or table;
   - all actions reachable and usable by keyboard, with visible focus;
   - form fields have labels tied to the input; errors are announced in text, not only colour;
   - meaning never carried by colour alone (signs, symbols or words as well);
   - headings in order; page has a title; layout usable at 200% zoom.
   Framework defaults (Streamlit widgets, Django forms) handle some of this; check what you add or override.
4. **Check it** (see `test-and-check` and its browser-check guide):
   - tests on the shared layer for every value, gap and caveat shown, and a test-client test that the page
     contains them;
   - a **browser check** of the critical interactions at both widths, including the loading, empty and error
     states, when the project has its browser-check tool installed (or offer to install it);
   - **visual inspection:** look at the screenshots, then ask the student to look at the running app.
   Report the three separately. Without a browser check, give the student a short click-through checklist and
   mark the screens **not verified**.

## Outputs

Updated interface code, the agreed visuals recorded in `docs/product.md`, a short note in the change report on what
each changed screen does, and the results of the tests, the browser check and the visual inspection, each named
separately (including what was not checked).

## Verification

- The main action of each changed screen works with normal, empty and invalid input, at both widths.
- Every chart and card value comes from the shared layer, and its tests cover missing, zero, negative and
  not-comparable cases where the data can contain them.
- The accessibility checklist was gone through; anything not met is listed as an open problem.

## Stop when

- The screens meet the acceptance criteria and the checklist, or the remaining gaps are listed.
- **Stop and ask** if the requested design conflicts with the main journey or exclusions in `docs/product.md`, or if
  it needs a different interface framework than `docs/architecture.md` says.

## Common mistakes

- Numbers without units, or rounding that differs between card, table and chart.
- Computing values a second time in chart code, or drawing a missing value as zero.
- Calling a screen "checked" because the tests pass.
- Hiding errors with a generic "something went wrong" and no next step.
- Adding a new library for one widget the framework already has.
