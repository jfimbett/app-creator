# RESPONSE — m1-08-design-shell

- From: design-lead → to: owner (top-level Claude Code session)
- Captured by: scripts/dispatch-step.mjs from the `result` field of `claude -p --output-format json`
- Session id: bb56fe23-f6b9-4219-be5a-ce39e1592cd9 (local Claude Code transcript; not committed)
- Finished: 2026-11-03T18:32:35.998Z; exit code 0; status completed
- Redaction: only explicit [REDACTED:<kind>] markers were inserted; otherwise verbatim.

<!-- VERBATIM:BEGIN -->
The design system, the page shell and the shared state and badge components are in place. Lint, typecheck and the unit tests all pass. I haven't looked at the result yet: my attempt to take screenshots timed out.

**Colours.** I measured every text colour from the brief against the page background, the panel and the raised panel. All pass the 4.5:1 minimum for readable text:

| Text colour | Background | Panel | Raised panel |
|---|---|---|---|
| Text `#DCE3EE` | 14.68 | 13.47 | 12.31 |
| Muted `#8C9AB3` | 6.67 | 6.12 | 5.59 |
| Amber accent `#F2B33D` | 10.19 | 9.35 | 8.54 |
| Link `#6CB6FF` | 8.82 | 8.09 | 7.39 |
| Positive `#3FB68B` | 7.47 | 6.85 | 6.26 |
| Negative `#F0605D` | 5.90 | 5.41 | 4.95 (lowest) |
| Warning `#E8A33A` | 8.78 | 8.06 | 7.36 |

I also added a light theme, which is optional at M1. Every text colour in it is at least 5.23:1. It only switches on when the page asks for it explicitly, not from the computer's own light/dark setting. Playwright's browser reports a light setting by default, so following it would have made the test screenshots light instead of the required dark.

**What I built:**
- **Tokens** in `globals.css`: one CSS variable per colour role, available to Tailwind as classes like `bg-panel` and `text-muted`. Also system fonts only (no font downloads), the type sizes from the brief, one amber focus ring for every control, and the reduced-motion setting is respected. I added shared styles for figures (aligned digits, right-aligned) and for dense tables (sticky header row and first column). I kept the old scaffold colour names working so the current home page doesn't break.
- **Shell** (`layout.tsx`): a "Skip to content" link, the header, and one main content area.
- **`AppHeader`**: the "SEC ANALYTICS" wordmark, the `RECORDED SEC DEMO` badge, and empty spaces for the search box and backend status. It has no search logic and draws nothing when the search space is empty, so there is no dead control. Below 768 px wide the search drops to its own full-width row.
- **`SourceBadge`**: always a text label (`RECORDED SEC DEMO · snapshot <date>`, `SYNTHETIC TEST DATA`, or `MISSING · <reason>`), never colour alone. It prefers the label the backend sends.
- **`StatePanel`**: covers loading (placeholder rows, no spinner), empty, missing, offline and error. Each state has a text tag. Offline and error are announced to screen readers immediately. The offline text is "Backend not reachable: start it with npm run demo", and errors can show a reference number and a "Try again" button.
- **`Panel`** (not in your file list): the bordered box with a small title row and its badge on the right. The brief allows small helper files in the same folder.

**Things for the next steps:**
- **Pages must not add their own main area**, because the shell now provides it. The current home page still has one, so main areas are nested until the screens step rewrites that page. The screens step also needs to put the search and backend status into the header in `layout.tsx`.
- **`package.json` and `package-lock.json` show as changed in git.** I didn't edit them; the parallel frontend-library step is probably adding Recharts there.

## Handoff
Changes: `fe/app/globals.css`, `fe/app/layout.tsx`; new `fe/components/AppHeader.tsx`, `SourceBadge.tsx`, `SourceBadge.test.tsx`, `StatePanel.tsx`, `StatePanel.test.tsx`, `Panel.tsx` (all under `examples/sec-analytics/frontend/`).
Verification evidence: in `fe/`: `npm run lint` exit 0; `npm run typecheck` exit 0; `npx vitest run` exit 0 (4 files, 17 tests); `npx next build` exit 0. Contrast measured with a WCAG luminance script: dark text colours are 4.95–14.68:1, light 5.23–16.38:1. Screenshots not looked at: an ad-hoc Playwright capture at 1366 and 390 px timed out twice inside `page.screenshot`, so the layout is visually unverified at every width.
Remaining findings: (1) Visual check still to do in m1-10/m1-11 at 1440, 1366 and 390 px. (2) The current `page.tsx` has its own main area, nested inside the shell's until m1-10 replaces it. (3) The light theme is opt-in through `data-theme="light"` and is not a done criterion. (4) `package*.json` changes come from another step, not this one. (5) `Panel.tsx` is an added helper beyond the listed files.
Next action: m1-10 fills the AppHeader `search` and `status` slots in `layout.tsx` and builds screens with `Panel`, `SourceBadge` and `StatePanel`, then looks at the screenshots at all three widths.
<!-- VERBATIM:END -->
