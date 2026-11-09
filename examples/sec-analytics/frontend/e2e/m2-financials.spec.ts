import { expect, type Page, test } from "@playwright/test";

// A mocked request can still be in flight when a test ends; drop the mocks quietly so it cannot fail the test.
test.afterEach(async ({ page }) => {
  await page.unrouteAll({ behavior: "ignoreErrors" });
});

// M2 browser journeys in offline fixture mode (brief §9). Run by `npm run verify`.
// Tests named "(mocked backend)" use page.route for states the fixture backend cannot produce.
const APPLE = "/companies/0000320193";
const MICROSOFT = "/companies/0000789019";
const NOT_CONFIGURED = "Live SEC data is not configured: set SEC_USER_AGENT (see .env.example and docs/SETUP.md)";
const widths = [
  { width: 1440, height: 900 },
  { width: 1366, height: 900 },
  { width: 390, height: 844 },
];

function recordHosts(page: Page) {
  const offHost: string[] = [];
  page.on("request", (request) => {
    const host = new URL(request.url()).hostname;
    if (host !== "127.0.0.1" && host !== "localhost") offHost.push(request.url());
  });
  return () => expect(offHost, "no request may leave the machine").toEqual([]);
}

/** Answer /api/meta as if the app were started with `npm run dev`. */
async function offerLive(page: Page) {
  await page.route("**/api/meta", async (route) => {
    const response = await route.fetch();
    await route.fulfill({ response, json: { ...(await response.json()), data_mode: "live", live_available: true, live_configured: true } });
  });
}

test("statements show annual columns with fiscal dates, units and the restatement note (M2-AC4)", async ({ page }) => {
  const assertLocalOnly = recordHosts(page);
  await page.goto(APPLE);
  for (const name of ["Income statement (summary)", "Balance sheet (summary)", "Cash flow (summary)", "Ratios"]) {
    await expect(page.getByRole("heading", { name, exact: true })).toBeVisible();
  }
  const income = page.getByTestId("statement-table").first();
  await expect(income.locator("thead th")).toHaveCount(11);
  await expect(income.locator("thead th").last()).toHaveText("FY2026 (ends 2026-09-26)");
  await expect(page.getByTestId("statement-note").first()).toHaveText("Values may reflect later restatements; not point-in-time.");
  await expect(page.getByText("normalized summary from SEC Company Facts, not the complete filed statement").first()).toBeVisible();
  // FX1 and FX6 in milestones/acceptance.md, in USD millions.
  await expect(income).toContainText("478,834");
  await expect(page.locator("#cash-flow")).toContainText("136,056");
  await expect(income).toContainText("USD millions");

  await page.getByRole("group", { name: "Years shown" }).getByText("5", { exact: true }).click();
  await expect(income.locator("thead th")).toHaveCount(6);
  assertLocalOnly();
});

test("key figures say REPORTED or DERIVED and show ratios (M2 key strip)", async ({ page }) => {
  await page.goto(APPLE);
  const figures = page.getByTestId("key-figures");
  await expect(figures).toContainText("REPORTED");
  await expect(figures).toContainText("DERIVED");
  // FX5, FX7 and FX9 in milestones/acceptance.md.
  await expect(figures).toContainText("27.6%");
  await expect(figures).toContainText("0.71×");
  await expect(figures).toContainText("15.1%");
});

test("unavailable values say so, never 0 or blank", async ({ page }) => {
  await page.goto(MICROSOFT);
  const income = page.locator("#income-statement");
  await expect(income).toContainText("unavailable");
  await expect(page.locator("#cash-flow")).toContainText("MISSING · no mapped D&A concept");
  const ebitda = income.getByRole("row", { name: /EBITDA/ }).getByRole("button").last();
  await ebitda.hover();
  const tip = page.getByTestId("provenance-tip");
  await expect(tip).toContainText("D&A missing");
  await expect(tip).toContainText("EBIT + D&A");
});

test("explorer: net margin and FCF as stacked charts with a zero line and a data table (M2-AC5)", async ({ page }) => {
  await page.goto(APPLE);
  const explorer = page.locator("#explorer");
  await explorer.scrollIntoViewIfNeeded();
  await expect(explorer.getByRole("button", { name: "Net margin", exact: true })).toHaveAttribute("aria-pressed", "true");
  await explorer.getByRole("button", { name: "Revenue", exact: true }).click();
  await explorer.getByRole("button", { name: "Free cash flow (FCF)", exact: true }).click();

  const charts = explorer.getByTestId("metric-chart");
  await expect(charts).toHaveCount(2);
  for (const metric of ["net_margin", "fcf"]) {
    const chart = explorer.locator(`[data-metric="${metric}"]`);
    await expect(chart.locator("svg.recharts-surface").first()).toBeVisible();
    await expect(chart.locator(".recharts-reference-line").first()).toBeAttached();
  }

  await explorer.getByRole("button", { name: "Show data" }).click();
  const data = explorer.getByTestId("explorer-data");
  await expect(data).toContainText("27.6%");
  await expect(data).toContainText("136,056");
});

test("explorer lists a missing year as MISSING, not 0 (M2-AC5)", async ({ page }) => {
  await page.goto(MICROSOFT);
  const explorer = page.locator("#explorer");
  await explorer.getByRole("button", { name: "Depreciation and amortization (D&A)", exact: true }).click();
  await explorer.getByRole("button", { name: "Show data" }).click();
  await expect(explorer.getByTestId("explorer-data")).toContainText("MISSING · no mapped D&A concept");
});

test("tooltips: reported shows full provenance, derived shows formula and inputs, also on keyboard focus (M2-AC6)", async ({ page }) => {
  await page.goto(APPLE);
  const income = page.locator("#income-statement");
  await income.getByRole("row", { name: /^Revenue/ }).getByRole("button").last().hover();
  const tip = page.getByTestId("provenance-tip");
  for (const text of ["RevenueFromContractWithCustomerExcludingAssessedTax", "us-gaap", "USD", "2025-09-28 – 2026-09-26", "10-K", "0000320193-26-000026", "2026-11-03"]) {
    await expect(tip).toContainText(text);
  }
  await expect(tip.getByRole("link", { name: "SEC Company Facts" })).toHaveAttribute("href", "https://data.sec.gov/api/xbrl/companyfacts/CIK0000320193.json");
  await page.mouse.move(0, 0);
  await expect(tip).toHaveCount(0);

  await page.locator("#ratios").getByRole("row", { name: /Net margin/ }).getByRole("button").last().focus();
  await expect(tip).toContainText("net income ÷ revenue");
  await expect(tip).toContainText("net_income");
  await expect(tip).toContainText("132,175,000,000 USD");
});

test("demo run has no mode selector (M1 behaviour kept)", async ({ page }) => {
  await page.goto("/app");
  await expect(page.getByTestId("health-status")).toHaveAttribute("data-state", "ok", { timeout: 15_000 });
  await expect(page.getByTestId("mode-selector")).toHaveCount(0);
  await expect(page.getByText("RECORDED SEC DEMO").first()).toBeVisible();
});

test("selector is explicit and starts on Demo; Live without a contact shows the exact message, Demo still works (M2-AC2, mocked backend)", async ({ page }) => {
  await offerLive(page);
  await page.route("**/api/companies/search?*source=live*", (route) =>
    route.fulfill({
      status: 503,
      json: { error: { code: "sec_contact_not_configured", message: NOT_CONFIGURED, details: { setting: "SEC_USER_AGENT" }, reference: null } },
    }),
  );
  await page.goto("/app");
  const selector = page.getByTestId("mode-selector");
  await expect(selector.getByRole("radio", { name: "Demo" })).toBeChecked();
  await selector.getByText("Live", { exact: true }).click();
  await expect(page).toHaveURL(/source=live/);
  await expect(selector.getByRole("radio", { name: "Live" })).toBeChecked();
  await expect(page.getByTestId("universe-note")).toHaveText("Live search covers SEC filers listed in the SEC ticker file; other filers can be opened by CIK.");

  const search = page.getByRole("combobox");
  await search.fill("NVDA");
  await expect(page.getByText(NOT_CONFIGURED).first()).toBeVisible();

  await selector.getByText("Demo", { exact: true }).click();
  await expect(page).not.toHaveURL(/source=live/);
  await search.fill("aapl");
  await expect(page.getByRole("option", { name: /Apple/ })).toBeVisible();
});

test("SEC down: the error panel offers demo data and the mode stays Live until pressed (M2-AC3, mocked backend)", async ({ page }) => {
  await offerLive(page);
  await page.route(/\/api\/companies\/\d+[^?]*\?.*source=live/, (route) =>
    route.fulfill({
      status: 502,
      json: { error: { code: "sec_unavailable", message: "SEC is unavailable right now", details: null, reference: null } },
    }),
  );
  await page.goto(`${APPLE}?source=live`);
  const panel = page.getByTestId("live-error").first();
  await expect(panel).toContainText("SEC is unavailable right now");
  await expect(page.getByText("RECORDED SEC DEMO", { exact: false })).toHaveCount(0);
  await expect(page).toHaveURL(/source=live/);
  await expect(page.getByRole("radio", { name: "Live" })).toBeChecked();

  await panel.getByRole("button", { name: "Use recorded demo data" }).click();
  await expect(page).not.toHaveURL(/source=live/);
  await expect(page.getByTestId("key-figures")).toContainText("478,834");
  await expect(page.getByText(/RECORDED SEC DEMO · snapshot/).first()).toBeVisible();
});

for (const [code, message] of [
  ["sec_rate_limited", "SEC is limiting requests; try again in 7 s"],
  ["sec_refused", "SEC refused the request (403). The app does not retry refused requests."],
] as const) {
  test(`${code} is explained in words (mocked backend)`, async ({ page }) => {
    await offerLive(page);
    await page.route(/\/api\/companies\/\d+[^?]*\?.*source=live/, (route) =>
      route.fulfill({ status: code === "sec_refused" ? 502 : 503, json: { error: { code, message, details: null, reference: null } } }),
    );
    await page.goto(`${APPLE}?source=live`);
    await expect(page.getByTestId("live-error").first()).toContainText(message);
  });
}

test("live and cached labels are distinct from demo (mocked backend)", async ({ page }) => {
  await offerLive(page);
  await page.route(/\/api\/companies\/0000320193\?.*source=live/, async (route) => {
    const response = await route.fetch({ url: route.request().url().replace("source=live", "") });
    const body = await response.json();
    await route.fulfill({ json: { ...body, source: { mode: "cached", label: "CACHED · retrieved 2026-11-03", retrieved_at: "2026-11-03T18:00:00Z", snapshot_date: null, source_urls: [] } } });
  });
  await page.route(/\/api\/companies\/0000320193\/(overview|financials|metrics)\?.*source=live/, async (route) => {
    const response = await route.fetch({ url: route.request().url().replace("source=live", "source=demo") });
    const body = await response.json();
    await route.fulfill({ json: { ...body, source: { mode: "live", label: "LIVE · retrieved 2026-11-03 18:00 UTC", retrieved_at: "2026-11-03T18:00:00Z", snapshot_date: null, source_urls: [] } } });
  });
  await page.goto(`${APPLE}?source=live`);
  await expect(page.getByText("CACHED · retrieved 2026-11-03").first()).toBeVisible();
  await expect(page.getByText("LIVE · retrieved 2026-11-03 18:00 UTC").first()).toBeVisible();
  await expect(page.getByText(/RECORDED SEC DEMO/)).toHaveCount(0);
});

for (const { width, height } of widths) {
  test(`statements and explorer fit at ${width} px, with screenshots`, async ({ page }) => {
    const assertLocalOnly = recordHosts(page);
    await page.setViewportSize({ width, height });
    await page.goto(APPLE);
    await expect(page.locator("#ratios").getByTestId("statement-table")).toBeVisible();
    await expect(page.locator("#explorer").getByTestId("metric-chart").first().locator("svg.recharts-surface").first()).toBeVisible();
    expect(await page.evaluate(() => document.documentElement.scrollWidth), "no sideways page scroll").toBeLessThanOrEqual(width);
    await page.locator("#income-statement").screenshot({ path: `test-results/m2-income-${width}.png` });
    await page.locator("#ratios").screenshot({ path: `test-results/m2-ratios-${width}.png` });
    await page.locator("#explorer").screenshot({ path: `test-results/m2-explorer-${width}.png` });
    await page.screenshot({ path: `test-results/m2-apple-${width}.png`, fullPage: true });
    assertLocalOnly();
  });
}
