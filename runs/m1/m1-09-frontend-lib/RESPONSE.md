# RESPONSE — m1-09-frontend-lib

- From: frontend-engineer → to: owner (top-level Claude Code session)
- Captured by: scripts/dispatch-step.mjs from the `result` field of `claude -p --output-format json`
- Session id: ccc20e50-36cd-4cac-abfb-e97effd90a55 (local Claude Code transcript; not committed)
- Finished: 2026-11-03T18:33:00.723Z; exit code 0; status completed
- Redaction: only explicit [REDACTED:<kind>] markers were inserted; otherwise verbatim.

<!-- VERBATIM:BEGIN -->
I built the five frontend helper files with their tests and added the two chart packages. Vitest passes (60/60, exit 0), and lint and typecheck also exit 0. I did not run `npm run verify` from the root, because other steps are still editing files in parallel and it is not this step's done condition.

- **`types.ts`** has TypeScript copies of every shape in the API contract (brief §5 and `architecture.md`). That includes the overview's `notes` field, which the brief lists and the architecture table leaves out.
- **`api.ts`** calls only same-origin `/api/*` and raises one `ApiError` that carries the error envelope.
  - If no answer arrives, or the proxy answers 5xx without an envelope (what happens when the backend is down), it gives `backend_unreachable` with the exact text "Backend not reachable: start it with npm run demo".
  - A backend 500 that does carry an envelope keeps its code and `reference`.
  - A cancelled request passes through unchanged.
- **`format.ts`** shows money in millions with thousands separators and a true minus sign (−), and the exact value for tooltips (`1,234,567,000,000 USD`). A missing value shows `—`, never 0, and the badge reads `MISSING · <reason>`. It also covers ISO dates, fiscal year-end `MMDD` → `MM-DD` (or "Not reported by SEC"), and `FY2024 (ends 2024-09-28)`.
- **`combobox.ts`** handles the search list keys: ↑/↓ wrap around, Enter with nothing highlighted does nothing, Esc closes. It also builds the ids screen readers need to announce the highlighted result.
- **`shortcuts.ts`** decides when `/` or Ctrl/Cmd-K should jump to the search box. `/` is ignored in any text field, including the search box itself, so it can still be typed. Ctrl/Cmd-K is ignored in other text fields but works inside the search box, so the browser's own Ctrl-K doesn't fire.
- **Packages:** `recharts` 3.10.1 and `react-is` 19.3.1 are pinned exactly, and the lockfile is updated.

## Handoff
Changes: `examples/sec-analytics/frontend/lib/{types,api,format,combobox,shortcuts}.ts` and `{api,format,combobox,shortcuts}.test.ts` (new); `examples/sec-analytics/frontend/package.json` and `package-lock.json` (exact `recharts` 3.10.1 and `react-is` 19.3.1, added with `npm install --save-exact`).
Verification evidence: inside `fe/`: `npm run test` exit 0 (8 files, 60 tests, including other steps' files); `npm run lint` exit 0 with no warnings; `npm run typecheck` exit 0; `npm ls recharts react-is` shows 3.10.1 and 19.3.1. `npm run verify` not run (parallel steps still editing; not this step's done condition).
Remaining findings: (1) The backend models (m1-06) don't exist yet, so `types.ts` follows the brief and `architecture.md` only. It needs checking against the pydantic models once they land; one assumption is that `FormerName.from`/`to` can be null. (2) The brief has `notes: [str]` in the overview but the `architecture.md` table doesn't; `types.ts` follows the brief. The table needs that field added (for m1-14). (3) Proposed decision-log rows, marked "routine technical choice under delegation": (a) Ctrl/Cmd-K is ignored in other text fields but kept in the search box; (b) millions are rounded to whole numbers and −0 shows as 0; (c) a 5xx without an envelope is treated as backend down. (4) `lib/health.ts` still shows the scaffold's "npm run dev" wording; `BackendStatus` (m1-10) should use `BACKEND_UNREACHABLE`. (5) `npm install` warned that fsevents has install scripts not covered by allowScripts; I left that alone.
Next action: m1-10-screens builds the components on `lib/api.ts`, `format.ts`, `combobox.ts` and `shortcuts.ts`; check `types.ts` against m1-06's models.
<!-- VERBATIM:END -->
