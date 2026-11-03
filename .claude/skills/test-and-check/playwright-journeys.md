# Browser journeys with Playwright, and the three kinds of evidence

Companion to [SKILL.md](SKILL.md). Replaces the starter's Python `browser_check.py`: the same checks now live in a
project-local Playwright test in TypeScript, run by `npm run verify`.

## Three kinds of evidence (never report one as another)

| Kind | What it proves | What it cannot prove | Report it as |
|---|---|---|---|
| **Automated tests** (pytest, Vitest) | the backend returns the right data, logic computes the right values, permissions hold | that the page draws, fits a phone, or is readable | `pytest: 42 passed; Vitest: 12 passed` |
| **Browser check** (Playwright in a real headless Chromium) | pages load without JavaScript errors or failed requests, the critical interactions work, no sideways scrolling, Tab reaches a control, nothing loads from the internet | whether it looks right or is understandable | `Playwright: 4 passed at 1366 px and 390 px` |
| **Visual inspection** (someone looks at the screenshots or the live page) | layout, overlap, legibility, whether a chart tells the truth at a glance | anything not on the screenshot | `Looked at: 4 screenshots by the assistant; owner's look pending` |

The assistant may inspect screenshots by opening the PNG files (if its model reads images). That is visual
inspection **by the assistant**, and it is still not the owner's look. The owner's own look at the running app is
the final visual check: ask for it, and record it in `<docs>/acceptance.md` as `checked by <role> on <date>`.

## How it is set up (nothing personal needed)

The browser tool is installed **by the project**, so every teammate, reviewer and CI run gets the same result:

- `@playwright/test` is a pinned dev dependency of `<frontend>/package.json` (scaffold: `1.64.1`).
- `npm run setup` installs Playwright's full Chromium (used in new headless mode via `channel: "chromium"`) into `.cache/ms-playwright` at the repository root
  (git-ignored), using `PLAYWRIGHT_BROWSERS_PATH=.cache/ms-playwright`. Nothing goes into a global cache.
- `<frontend>/playwright.config.ts` reads `BASE_URL`; tests live in `<frontend>/e2e/`; output goes to
  `<frontend>/test-results/` (git-ignored, emptied at the start of each run).
- `npm run verify` builds the app, starts backend and frontend on spare ports with the config's `demoEnv`
  (offline fixture mode), sets `BASE_URL`, `PLAYWRIGHT_BROWSERS_PATH` and `CI=1`, and runs the tests matching
  `smokeSpec` (default `e2e`, meaning every file in `e2e/`).

A browser tool configured only in one person's assistant (a browser extension, an MCP server) does not count as
the project's check. If one was used, say so in the change report.

## Run it by hand while developing

```bash
# terminal 1, repository root
npm run dev                       # or `npm run demo` for offline fixture mode

# terminal 2, in <frontend>
BASE_URL=http://127.0.0.1:3000 PLAYWRIGHT_BROWSERS_PATH=../../.cache/ms-playwright npx playwright test
npx playwright test e2e/journey.spec.ts --headed      # watch it (needs a full browser, see below)
npx playwright show-trace test-results/<test-folder>/trace.zip   # after a failure (trace kept on failure)
```

The relative `PLAYWRIGHT_BROWSERS_PATH` above assumes `<frontend>` is `app/frontend`; adjust the `../` count, or
use an absolute path. Windows PowerShell: `$env:BASE_URL="http://127.0.0.1:3000"; npx playwright test`.
`--headed` works with the same full Chromium that setup installs (`npx playwright install --no-shell chromium`);
the headless shell is not used (its screenshots hung on macOS in testing). If port 3000 is busy, `npm run dev` refuses it: set `FRONTEND_PORT` and
use that URL.

## A journey spec with the starter's checks (`<frontend>/e2e/journey.spec.ts`)

This file was run against a temporary copy of the scaffold (backend on 127.0.0.1:8765, `next dev` on 3765) with
the project-local browser: 4 passed, `tsc --noEmit` and `eslint` clean. Its screenshots were looked at by the
assistant: the layout fits at 390 px and the error state is readable. Adapt the selectors and the interaction to
your `<docs>/acceptance.md`.

```ts
import { expect, test, type Page } from "@playwright/test";

// One journey at the two required widths. Each test collects problems while it runs and fails on any of them.
// Screenshots go to test-results/screens/ for a person (or the assistant) to LOOK at; passing is not "looks right".
const sizes = [
  { name: "desktop", width: 1366, height: 900 },
  { name: "mobile", width: 390, height: 844 },
] as const;

const LOCAL_HOSTS = new Set(["127.0.0.1", "localhost"]);

function watchProblems(page: Page): string[] {
  const problems: string[] = [];
  page.on("pageerror", (error) => problems.push(`JavaScript error: ${error.message}`));
  page.on("console", (msg) => {
    // HTTP failures are reported by the "response" handler below, with their address.
    if (msg.type() === "error" && !msg.text().startsWith("Failed to load resource")) {
      problems.push(`console error: ${msg.text()}`);
    }
  });
  page.on("response", (res) => {
    if (res.status() >= 400) problems.push(`HTTP ${res.status()} ${res.url()}`);
  });
  page.on("request", (req) => {
    const url = new URL(req.url());
    if (url.protocol.startsWith("http") && !LOCAL_HOSTS.has(url.hostname)) {
      problems.push(`request to another host (the app must work offline): ${req.url()}`);
    }
  });
  return problems;
}

async function checkLayoutAndKeyboard(page: Page, width: number) {
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
  expect(overflow, `content is wider than ${width} px (sideways scrolling)`).toBeLessThanOrEqual(1);

  const controls = page.locator("a[href], button:not([disabled]), input, select, textarea");
  if ((await controls.count()) > 0) {
    await page.keyboard.press("Tab");
    const focused = await page.evaluate(() => document.activeElement?.tagName ?? "BODY");
    expect(focused, "the Tab key does not reach any control").not.toMatch(/^(BODY|HTML)$/);
  }
}

for (const size of sizes) {
  test.describe(`${size.name} ${size.width}px`, () => {
    test.use({ viewport: { width: size.width, height: size.height } });

    test("home: loads, reaches the backend, fits the screen, keyboard works", async ({ page }) => {
      const problems = watchProblems(page);
      await page.goto("/");

      await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
      await expect(page.getByTestId("health-status")).toHaveAttribute("data-state", "ok", { timeout: 15_000 });
      await checkLayoutAndKeyboard(page, size.width);

      // The critical interaction from acceptance.md, then what the user should see.
      await page.getByRole("button", { name: "Check again" }).click();
      await expect(page.getByTestId("health-status")).toContainText("OK");

      await page.screenshot({ path: `test-results/screens/home-${size.name}-${size.width}.png`, fullPage: true });
      expect(problems, problems.join("\n")).toEqual([]);
    });

    test("home: shows a helpful error when the backend fails", async ({ page }) => {
      // Simulate the failure in the browser only: no backend change, no real outage needed.
      await page.route("**/api/health", (route) =>
        route.fulfill({ status: 503, contentType: "application/json", body: '{"detail":"down"}' }),
      );
      await page.goto("/");

      const status = page.getByTestId("health-status");
      await expect(status).toHaveAttribute("data-state", "error");
      await expect(status).toContainText("Error");
      await page.screenshot({ path: `test-results/screens/home-error-${size.name}-${size.width}.png`, fullPage: true });
    });
  });
}
```

What each part catches (all ideas carried over from the starter's `browser_check.py`):

| Check | How | Typical cause when it fails |
|---|---|---|
| JavaScript errors | `pageerror`, console `error` messages | a component crashes on missing data |
| Failed requests | any response with status 400 or more | wrong `/api` path, backend error, missing file |
| Offline | requests to hosts other than 127.0.0.1/localhost | a font, script or chart library loaded from a CDN; the browser calling a third-party API directly |
| Fits the phone | `scrollWidth - innerWidth <= 1` at 390 px | a wide table or chart without a scroll container |
| Keyboard | Tab moves focus off `<body>` when controls exist | clickable `div`s instead of buttons and links |
| Error state | `page.route` makes `/api/...` answer 503 | no error message, or a crash, when the backend fails |
| Screenshots | full page at 1366 and 390 px | — (this is input for visual inspection, not a check) |

More patterns:

- **Expected error pages:** to check a 404 page, expect the status instead of collecting it as a problem:
  `const res = await page.goto("/no-such-page"); expect(res?.status()).toBe(404);`. With `next dev`, Next.js may
  show its developer overlay instead of your page; check error pages against the production build (`npm run
  verify`) and say which one you looked at.
- **Loading and empty states:** `page.route` can delay a response (`await new Promise(r => setTimeout(r, 1500))`
  before `route.fulfill(...)`) or return an empty list, then screenshot each state.
- **Chart tooltips:** scroll the chart into view, hover a point that has a value (not a gap), wait briefly, then
  screenshot: `const box = await chart.boundingBox(); await chart.hover({ position: { x: box!.width * 0.25, y:
  box!.height * 0.6 } });`.
- **Inner scroll containers:** `fullPage: true` captures the document; content scrolling inside its own `div` is
  cut off. Screenshot that element (`locator.screenshot()`) or make the container non-scrolling in the test.
- **Signed-in pages** (`add-accounts`): create a test user in the test (through an API the backend offers only in
  test or demo mode, or a fixture database), with a throw-away password from an environment variable set in the
  terminal. Never real accounts, never values from `.env`.
- **Dev indicator:** screenshots from `next dev` show Next.js's small "N" development badge in a corner; ignore it,
  or take the screenshots from `npm run verify` (production build).

## Data used by checks

- Run journeys against fixture data (`npm run demo` / the config's `demoEnv`) or a temporary database, never the
  owner's own local data. If you had to create records in it, delete them afterwards and say so.
- Do not depend on today's date or on live services: they make journeys flaky.

## Visual inspection: how to look at the screenshots

Open each PNG in `<frontend>/test-results/screens/` (and the `smoke-*` ones from the scaffold's smoke test) and
check, per width:

- [ ] Nothing overlaps or is cut off; text is not hidden behind other elements.
- [ ] Headings and numbers are readable; contrast looks sufficient (light and dark theme if both exist).
- [ ] At 390 px, the main action is visible without hunting; tables and charts scroll or adapt instead of
      shrinking to unreadable.
- [ ] Charts: axes labelled with units, gaps shown as gaps (not as zero), legend matches the colors.
- [ ] Loading, empty and error states say what happened and what to do.

Report what you looked at ("6 screenshots looked at by the assistant: ...") and what is still pending (the owner's
look). If nothing can show the screen (no image reading, browser install refused), give the owner a numbered
click-through with the expected result per step, and report the journey as **not verified** until they confirm.
