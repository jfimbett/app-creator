# M6 Polish and launch: build brief

This is the implementation brief for SEC Analytics milestone 06, the last milestone. It was written on 2026-11-09 at
the owner's request ("improving a lot the user interface, having a dark and light mode, a landing page with fake
reviews, company info, pricing etc, and the /brag video"). Give it, unchanged, to the session that implements the
milestone. Corrections go into `FOLLOWUPS.md` (create it if needed) before they are acted on.

Paths are relative to the repository root unless stated. `fe/` means `examples/sec-analytics/frontend/` and `be/`
means `examples/sec-analytics/backend/`.

---

## 0. How to run this brief (for the session that executes it)

Work autonomously end to end and report once at the end (owner preference: scoped milestones done fully, one report).
Never push, tag on the remote, or change remotes: the owner pushes after reading the report.

1. On `main` in the main checkout, commit this brief alone: `docs(m6): build brief for polish and launch`. This is
   authorized by the owner running this brief. Do not change application files in the main checkout.
2. Save the instruction record `runs/m6/m6-01-implement-main-session/PROMPT.md` in the same format as
   `runs/m5/m5-01-implement-main-session/PROMPT.md` (sender, receiver, starting commit, workspace, brief sha256, the
   owner's exact instruction between `DISPATCH:BEGIN/END`, and "Decisions recorded before work").
3. Create the worktree `.worktrees/m6` on a new branch `work/m6` from `main`. Run `npm ci` and `npm run setup` there.
   Use spare ports (for example `BACKEND_PORT=8600 FRONTEND_PORT=3600`) so nothing collides with other services.
4. Check the start: `npm run verify` exits 0 before you change anything (otherwise record it as a finding first).
5. Do slices 6.1–6.6 (section 9) in order, each ending with `npm run verify` exit 0 and a local commit.
6. Pass the gate (section 10), then merge `work/m6` into `main` locally, create the local branch
   `milestone/06-polish-and-launch` and the local tag `m6` at the verified commit, and update the records (section 11).
7. End with the Change report from `AGENTS.md` plus the `## Handoff` block (section 12).

Use subagents where they help: `design-lead` or `frontend-engineer` for large screen work (give them sections 3–6 of
this brief and the files to touch), and `ux-reviewer`, `code-reviewer` and `security-reviewer` in parallel for the
review in slice 6.5. Keep one owner (this session) for integration, Git and the gate.

## 1. Starting ref

- Start from `main` (tag `m5` plus documentation commits; `git merge-base --is-ancestor m5 HEAD` exits 0).
- A student rebuilding this milestone later:

  ```bash
  git fetch origin --tags
  git switch -c exercise/build-m6 m5
  npm ci
  npm run setup
  ```

## 2. Context: what exists at `m5`

Read the code before planning; where it differs from this summary, the code and the statuses in
`milestones/acceptance.md` win, and you record the difference.

- **Config:** app in `examples/sec-analytics/`, `docsDir` `milestones`, `devEnv` `{"DATA_MODE": "live"}`, `demoEnv`
  `{"DATA_MODE": "fixtures"}`.
- **Example rules:** `examples/sec-analytics/CLAUDE.md` and
  `examples/sec-analytics/.claude/skills/sec-edgar-data/SKILL.md`. Read both.
- **Frontend:** Next.js 16 App Router, React 19, Tailwind 4, Recharts 3. One root layout (`fe/app/layout.tsx`) with a
  skip link, `AppHeader` (search, Compare link, Demo/Live selector, backend status) and `<main>`. `<html>` has a
  hard-coded `data-theme="dark"`. `fe/app/globals.css` defines colour roles (`--bg`, `--panel`, `--panel-raised`,
  `--border`, `--text`, `--text-muted`, `--accent`, `--link`, `--positive`, `--negative`, `--warning`, chart series)
  for dark and an unused, already contrast-checked `[data-theme="light"]` set, exposed to Tailwind with
  `@theme inline`. Components use roles, not raw hex (checked: no hex in `fe/components` or `fe/app`). System fonts
  only (offline).
- **Routes:** `/` (home: how to search, the three demo companies), `/companies/[cik]` (Overview), `/companies/[cik]/filings`,
  `/companies/[cik]/filings/[accession]` (reader), `/compare`. Analyst panel on company, reader and compare screens.
- **Tests:** Vitest units in `fe/lib`, `fe/components`; Playwright journeys `fe/e2e/demo-journey`, `m1`–`m5` specs at
  1440, 1366 and 390 px; several start with `page.goto("/")`. `m5-analyst.spec.ts` asserts
  `Object.keys(localStorage)` is `[]` (three places).
- **Planning:** [GOAL.md](../../GOAL.md), [docs/PRODUCT-DECISIONS.md](../../docs/PRODUCT-DECISIONS.md) (Q14, Q15, Q17,
  Q34), [milestones/architecture.md](../architecture.md), [acceptance.md](../acceptance.md), [plan.md](../plan.md).

All M1–M5 behaviour must keep working **with no key and no network**.

## 3. Owner decisions for M6 (record them first)

Add these to `docs/PRODUCT-DECISIONS.md` as owner decisions dated 2026-11-09 (new IDs, for example O1–O6), each
citing this brief. They change earlier delegated answers only where stated.

- **O1 Light mode becomes a done criterion** (supersedes the timing part of Q15). Both themes must pass the contrast
  checks and the screenshot inspection. Dark stays the default.
- **O2 A marketing landing page** at `/`. The current home moves to `/app`. All other URLs stay the same.
- **O3 Fictional testimonials** are allowed on the landing page **only** if clearly labelled as fictional on the page
  (see section 4.3). No real people, real employers, real logos or invented aggregate statistics ("10,000 analysts",
  "4.9 stars from 2,000 reviews").
- **O4 Illustrative pricing** is shown, but there are **no payments, checkout, accounts or sign-up** (Q17 and Q34
  still hold). Every pricing button goes to the app or to a section of the page; a visible note says the prices are
  illustrative and that this teaching app takes no payments.
- **O5 Fictional company information** (an About section). The maker is a fictional team; contact details use
  `example.com` addresses only (RFC 2606). The page states that SEC Analytics is not affiliated with or endorsed by
  the U.S. Securities and Exchange Commission, uses public SEC EDGAR data, and is not investment advice.
- **O6 A launch video** made with the installed `/brag` skill from the finished landing page and app.

## 4. Goal and new work

### 4.1 Theme: dark and light

- `fe/lib/theme.ts`: `type Theme = "dark" | "light"`; `readTheme()`, `writeTheme(t)`, `applyTheme(t)`. Storage key
  `sec-analytics.theme` in `localStorage`, values `"dark"` or `"light"` only; any other or missing value → `"dark"`.
  This key holds a display preference only; it never holds the AI key or anything about it.
- **No flash of the wrong theme:** a small inline script in the root layout's `<head>` sets
  `document.documentElement.dataset.theme` from storage before first paint (wrapped in `try/catch`; on any error,
  dark). Remove the hard-coded `data-theme="dark"` default only once the script sets it; keep `suppressHydrationWarning`
  on `<html>`. Server rendering assumes dark.
- **Toggle** `fe/components/ThemeToggle.tsx`: one button with a sun/moon inline SVG and a text label for screen readers,
  `aria-label` "Switch to light theme" / "Switch to dark theme", `aria-pressed` not used (it is an action). In the app
  header and in the landing header. Keyboard operable, visible focus ring.
- `color-scheme` follows the theme (already in the CSS). Charts, tooltips, the analyst panel, the settings dialog,
  the filing reader and every state panel must look right in both themes; if a chart reads colours once with
  `getComputedStyle`, make it re-read on theme change.
- **Contrast:** keep every text role ≥ 4.5:1 on `--bg`, `--panel` and `--panel-raised` and non-text UI (borders of
  inputs, focus ring, chart lines) ≥ 3:1, in both themes. Update the measured table in the `globals.css` comment.

### 4.2 Interface overhaul (app screens)

"Improve the interface a lot" means a visibly more polished, consistent product, not new features. Keep every data
rule, string that tests or acceptance criteria depend on, and the dark navy terminal identity (amber accent). Use the
`design-interface` skill and its checklist; the `taste` skill may help with judgment.

- **Design tokens:** a type scale (for example 12 / 13 / 14 / 16 / 20 / 28 / 40 px, with line heights), a 4-px
  spacing scale, radii (4 / 8 / 12), elevation (subtle shadows in light, border-plus-lift in dark), and motion tokens
  (120–200 ms, `prefers-reduced-motion: reduce` turns them off). Tabular numbers for every figure.
- **Shell:** a cleaner header: brand mark and name (links to `/app`), primary nav (Home, Compare), the search as the
  central control, then Demo/Live, backend status and theme toggle grouped on the right; collapses cleanly at 390 px.
  A slim app footer with the data disclaimer and a link back to the landing page.
- **`/app` home:** a search-first hero, then the demo companies as cards (ticker, name, CIK, exchange if known) with a
  small revenue sparkline drawn from the existing overview endpoint (no new API), and short "what you can do" hints
  (Overview, Filings, Compare, Analyst).
- **Company page:** a header block (ticker badge, name, CIK, SIC description, fiscal year end, source badge); key
  figures as cards with the year-on-year change shown with a sign and text, not colour alone; charts with consistent
  axes, gridlines, legend and themed tooltips; statement and ratio tables with a sticky header, right-aligned
  tabular numbers, row hover and readable "not reported" cells.
- **Filings and reader:** a clearer history table; the reader at a comfortable measure (about 70–80 characters) with a
  sticky section list on desktop.
- **Compare:** tidier chips and controls bar, chart and table aligned to the new tokens.
- **Analyst panel and AI settings:** the same tokens; no change to their behaviour or text.
- **States:** one consistent look for loading skeletons, empty, error and offline states.
- **Responsive:** 1440, 1366 and 390 px; no sideways page scroll; wide tables scroll inside their container.
- **Not allowed:** new runtime dependencies (no component kits, icon packages, animation libraries or web fonts),
  data or API changes, removing a feature or a provenance detail.

### 4.3 Landing page at `/`

One long, fast, static page (no backend call needed to render; it must also render when the backend is down), with
its own header and footer (route group `fe/app/(marketing)/`), sharing the theme and tokens. Sections, each with an
`id` for anchor links:

1. **Header:** brand, anchor links (Features, Reviews, Pricing, About, FAQ), theme toggle, button "Open the app" →
   `/app`. At 390 px the anchor links fold into a menu button that really opens and closes (Esc closes it).
2. **Hero** (`#top`): a clear headline about understanding public companies from SEC filings, one supporting sentence,
   buttons "Open the app" (`/app`) and "See pricing" (`#pricing`), and a real screenshot of the app (see below).
3. **Features** (`#features`): six cards that describe what the app actually does at `m5`: search by name, ticker or
   CIK; ten years of statements and ratios with provenance; the filings reader with sections and search; Compare up to
   four companies with indexing and CSV export; the optional AI analyst with checked source chips (own key); Demo mode
   that works offline. No claims the app cannot back up.
4. **How it works:** three steps (search a company → read the figures and filings → compare and ask).
5. **Reviews** (`#reviews`): 4–6 fictional testimonials with fictional names, plausible roles ("Finance student",
   "Teaching assistant, corporate finance", "Equity research intern") and generic, fictional organisations or none,
   initials avatars (no photos), optional stars per card. A visible label directly under the section heading:
   **"Fictional testimonials written for this teaching demo."** No aggregate rating and no invented usage numbers.
6. **Pricing** (`#pricing`): three illustrative tiers, for example **Student** $0 (Demo and Live data, Compare, own AI
   key), **Team** $12 per member per month (everything in Student plus shared workspaces, *described as illustrative*),
   **Classroom** $299 per term (instructor features, illustrative). The middle tier is highlighted. Every button goes
   to `/app` (labels such as "Start with the demo"). A visible note under the cards: **"Prices are illustrative. This
   teaching app has no accounts and takes no payments."** No checkout, payment form, plan selection state or sign-up.
7. **About** (`#about`): a fictional company story (mission, why SEC data, values such as "numbers with their
   sources"), a fictional team of 3–4 with roles and initials avatars, a fictional city, and contact
   `hello@example.com`. Label it: **"SEC Analytics and its team are fictional, created for a programming course."**
8. **FAQ** (`#faq`): native `<details>` items: where the data comes from (public SEC EDGAR, recorded snapshot in Demo
   mode); is it investment advice (no); does the AI need a key (yes, your own, optional); is it affiliated with the SEC
   (no); does it store my data (no accounts; the AI key stays in memory unless you opt in for the tab).
9. **Final call to action** and **footer**: "Open the app", links to the app routes and the GitHub repository
   `https://github.com/jfimbett/app-creator`, the disclaimer of O5, and "© 2026 SEC Analytics (fictional)".

**Screenshots for the hero and features:** capture them from the running demo app (fixture mode) with a Playwright
script `fe/scripts/capture-landing-shots.ts` (run by hand, not part of `verify`), in both themes, at 1440×900, into
`fe/public/landing/` (`app-dark.png`, `app-light.png`, plus one or two feature crops). The hero shows the shot that
matches the theme. Shots show recorded demo data only, no key, no personal data. Use `next/image` with explicit
sizes and meaningful `alt` text; keep each file under 400 KB.

**Metadata:** title "SEC Analytics: understand public companies from their SEC filings", a description, and Open
Graph title/description. No analytics, trackers, external fonts, external images or third-party scripts.

### 4.4 Routing

- Route groups: `fe/app/(marketing)/layout.tsx` + `page.tsx` for `/`; `fe/app/(app)/layout.tsx` with the current shell
  for `/app`, `/companies/...` and `/compare`. Moving files into a route group must not change those URLs.
- The root layout keeps `<html>`, `<body>`, the theme script, the skip link and global CSS.
- Update every internal link that meant "home" to `/app` (the brand link, not-found and error pages, breadcrumbs).
- Update the specs that start with `page.goto("/")` to `/app` where they test the app home. The `?source=` handling
  must keep working on `/app`.

### 4.5 The localStorage test change

The theme preference is the app's first `localStorage` entry. Change the three M5 assertions in
`m5-analyst.spec.ts` so they still prove the security property: the only allowed key is `sec-analytics.theme`, its
value is `"dark"` or `"light"`, and no `localStorage` value contains the test key `test-key-not-real-0000` or any
part of it. `lib/ai-key.test.ts` (no `localStorage.setItem` from the key holder) stays unchanged. Record the change and
the reason in `FOLLOWUPS.md` and the architecture decision log.

## 5. Architecture and files

| Path | Change |
|---|---|
| `fe/app/layout.tsx` | root only: html/body, theme script, skip link, globals |
| `fe/app/(app)/layout.tsx` | the current shell (header, main, app footer) |
| `fe/app/(app)/app/page.tsx` | the current home, redesigned (4.2) |
| `fe/app/(app)/companies/**`, `fe/app/(app)/compare/**` | moved unchanged, then restyled |
| `fe/app/(marketing)/layout.tsx`, `page.tsx` | landing page (4.3) |
| `fe/components/landing/*` | `LandingHeader`, `Hero`, `Features`, `HowItWorks`, `Testimonials`, `Pricing`, `About`, `Faq`, `LandingFooter`; content as typed constants in `fe/lib/landing-content.ts` so tests can check it |
| `fe/lib/theme.ts`, `fe/components/ThemeToggle.tsx` | theme (4.1) |
| `fe/app/globals.css` | tokens (type, spacing, radii, elevation, motion), both themes, updated contrast table |
| `fe/components/*` | restyling only |
| `fe/public/landing/*.png`, `fe/scripts/capture-landing-shots.ts` | screenshots |
| `fe/lib/contrast.ts` + test | WCAG relative-luminance contrast function used by the token test |
| `fe/e2e/m6-landing.spec.ts`, `fe/e2e/m6-theme.spec.ts` | section 7 |
| `be/` | **no change** |

Add to `milestones/architecture.md`: route groups and the `/app` move, the theme storage and pre-paint script, the
landing content as static constants, and the no-new-dependency rule for the overhaul.

## 6. Honesty and content rules

- Fictional content is always labelled fictional where it appears (reviews, team, company). Nothing imitates a real
  person, real company, real review site or the SEC's branding (no seal, no "official").
- Feature claims match the app at `m5`. No "AI-verified", "real-time", "bank-grade security" or invented numbers.
- No control that does nothing: every button and link goes somewhere real or opens something real.
- The disclaimer (not affiliated with the SEC; public EDGAR data; not investment advice) is on the landing page and in
  the app footer.

## 7. Tests and verification

Failing test first for logic. No test reaches the network.

**Vitest:**

- `lib/theme.test.ts`: missing or invalid stored value → `"dark"`; `writeTheme("light")` stores exactly
  `sec-analytics.theme` = `"light"`; `applyTheme` sets `data-theme`; storage that throws → dark, no crash.
- `lib/contrast.test.ts`: known answers from the WCAG 2.x formula: `#000000` vs `#ffffff` = 21:1, `#777777` vs
  `#ffffff` ≈ 4.48:1 (rounded to 2 decimals); then every text role in both themes ≥ 4.5:1 against `--bg`, `--panel`,
  `--panel-raised`, and border/focus/series roles ≥ 3:1 against `--bg` and `--panel` (token values read from
  `globals.css` or from one shared constants file, not retyped in the test).
- `lib/landing-content.test.ts`: the testimonials label, the pricing note and the About label are present; every
  pricing `href` is `/app` or an in-page anchor; no testimonial uses an organisation from a small deny list of real
  well-known firms you define in the test; contact emails end with `@example.com`.

**Playwright** (fixture mode):

1. `m6-landing.spec.ts`: `/` renders every section and the three labels (reviews, pricing, About) and the SEC
   disclaimer; "Open the app" goes to `/app` and the demo companies load; "See pricing" scrolls to `#pricing`; every
   link and button on the page has a real target (collect all `a[href]` and assert internal ones resolve with 200);
   the page has no `form`, no `input[type=password]`, no payment wording such as "card number"; it renders with the
   backend stopped (route `/api/**` to abort); the mobile menu opens, closes with Esc and returns focus; no request
   leaves `127.0.0.1`/`localhost`.
2. `m6-theme.spec.ts`: default is dark; the toggle switches `data-theme` to light and back; the choice survives a
   reload with no flash (check `data-theme` before hydration with `page.waitForFunction` on the first paint or by
   reading it in an `addInitScript`-free first `evaluate`); works from both the landing and the app header.
3. Screenshots, both themes, at 1440×900, 1366×900 and 390×844, into `fe/test-results/m6-<screen>-<theme>-<width>.png`
   for: landing (full page), `/app`, Apple Overview, Filings, the reader, Compare, the Analyst panel (not configured)
   and the AI settings dialog. At 390 px no sideways page scroll on any of them.
4. All M1–M5 journeys still pass (after the `/app` and localStorage edits of 4.4 and 4.5).

## 8. No-interview defaults

Do not interview the owner; this brief and the recorded decisions answer the product questions. Choose reversible
details yourself (copy wording, the fictional names, exact tier features, icon drawings, card layouts) and list the
important ones in the Handoff. Stop and record a blocker only for: money, a secret, personal data, new scope beyond
this brief, or a check that fails twice after two different fixes.

## 9. Slices

| # | Slice | Done when |
|---|---|---|
| 6.1 | Decisions O1–O6 recorded; route groups and the `/app` move; specs updated; no visual change yet | `npm run verify` exit 0 |
| 6.2 | Theme: `theme.ts`, pre-paint script, toggle, contrast function and tests, both themes fixed across every screen; the localStorage test change | Vitest and `m6-theme.spec.ts` pass; verify exit 0 |
| 6.3 | Interface overhaul of the app screens (4.2), screen by screen; look at screenshots of each in both themes after each screen | verify exit 0; screenshots inspected |
| 6.4 | Landing page (4.3) with captured screenshots and `m6-landing.spec.ts`, `landing-content.test.ts` | verify exit 0; screenshots inspected |
| 6.5 | Reviews in parallel: `ux-reviewer` (all screens, both themes, 390 px, keyboard), `code-reviewer`, `security-reviewer` (inline script, external requests, localStorage, the honesty rules of section 6); fix every finding or record why not | verify exit 0 after fixes |
| 6.6 | Launch video (section 9.1) | `brag.mp4` exists, plays, and was inspected |

Each slice ends with a local commit (`feat(m6): …`, `fix(m6): …`, `test(m6): …`, `docs(m6): …`).

### 9.1 Launch video with /brag

After the gate checks 1–4 of section 10 pass:

1. Start the demo (fixture mode) from the worktree on spare ports so the landing page and app are reachable.
2. Invoke the installed skill with the Skill tool: `brag:brag` with args `--tone polished --format landscape`. On Opus
   5.5 it hands off to brag-slim (it says so); follow it. It reads the project code; point it at the landing page and
   the app screens of SEC Analytics. Tools already on this machine: Node, Playwright's Chromium, ffmpeg. The skill
   asks before installing anything: in this autonomous run, do not install anything new; if something essential is
   missing, record it as a blocker and skip the video.
3. Creative constraints for the video: 15–25 s; real screens of the app (Overview chart, filings reader, Compare,
   the Analyst panel with mocked or no answer) and the landing hero; both themes may appear; **do not show the
   fictional testimonials or pricing as if real** (leave them out, or keep the "fictional"/"illustrative" label
   readable on screen); no key, no personal data, no real people; end card "SEC Analytics · Demo mode works offline"
   and the repository URL. Music and sound must be generated or bundled by the skill, not downloaded from an unknown
   source.
4. Output in `examples/sec-analytics/brag-output/` (run the skill with that as the working output location, or move
   its output there). Commit `brag.mp4` (if ≤ 25 MB; otherwise commit a ≤ 25 MB re-encode and say so), the brag plan
   and the share copy. Add `examples/sec-analytics/brag-output/work/` to `.gitignore`.
5. Look at stills from every scene before and after the render; check text fits, contrast, and that nothing in
   section 6 is broken. Watch the final file's duration with `ffprobe`.

## 10. Gate

1. `npm run check-toolkit` exits 0.
2. `npm run verify` exits 0 offline, with no key.
3. `npm run demo` works with no `.env`, no keys and no network: the landing page, then every M1–M5 journey; the
   Analyst panel shows "AI not configured".
4. Open and inspect every M6 screenshot (both themes, three widths); list what you checked and what you fixed.
5. The review findings of slice 6.5 are fixed or listed with reasons.
6. The video exists and was inspected, or its blocker is recorded.
7. Report separately: automated tests, browser checks, screenshots inspected by you, the owner's own look (pending),
   live SEC (not needed for M6; not run unless configured), live AI (still not verified, N1).

## 11. Records and documents

- `milestones/acceptance.md`: an "M6 — Polish and launch" section with criteria M6-AC1 … (one per item of 4.1–4.5,
  section 6, the video) and their statuses; screens table updated for both themes.
- `milestones/plan.md`: an M6 table with slices 6.1–6.6, statuses and the progress log; known problems.
- `milestones/architecture.md`: decision-log rows (section 5).
- `milestones/06-polish-and-launch/README.md` in the format of the M5 README (what it delivers, inspect at tag `m6`,
  rebuild from `m5`, Results left for the owner); `milestones/PROMPT-INDEX.md` M6 entry.
- `examples/sec-analytics/README.md`: the landing page, `/app`, the theme toggle, where the video is.
- `AI-USAGE.md`: design, generated code, reviews and fixes, the video.
- `PROGRESS.md`: "M6 complete (not pushed)", the worktree, branch, tag and SHAs.
- `runs/m6/m6-01-implement-main-session/`: `PROMPT.md` (step 0), `RESPONSE.md` marker (top-level session),
  `RESULT.json` (as for M5); a line in `runs/INDEX.md`.

## 12. Out of scope

- Accounts, sign-up, payments, checkout, newsletters or any form that sends data; analytics or trackers; hosting or
  deployment; new backend endpoints or data; new runtime dependencies; web fonts or external assets; a CMS; blog;
  internationalisation; changing AI, SEC or calculation behaviour.
- Do not edit `milestones/0[1-5]-*/PROMPT.md`, the toolkit (`.claude/`, `scripts/`, `scaffold/`, `AGENTS.md`,
  `CLAUDE.md`, `docs/TOOLKIT.md`), `GOAL.md` or the fixtures. Never read, create or print `.env`.

End your final message with the `AGENTS.md` Change report and then exactly this block:

```
## Handoff
Changes: <files created or changed, grouped by folder>
Verification evidence: <each command with its exit code and summary line; screenshots looked at (both themes, three widths); reviews and fixes; video path, duration and size>
Remaining findings: <blockers, defaults chosen (names, copy, tiers), deviations and why>
Next action: <one line, e.g. "Owner: watch the video and look at both themes, then say 'push m6'">
```
