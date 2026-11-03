# Responsive layout and accessibility

Two widths are checked on every screen: **390 px** (a phone) and **1366 px** (a laptop). The scaffold's Playwright
smoke test (`<frontend>/e2e/smoke.spec.ts`) already runs both and saves screenshots in
`<frontend>/test-results/`. Add your screens to that pattern.

## 1. Responsive checklist

- [ ] No sideways scrolling of the page at 390 px (`document.documentElement.scrollWidth <= 390`).
- [ ] Mobile first: base classes for the phone, `md:`/`lg:` for wider (`grid-cols-1 md:grid-cols-2 lg:grid-cols-4`).
- [ ] Cards wrap; navigation collapses into a menu button or a horizontal scroller with visible overflow.
- [ ] Tables scroll inside their own box (`<div className="overflow-x-auto">`) or drop secondary columns
      (`hidden md:table-cell`); the first column stays readable.
- [ ] Charts resize (`ResponsiveContainer`), keep readable labels (fewer ticks on phones), and keep their table.
- [ ] Touch targets at least 24×24 px, preferably 44×44 px on phones.
- [ ] Text still fits at 200 % browser zoom at 1366 px.

A Playwright check for sideways scrolling:

```ts
test("no horizontal scroll at 390 px", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/weekly");
  await expect(page.getByTestId("weekly-table")).toHaveAttribute("data-state", "ok");
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
  expect(overflow).toBeLessThanOrEqual(0);
});
```

## 2. Keyboard and focus

- [ ] Every action works with the keyboard alone: Tab / Shift+Tab to move, Enter/Space to activate, Escape to
      close dialogs and menus, arrow keys inside menus, tabs and comboboxes (shadcn/Radix components do this).
- [ ] Use real elements: `<button>` for actions, `<a href>` for navigation, `<label>` for inputs. No clickable
      `<div>`.
- [ ] **Visible focus** on everything focusable: `focus-visible:outline-2 focus-visible:outline-offset-2
      focus-visible:outline-focus` (as in the scaffold's button). Never `outline-none` without a replacement.
- [ ] Logical tab order (follows the visual order); no positive `tabIndex`.
- [ ] A "Skip to content" link as the first focusable element on pages with navigation.
- [ ] Dialogs trap focus while open and return it to the opener on close.
- [ ] Keyboard shortcuts (for example `/` to focus search) are optional extras, announced, and never override
      typing inside inputs.

Playwright can check keyboard paths:

```ts
await page.keyboard.press("Tab");
await expect(page.getByRole("searchbox", { name: "Search members" })).toBeFocused();
```

## 3. Contrast and colour

- [ ] Body text at least 4.5:1 against its background; large text (≥ 24 px, or ≥ 19 px bold) and meaningful UI
      parts (input borders, focus rings, chart lines) at least 3:1. Check both themes.
- [ ] Meaning is never carried by colour alone: add a word, sign or symbol ("Error:", "−2.0", "▲").
- [ ] Muted text (`--muted`) still passes 4.5:1 where it carries information.

How to check: browser developer tools show the contrast ratio of text in the colour picker; for a token pair, any
WCAG contrast calculator. Optionally add `@axe-core/playwright` to the Playwright tests (ask first: it is a new dev
dependency) and fail on serious violations.

## 4. Structure and names

- [ ] One `<h1>` per page, headings in order (`h2` then `h3`), a page `<title>` (Next.js `metadata.title`).
- [ ] Landmarks: `<header>`, `<nav aria-label="Main">`, `<main id="content">`, `<footer>`.
- [ ] Icons-only buttons have an accessible name (`aria-label="Close"`).
- [ ] Dynamic messages use `role="status"` / `aria-live="polite"` (errors `role="alert"`), as in the scaffold.
- [ ] `lang` set on `<html>`.

## 5. Motion

- [ ] Respect reduced motion: Tailwind `motion-safe:transition` / `motion-reduce:transition-none`; Recharts
      `isAnimationActive={false}` when `window.matchMedia("(prefers-reduced-motion: reduce)").matches`.
- [ ] Nothing flashes more than three times per second; no auto-playing movement that cannot be paused.

## 6. Charts' text alternatives

- [ ] A visible title with the unit and period.
- [ ] An accessible name on the chart area (`role="img"` and `aria-label` summarising what it shows).
- [ ] A visible summary sentence ("Distance rose from 18.0 km in week 10 to 24.5 km in week 12; no data for week 11.")
      **and** a table with every value, including "n/a (reason)" rows, adjacent or behind a "Show data" toggle
      that is a real `<button aria-expanded>`.
- [ ] Tooltips repeat information, never add it.

More on honest charts: [charts-and-data-display.md](charts-and-data-display.md).

## 7. How to report

Report three kinds of evidence separately (AGENTS.md rule 8):

1. **Automated tests**: `npm run verify` (exit code), including the Playwright journeys at both widths.
2. **Screenshots looked at**: which files in `<frontend>/test-results/` you opened, and what you saw.
3. **The owner's own look**: done or pending, with the click-through steps you gave them.

Anything on these checklists that is not met goes into the change report and `<docs>/plan.md` "Known problems".
