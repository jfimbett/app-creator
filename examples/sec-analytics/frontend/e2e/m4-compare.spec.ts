import { expect, type Page, test } from "@playwright/test";

// A mocked request can still be in flight when a test ends; drop the mocks quietly so it cannot fail the test.
test.afterEach(async ({ page }) => {
  await page.unrouteAll({ behavior: "ignoreErrors" });
});

// M4 browser journeys in offline fixture mode (brief §9). Run by `npm run verify`.
const COMPARE_THREE = "/compare?ciks=0000320193,0000789019,0001652044&metrics=revenue,net_margin&years=10&index=none&source=demo";
const CSV_HEADER = "company,ticker,cik,fiscal_year_label,fiscal_year_end,period_start,period_end,metric,value,unit,kind,indexed,source_concept,accession,data_source";
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

async function addCompany(page: Page, query: string, ticker: string) {
  const box = page.getByTestId("compare-add");
  await box.fill(query);
  await page.getByRole("option", { name: new RegExp(ticker) }).first().click();
  await expect(page.locator(`[data-testid="company-chip"]`, { hasText: ticker })).toBeVisible();
}

test("header → Compare, add AAPL, MSFT and GOOGL: table and chart by fiscal year (M4-AC1, M4-AC3)", async ({ page }) => {
  const assertLocalOnly = recordHosts(page);
  await page.goto("/");
  await page.getByRole("navigation", { name: "Main" }).getByRole("link", { name: "Compare" }).click();
  await expect(page).toHaveURL(/\/compare$/);
  await expect(page.getByText("Add at least 2 companies to compare")).toBeVisible();
  await expect(page.getByTestId("compare-add")).toBeFocused();

  await addCompany(page, "aapl", "AAPL");
  await expect(page.getByText("Add at least 2 companies to compare")).toBeVisible();
  await addCompany(page, "msft", "MSFT");
  await addCompany(page, "googl", "GOOGL");
  await expect(page).toHaveURL(/ciks=0000320193%2C0000789019%2C0001652044/);

  const table = page.getByTestId("compare-table");
  await expect(table).toBeVisible();
  await expect(page.getByTestId("compare-line")).toHaveCount(6);
  // FX1 and FX3 in milestones/acceptance.md, in USD millions, each under its own fiscal year.
  const appleRevenue = page.locator('[data-testid="compare-line"][data-cik="0000320193"][data-metric="revenue"]');
  await expect(appleRevenue).toContainText("478,834");
  await expect(page.locator('[data-testid="compare-line"][data-cik="0000789019"][data-metric="revenue"]')).toContainText("331,839");
  await expect(page.getByTestId("compare-chart")).toBeVisible();
  await expect(page.getByTestId("compare-chart").locator(".recharts-line")).toHaveCount(3);

  // M4-AC3: the companies' own year-ends, the warning, and each cell's own period end.
  await expect(page.getByTestId("fiscal-year-ends")).toHaveText("AAPL: FY ends 09-26 · MSFT: FY ends 06-30 · GOOGL: FY ends 12-31");
  await expect(page.getByTestId("chart-not-aligned")).toContainText("Fiscal years are not aligned");
  await expect(page.locator('[data-testid="compare-warning"][data-code="fiscal_years_not_aligned"]')).toHaveText(/Fiscal years are not aligned/);
  const cell = appleRevenue.locator('[data-testid="compare-cell"]').last();
  await expect(cell).toHaveAttribute("data-period-end", "2026-09-26");
  await expect(cell).toHaveAttribute("title", /AAPL FY2026, 2025-09-28 – 2026-09-26: 478,834 \(reported\)/);
  assertLocalOnly();
});

test("removing down to one company clears the comparison (M4-AC2)", async ({ page }) => {
  await page.goto(COMPARE_THREE);
  await expect(page.getByTestId("compare-table")).toBeVisible();
  await page.getByRole("button", { name: "Remove GOOGL" }).click();
  await expect(page.getByTestId("compare-line")).toHaveCount(4);
  await page.getByRole("button", { name: "Remove MSFT" }).click();
  await expect(page.getByTestId("company-chip")).toHaveCount(1);
  await expect(page.getByText("Add at least 2 companies to compare")).toBeVisible();
  await expect(page.getByTestId("compare-table")).toHaveCount(0);
  await expect(page.getByTestId("compare-chart")).toHaveCount(0);
});

test("a company already present is ignored with a message (M4-E3)", async ({ page }) => {
  await page.goto(COMPARE_THREE);
  await page.getByTestId("compare-add").fill("aapl");
  await page.getByRole("option", { name: /AAPL/ }).first().click();
  await expect(page.getByTestId("compare-message")).toHaveText("Already in the comparison");
  await expect(page.getByTestId("company-chip")).toHaveCount(3);
});

test("a fifth company is refused with the rule (M4-AC2, mocked search)", async ({ page }) => {
  // The demo has three companies (Q19): a fourth and fifth come from a mocked search; the comparison call is mocked too.
  await page.route("**/api/companies/search*", async (route) => {
    const q = new URL(route.request().url()).searchParams.get("q") ?? "";
    const results = q.startsWith("e")
      ? [{ cik: "0000000905", ticker: "EFIF", name: "Example Five", match: "ticker" }]
      : [{ cik: "0000000904", ticker: "EFOU", name: "Example Four", match: "ticker" }];
    await route.fulfill({ json: { query: q, results, source: { mode: "demo", label: "SYNTHETIC TEST DATA", retrieved_at: null, snapshot_date: null, source_urls: [] }, universe_note: "" } });
  });
  await page.route("**/api/compare?*", (route) => route.fulfill({ status: 404, json: { error: { code: "company_not_found", message: "not in the demo", details: null, reference: null } } }));
  await page.goto(COMPARE_THREE);
  await page.getByTestId("compare-add").fill("four");
  await page.getByRole("option", { name: /EFOU/ }).click();
  await expect(page.getByTestId("company-chip")).toHaveCount(4);
  await page.getByTestId("compare-add").fill("efive");
  await page.getByRole("option", { name: /EFIF/ }).click();
  await expect(page.getByTestId("compare-message")).toHaveText("Compare 2–4 companies");
  await expect(page.getByTestId("company-chip")).toHaveCount(4);
});

test("index revenue: INDEXED badge, base label with each year-end, ratios not indexed (M4-AC5)", async ({ page }) => {
  await page.goto(COMPARE_THREE.replace("ciks=0000320193,0000789019,0001652044", "ciks=0000320193,0000789019"));
  await page.getByTestId("index-toggle").click(); // the toggle changes once the URL does
    await expect(page.getByTestId("index-toggle")).toBeChecked();
  await expect(page).toHaveURL(/index=first_common_year/);
  await expect(page.getByTestId("indexed-badge")).toHaveCount(2);
  await expect(page.getByTestId("chart-title")).toHaveText("Revenue, index = 100 at FY2017 (AAPL ends 2017-09-30; MSFT ends 2017-06-30)");
  await expect(page.getByTestId("chart-indexed-badge")).toHaveText("INDEXED");
  // FX16 in milestones/acceptance.md.
  await expect(page.locator('[data-testid="compare-line"][data-cik="0000320193"][data-metric="revenue"]')).toContainText("208.9");
  await expect(page.locator('[data-testid="compare-line"][data-cik="0000789019"][data-metric="revenue"]')).toContainText("343.6");
  await expect(page.getByTestId("not-indexed")).toHaveCount(2);
  await expect(page.getByTestId("not-indexed").first()).toHaveText("not indexed: ratio");

  await page.locator('button[data-metric="revenue"]').click();
  await expect(page.getByTestId("index-unavailable")).toHaveText("Indexing applies to revenue, operating cash flow and FCF");
  await expect(page.getByTestId("index-toggle")).toBeDisabled();
});

test("Export CSV downloads exactly the shown data points (M4-AC6)", async ({ page }) => {
  await page.goto(COMPARE_THREE);
  const table = page.getByTestId("compare-table");
  await expect(table).toBeVisible();
  const cells = await page.getByTestId("compare-cell").count();
  expect(cells).toBe(Number(await table.getAttribute("data-points")));
  await page.evaluate(() => {
    const original = URL.createObjectURL.bind(URL);
    URL.createObjectURL = (blob: Blob) => {
      (window as unknown as { __lastDownload: Blob }).__lastDownload = blob;
      return original(blob);
    };
  });
  const [download] = await Promise.all([page.waitForEvent("download"), page.getByTestId("export-csv").click()]);
  expect(download.suggestedFilename()).toMatch(/^sec-analytics-compare-AAPL-MSFT-GOOGL-\d{4}-\d{2}-\d{2}\.csv$/);
  // The bytes the page handed to the browser as the download. Not download.path(): on this Windows machine the
  // system cancels Chromium downloads into the Documents folder (where test-results lives), so the file never lands.
  const text = await page.evaluate(() => (window as unknown as { __lastDownload: Blob }).__lastDownload.text());
  const lines = text.split("\r\n").filter(Boolean);
  expect(lines[0]).toBe(CSV_HEADER);
  expect(lines.length - 1).toBe(cells);
  expect(lines[1]).toMatch(/^Apple Inc\.,AAPL,0000320193,FY2017,/);
});

test("reloading restores the same comparison from the URL", async ({ page }) => {
  await page.goto(COMPARE_THREE);
  await page.locator('button[data-metric="fcf"]').click();
  await expect(page).toHaveURL(/metrics=revenue%2Cnet_margin%2Cfcf/);
  await expect(page.getByTestId("compare-line")).toHaveCount(9);
  await page.reload();
  await expect(page.getByTestId("company-chip")).toHaveCount(3);
  await expect(page.getByTestId("compare-line")).toHaveCount(9);
  await expect(page.locator('button[data-metric="fcf"]')).toHaveAttribute("aria-pressed", "true");
});

test("different currencies: warning and no shared money axis (M4-AC4, mocked backend)", async ({ page }) => {
  await page.route("**/api/compare?*", async (route) => {
    const response = await route.fetch();
    const body = await response.json();
    const euro = body.companies[1].cik;
    await route.fulfill({
      response,
      json: {
        ...body,
        companies: body.companies.map((c: { cik: string }) => (c.cik === euro ? { ...c, currency: "EUR" } : c)),
        rows: body.rows.map((r: { cik: string; metric_id: string }) => (r.cik === euro && r.metric_id === "revenue" ? { ...r, unit: "EUR" } : r)),
        warnings: [...body.warnings, { code: "currencies_differ", message: "Different reporting currencies (USD, EUR): not converted" }],
      },
    });
  });
  await page.goto(COMPARE_THREE.replace(",0001652044", ""));
  await expect(page.locator('[data-testid="compare-warning"][data-code="currencies_differ"]')).toHaveText(/Different reporting currencies \(USD, EUR\): not converted/);
  await expect(page.getByTestId("chart-blocked")).toBeVisible();
  await expect(page.locator('[data-testid="compare-line"][data-metric="revenue"]').nth(1)).toContainText("EUR millions");
  await page.getByRole("tab", { name: "Net margin" }).click();
  await expect(page.getByTestId("chart-blocked")).toHaveCount(0);
  await expect(page.getByTestId("compare-chart").locator(".recharts-line")).toHaveCount(2);
});

for (const size of widths) {
  test(`screenshots at ${size.width} px: table, trend chart, indexed view; no sideways page scroll`, async ({ page }) => {
    await page.setViewportSize(size);
    await page.goto(COMPARE_THREE);
    await expect(page.getByTestId("compare-table")).toBeVisible();
    await expect(page.getByTestId("compare-chart").locator(".recharts-line").first()).toBeVisible();
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
    expect(overflow).toBeLessThanOrEqual(0);
    await page.screenshot({ path: `test-results/m4-table-${size.width}.png`, fullPage: true });
    await page.getByTestId("compare-chart").scrollIntoViewIfNeeded();
    await page.screenshot({ path: `test-results/m4-trend-${size.width}.png` });
    await page.getByTestId("index-toggle").click(); // the toggle changes once the URL does
    await expect(page.getByTestId("index-toggle")).toBeChecked();
    await expect(page.getByTestId("chart-indexed-badge")).toBeVisible();
    await page.screenshot({ path: `test-results/m4-indexed-${size.width}.png`, fullPage: true });
  });
}
