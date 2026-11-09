import { expect, type Page, test } from "@playwright/test";

// A mocked request can still be in flight when a test ends; drop the mocks quietly so it cannot fail the test.
test.afterEach(async ({ page }) => {
  await page.unrouteAll({ behavior: "ignoreErrors" });
});

// M1 browser journeys in offline fixture mode (brief §9). Run by `npm run verify`.
// By hand: BASE_URL=http://127.0.0.1:3200 npx playwright test e2e/m1-foundation.spec.ts
const APPLE = "/companies/0000320193";
const SNAPSHOT_LABEL = /RECORDED SEC DEMO · snapshot \d{4}-\d{2}-\d{2}/i;
const widths = [
  { width: 1440, height: 900 },
  { width: 1366, height: 900 },
  { width: 390, height: 844 },
];

/** Journey 6: fails the test if any request goes to a host other than this machine. */
function recordHosts(page: Page) {
  const offHost: string[] = [];
  page.on("request", (request) => {
    const host = new URL(request.url()).hostname;
    if (host !== "127.0.0.1" && host !== "localhost") offHost.push(request.url());
  });
  return () => expect(offHost, "no request may leave the machine").toEqual([]);
}

test("journey 1: home shows the badge, the demo-universe note and backend status (M1-AC1)", async ({ page }) => {
  const assertLocalOnly = recordHosts(page);
  await page.goto("/app");
  await expect(page.getByTestId("health-status")).toHaveAttribute("data-state", "ok", { timeout: 15_000 });
  await expect(page.getByTestId("health-status")).toContainText("OK");
  await expect(page.getByText(/RECORDED SEC DEMO/).first()).toBeVisible();
  await expect(page.getByText("Search covers the demo companies only: Apple, Microsoft, Alphabet")).toBeVisible();
  assertLocalOnly();
});

test("journey 2: `/` and Ctrl/Cmd-K focus search; aapl, down, Enter opens Apple (M1-AC2)", async ({ page }) => {
  const assertLocalOnly = recordHosts(page);
  await page.goto("/app");
  await expect(page.getByTestId("health-status")).toHaveAttribute("data-state", "ok", { timeout: 15_000 });
  const search = page.getByRole("combobox");

  await page.keyboard.press("/");
  await expect(search).toBeFocused();
  await search.fill("aapl");
  const option = page.getByRole("option", { name: "Apple Inc. · AAPL · CIK 0000320193" });
  await expect(option).toBeVisible();
  await page.keyboard.press("ArrowDown");
  await expect(option).toHaveAttribute("aria-selected", "true");
  await page.keyboard.press("Enter");
  await expect(page).toHaveURL(new RegExp(`${APPLE}$`));

  // Move focus away, then each shortcut must bring it back.
  await page.getByRole("heading", { level: 1 }).click();
  await expect(search).not.toBeFocused();
  await page.keyboard.press("Control+k");
  await expect(search).toBeFocused();
  await page.getByRole("heading", { level: 1 }).click();
  await page.keyboard.press("Meta+k");
  await expect(search).toBeFocused();
  assertLocalOnly();
});

test("journey 3: the company page shows profile, figures, chart, label and source tooltip (M1-AC4, M1-AC5)", async ({ page }) => {
  const assertLocalOnly = recordHosts(page);
  await page.goto(APPLE);

  const profile = page.getByTestId("company-profile");
  await expect(profile).toContainText("Apple Inc.");
  await expect(profile).toContainText("AAPL");
  await expect(profile).toContainText("0000320193");
  await expect(profile).toContainText("Nasdaq");
  await expect(profile).toContainText("3571");
  await expect(profile).toContainText("Electronic Computers");
  await expect(profile).toContainText("09-26");
  await expect(profile).toContainText("APPLE COMPUTER INC");

  // Expected values come from FX1 and FX2 in milestones/acceptance.md.
  const figures = page.getByTestId("key-figures");
  await expect(figures).toContainText("478,834");
  await expect(figures).toContainText("132,175");
  await expect(figures).toContainText("USD millions");
  await expect(figures).toContainText("FY2026 (ends 2026-09-26)");

  await expect(page.getByTestId("overview-chart").locator("svg").first()).toBeVisible();
  await expect(page.getByText(SNAPSHOT_LABEL).first()).toBeVisible();
  await expect(page.getByText("Values may reflect later restatements; not point-in-time.").first()).toBeVisible();

  await figures.getByRole("button").first().hover();
  const tip = page.getByTestId("provenance-tip");
  await expect(tip).toContainText("RevenueFromContractWithCustomerExcludingAssessedTax");
  await expect(tip).toContainText("0000320193-26-000026");
  assertLocalOnly();
});

test("journey 4: a company outside the snapshot is reported, not substituted (M1-AC3)", async ({ page }) => {
  await page.goto("/app");
  await page.getByRole("combobox").fill("tesla");
  await expect(page.getByText("No match in the demo universe (3 companies)").first()).toBeVisible();
  await expect(page.getByRole("option")).toHaveCount(0);
  await page.screenshot({ path: "test-results/m1-no-match-1440.png" });
});

test("journey 5: with the backend down the header says how to start it (M1-E1)", async ({ page }) => {
  await page.route("**/api/**", (route) => route.abort());
  await page.goto("/app");
  const status = page.getByTestId("health-status");
  await expect(status).toHaveText("Backend not reachable: start it with npm run demo", { timeout: 15_000 });
  await expect(status).toBeVisible();
  await expect(page.locator("body")).not.toContainText("Traceback");
  await page.screenshot({ path: "test-results/m1-backend-down-1440.png" });
  await page.setViewportSize({ width: 390, height: 844 });
  expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(390);
  await page.screenshot({ path: "test-results/m1-backend-down-390.png" });
});

for (const { width, height } of widths) {
  test(`journey 7: home and Apple fit at ${width} px, with screenshots (V1, V2)`, async ({ page }) => {
    await page.setViewportSize({ width, height });
    for (const [screen, url] of [["home", "/app"], ["apple", APPLE]] as const) {
      await page.goto(url);
      await expect(page.getByTestId("health-status")).toHaveAttribute("data-state", "ok", { timeout: 15_000 });
      if (screen === "apple") await expect(page.getByTestId("overview-chart").locator("svg").first()).toBeVisible();
      const scrollWidth = await page.evaluate(() => document.documentElement.scrollWidth);
      expect(scrollWidth, `${screen} must not scroll sideways`).toBeLessThanOrEqual(width);
      await page.screenshot({ path: `test-results/m1-${screen}-${width}.png`, fullPage: true });
    }
  });
}
