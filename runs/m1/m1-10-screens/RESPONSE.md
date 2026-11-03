# RESPONSE — m1-10-screens

- From: frontend-engineer → to: owner (top-level Claude Code session)
- Captured by: scripts/dispatch-step.mjs from the `result` field of `claude -p --output-format json`
- Session id: 9cfc69d3-e6a7-4893-954a-d5a132aa4383 (local Claude Code transcript; not committed)
- Finished: 2026-11-03T18:54:44.803Z; exit code 0; status completed
- Redaction: only explicit [REDACTED:<kind>] markers were inserted; otherwise verbatim.

<!-- VERBATIM:BEGIN -->
The M1 screens are built and `npm run verify` passes (exit 0). I looked at my own screenshots at 1440, 1366 and 390 px and fixed what I found.

**What a user can now do**
- **Home page:** a heading, the shortcut hints, the note "Search covers the demo companies only: Apple, Microsoft, Alphabet" always visible under the header search, and the three demo companies as links (name · ticker · CIK).
- **Search:** `/` or Ctrl/Cmd-K focuses it, typing shows matches, ↑/↓ move, Enter opens, Esc closes. A miss shows "No match in the demo universe (3 companies)".
- **Company page:** the heading reads "Apple Inc. · AAPL · CIK 0000320193" and a short CIK in the address (e.g. `/companies/320193`) is replaced by the 10-digit one. The profile follows the SEC data. Alphabet's four "Nasdaq" entries are shown once and former-name dates are shown as `YYYY-MM-DD`. Missing fields say "Not reported by SEC".
- **Dashboard:** two key figures (latest annual revenue and net income) with fiscal year-end and unit. Below them are the line chart with Revenue / Net income toggles and "Last 5 years / All in snapshot", the restatement note, and a table of the same values. Hovering or focusing any value shows its concept, accession, period, form and filing date. If a company has no revenue, the chart area shows an empty message with the backend's note.
- **Problem states:** loading skeletons, invalid CIK ("A CIK has up to 10 digits"), company not in the snapshot, "Backend not reachable: start it with npm run demo" (plus a "Backend OFFLINE" badge in the header), a 404 page and an error page with "Try again".

**What the screenshots showed**
- **Fixed:** the provenance tooltip was rendered inside a paragraph, which is invalid HTML and caused React hydration errors in the console. It now renders separately at the end of the page, and those errors are gone.
- **Fixed:** the profile panel stretched down to match the dashboard's height.
- **Fine everywhere:** at all three widths the layout is dense and dark, the badges are readable and nothing overlaps. At 390 px the page never scrolls sideways (checked in the test), and wide tables scroll inside their own box.
- **Still open:** the only browser console error left is a 404 for `/favicon.ico`, which the app doesn't have yet.

**How I checked it**
- **Automated tests:** lint, typecheck and Vitest all pass (70 tests, including new ones for the display helpers and `BackendStatus`).
- **Browser check:** I wrote a throwaway Playwright spec and ran it with the project's config against the demo on ports 3200/8200 (3 passed). It covered home, `/`, `aapl` ↓ Enter, Cmd-K, tooltip contents, "Last 5 years", the series toggle, Alphabet, `abc`, `1234`, an unknown page and backend down. It also checked that every request stayed on 127.0.0.1, and the 390 px width check. I deleted the spec afterwards because the real one is step m1-11. `npm run verify` currently runs only the old scaffold smoke spec, at 1366 and 390 px.
- **Visual check:** I looked at the screenshots described above. The owner's own look is still pending.

**Things you should know**
- I edited `app/layout.tsx`, which wasn't on my list, to put the search and backend status into the header slots the layout had left for this step.
- I deleted the scaffold's `HealthStatus` component and its test, since `BackendStatus` replaces it. I also added two small helper files in `lib/`.
- Running Next.js generated a stray `frontend/AGENTS.md`. I deleted it, but it may come back on later runs.
- `PROGRESS.md` was already modified before I started; I didn't touch it.
- I didn't update `milestones/*.md` or `AI-USAGE.md`; step m1-14 does that.

## Handoff
Changes: in `examples/sec-analytics/frontend/` — new: `components/{CompanySearch,BackendStatus,BackendStatus.test,CompanyProfile,KeyFigures,RevenueIncomeChart,ProvenanceTip}.tsx`, `lib/display.ts`, `lib/display.test.ts`, `lib/useApiResource.ts`, `app/companies/[cik]/page.tsx`, `app/not-found.tsx`, `app/error.tsx`; changed: `app/page.tsx`, `app/layout.tsx` (header slots); deleted: `components/HealthStatus.tsx` and its test (replaced by BackendStatus). No `app/api/`, no new dependencies.
Verification evidence: frontend `npm run lint`, `npm run typecheck`, `npm run test` exit 0 (9 files, 70 tests); temporary Playwright spec via the project config against `FRONTEND_PORT=3200 BACKEND_PORT=8200 npm run demo`: 3 passed (1440/1366/390), then deleted; root `npm run verify` exit 0 ("All checks passed"). Screenshots looked at: home 1440/390, Apple 1440/390, Apple last-5 1366, search 1366, no-match 390, tooltip 390, Alphabet 390, offline 1366. Demo stopped (exit 130 from the interrupt); ports 3200/8200 free.
Remaining findings: `/favicon.ico` returns 404 (one console error); chart legend lists Net income before Revenue; `npm run verify` still runs only the scaffold smoke spec at 1366/390 (1440 and the full journey are m1-11); Next.js regenerates `frontend/AGENTS.md` (deleted here); the owner's own look is pending.
Next action: m1-11-e2e: write `e2e/m1-foundation.spec.ts` (the screens expose roles, `health-status`, `key-figures`, `overview-chart`, `company-profile`, `provenance-tip` test ids) and delete `smoke.spec.ts`.
<!-- VERBATIM:END -->
