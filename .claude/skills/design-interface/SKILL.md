---
name: design-interface
description: Use when creating or changing a screen, page, form, table, chart, dashboard, theme or navigation, when the app looks confusing, cluttered or inconsistent, when a user cannot find or understand something, or before calling a screen done at phone and laptop widths.
---

# Design an interface people can use

The interface serves the main user journey in `<docs>/product.md`. Clarity beats decoration.

**Paths.** `<docs>` and `<frontend>` come from `app-creator.config.json` (`app.docsDir`, `app.frontendDir`).
Standard stack: Next.js + React + TypeScript + Tailwind CSS v4, shadcn/ui-style components where they help,
Recharts for agreed charts ([docs/TOOLKIT.md](../../../docs/TOOLKIT.md) §2).

## Inputs

- `<docs>/product.md` (customer, main journey, **Screens and visuals**, theme and density),
  `<docs>/acceptance.md` (what must be visible and checked), `<docs>/architecture.md` (where the logic layer and
  the API client live).
- The current screens: read `<frontend>/app/`, `components/`, `app/globals.css`, and run `npm run dev` (or
  `npm run demo`) to see them when possible.
- Guides in this folder:
  - [design-system.md](design-system.md): colour tokens, dark/light theme with Tailwind v4, type scale,
    spacing, density, shadcn/ui;
  - [ui-states-and-forms.md](ui-states-and-forms.md): loading, empty, error, offline, missing-data states; forms;
  - [responsive-and-accessibility.md](responsive-and-accessibility.md): 390/1366 px, keyboard, focus, contrast,
    reduced motion, chart text alternatives;
  - [charts-and-data-display.md](charts-and-data-display.md): choosing cards, charts and tables; honesty rules.

## Actions

1. **Sketch before coding.** For each screen of the change, in a few lines: its purpose (one sentence), what the
   user sees first, the inputs, the one primary action, the cards, charts and tables with their units and
   periods, and the text for each state (**loading, empty, error, offline/demo, missing data**). Show it to the
   owner when the change is more than a small tweak (in delegated mode the orchestrator's plan covers routine
   layout; new screens or visuals not in `product.md` are scope and need the owner). If the screen shows numbers
   and `product.md` has no agreed visuals for it, propose them from
   [charts-and-data-display.md](charts-and-data-display.md), get an explicit yes, and record them in "Screens and
   visuals". Never add charts nobody asked for.
2. **Set or reuse the design system** ([design-system.md](design-system.md)): role tokens in `globals.css`,
   exposed to Tailwind with `@theme inline`; the type scale; spacing steps; the density in `product.md`; shared
   components in `<frontend>/components/ui/`. No hex values or one-off button styles in screens.
3. **Build with these rules:**
   - One primary action per screen; the most important number or result is the most visible.
   - Plain labels in the customer's words; units on every number (`km`, `%`, a currency), consistent decimals,
     dates in one format, `tabular-nums` for figures.
   - Every input has a visible label, a sensible default, and validation messages that say how to fix it
     ([ui-states-and-forms.md](ui-states-and-forms.md)).
   - Every data area has its states designed; never raw exceptions, keys or internal ids.
   - **Responsive:** usable at 390 px and 1366 px: no sideways page scrolling, cards wrap, tables scroll inside
     their own box or drop secondary columns, charts resize with readable labels.
   - Tables: right-aligned numbers, headers visible, units in headers, only the columns the journey needs.
   - Charts follow the honesty checklist (missing ≠ 0, units, periods, text alternative). Interface and chart code
     only format and draw values prepared by the backend's logic layer; they never compute or round the figures.
   - Show where data comes from (source, date; live vs cached vs recorded) when the product depends on it.
4. **Accessibility** (go through [responsive-and-accessibility.md](responsive-and-accessibility.md)): contrast
   4.5:1 for text in both themes, keyboard access with visible focus, labelled fields with announced errors,
   meaning not by colour alone, headings in order, reduced motion, a text alternative and data table for every
   chart. shadcn/Radix components handle much of the keyboard behaviour; check what you add or override.
5. **Check it** (see `test-and-check`):
   - **tests**: pytest on the logic layer for every value, gap and caveat shown; Vitest for frontend helpers
     (formatting, state mapping);
   - **browser check**: a Playwright spec in `<frontend>/e2e/` for the screen's main interaction at 1366 and
     390 px, including at least one empty or error state, run by `npm run verify`;
   - **visual inspection**: open the screenshots in `<frontend>/test-results/` (both widths, dark and light if
     both are supported) and look; then ask the owner to look at the running app.
   Report the three separately. If Playwright cannot run, give the owner a short click-through checklist and mark
   the screens **not verified**.

## Outputs

Updated interface code and shared components, tokens in `globals.css`, the agreed visuals and states recorded in
`<docs>/product.md`, Playwright specs for the changed screens, and in the change report: what each changed screen
does, and the results of tests, browser check and visual inspection, each named separately (including what was
not checked).

## Verification

- `npm run verify` exits 0, including the Playwright specs for the changed screens at both widths.
- The main action of each changed screen works with normal, empty and invalid input, at both widths.
- Every card, chart and table value comes from the logic layer, and its tests cover missing, zero, negative and
  not-comparable cases where the data can contain them.
- No raw colour values in components; text contrast checked in each supported theme.
- The accessibility checklist was gone through; anything not met is listed as an open problem in
  `<docs>/plan.md`.

## Stop when

- The screens meet the acceptance criteria and the checklists, or the remaining gaps are listed.
- **Stop and ask** if the requested design conflicts with the main journey or exclusions in `product.md`, needs a
  different interface framework than `architecture.md` says, or adds a paid font, icon set or service.
- A Playwright spec fails twice after two different fixes: switch to `debug-issue` with the failing spec and its
  screenshot or trace.

## Common mistakes

- Numbers without units, or rounding that differs between card, table and chart.
- Computing values in React or chart code, or drawing a missing value as zero.
- A loading spinner with no end, an empty white box for "no data", or "Something went wrong" with no next step.
- Hard-coded colours that break in the other theme; `outline-none` with no focus style.
- Calling a screen "checked" because the tests pass, without opening the screenshots.
- Pulling in a whole UI library for one widget, or decorative cards and controls that do nothing.
- Silently showing demo or cached data as if it were live.

## Example

Screen "Weekly totals" (running-club app), sketch:

- Purpose: see each member's distance for a week and who improved. First seen: the "Most improved" card.
- Input: week picker (default: current week). Primary action: none (read-only); secondary "Add a run".
- Cards: "Most improved — Ana, +2.0 km vs week 11". Table: Member, Distance (km), Change (km); right-aligned,
  `tabular-nums`. Chart: none (owner chose table only).
- States: loading "Loading weekly totals…"; empty "No runs for week 12. **Add a run**"; error from the envelope
  with **Try again**; missing "n/a (no runs last week)" in the Change column; demo label "Sample data".
- Checks: pytest for `weekly_totals` (CALC1, missing week); Vitest for `formatValue(null, "km", "no runs last
  week")`; Playwright `e2e/weekly.spec.ts` at 1366 and 390 px plus a mocked 503; screenshots opened.
