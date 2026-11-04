import { expect, test } from "@playwright/test";

// The classroom demonstration as one journey, in offline fixture mode.
// Run by `npm run verify`; by hand: BASE_URL=http://127.0.0.1:3200 npx playwright test e2e/demo-journey.spec.ts
test("classroom journey: search by name, ticker and CIK; figures, chart and source labels", async ({ page }) => {
  test.setTimeout(60_000);
  const offHostRequests: string[] = [];
  const consoleErrors: string[] = [];
  page.on("request", (request) => {
    const host = new URL(request.url()).hostname;
    if (host !== "127.0.0.1" && host !== "localhost") offHostRequests.push(request.url());
  });
  page.on("console", (message) => {
    if (message.type() === "error") consoleErrors.push(`${message.text()} ${message.location().url}`);
  });

  await page.setViewportSize({ width: 1440, height: 900 });
  await page.goto("/");
  await expect(page.getByTestId("health-status")).toHaveAttribute("data-state", "ok", { timeout: 15_000 });
  await expect(page.getByText("RECORDED SEC DEMO").first()).toBeVisible();
  await expect(page.getByRole("link", { name: /Apple/ })).toBeVisible();
  await page.screenshot({ path: "test-results/demo-1-home-1440.png", fullPage: true });

  // Keyboard shortcut, search by name, choose the result.
  const search = page.getByRole("combobox");
  await page.keyboard.press("/");
  await expect(search).toBeFocused();
  await search.fill("micro");
  await expect(page.getByRole("option", { name: /MICROSOFT/ })).toBeVisible();
  await page.keyboard.press("ArrowDown");
  await page.keyboard.press("Enter");
  await expect(page).toHaveURL(/companies\/0000789019/);
  await expect(page.getByTestId("company-profile")).toContainText("0000789019");
  await expect(page.getByTestId("key-figures")).toBeVisible();
  await expect(page.getByTestId("overview-chart").locator("svg").first()).toBeVisible();
  await expect(page.getByText("RECORDED SEC DEMO").first()).toBeVisible();
  await page.screenshot({ path: "test-results/demo-2-microsoft-1440.png", fullPage: true });

  // Search by ticker.
  await search.fill("GOOGL");
  await page.getByRole("option", { name: /Alphabet/ }).click();
  await expect(page).toHaveURL(/companies\/0001652044/);
  await expect(page.getByTestId("key-figures")).toBeVisible();

  // Search by unpadded CIK.
  await search.fill("320193");
  await page.getByRole("option", { name: /Apple/ }).click();
  await expect(page).toHaveURL(/companies\/0000320193/);
  await expect(page.getByTestId("overview-chart").locator("svg").first()).toBeVisible();
  await page.screenshot({ path: "test-results/demo-3-apple-1440.png", fullPage: true });

  // Chart controls: range and series, with the data table following the range.
  const chart = page.getByTestId("overview-chart");
  await expect(chart.locator("tbody tr")).toHaveCount(20);
  await page.getByText("Last 5 years").click();
  await expect(chart.locator("tbody tr")).toHaveCount(5);
  const netIncome = page.getByRole("button", { name: "Net income" });
  await netIncome.click();
  await expect(netIncome).toHaveAttribute("aria-pressed", "false");
  await netIncome.click();
  await expect(netIncome).toHaveAttribute("aria-pressed", "true");

  // Hovering a value shows where it came from.
  await page.getByTestId("key-figures").getByRole("button").first().hover();
  const tip = page.getByTestId("provenance-tip");
  await expect(tip).toContainText("0000320193-26-000026");
  await expect(tip).toContainText("10-K");
  await page.screenshot({ path: "test-results/demo-4-apple-tooltip-1440.png" });
  await page.mouse.move(0, 0);

  // A company outside the snapshot is reported, not substituted.
  await search.fill("Tesla");
  await expect(page.getByText(/demo companies only/i).first()).toBeAttached();
  await expect(page.getByRole("option")).toHaveCount(0);

  expect(offHostRequests, "the browser must not call any other host").toEqual([]);
  expect(consoleErrors, "no console errors").toEqual([]);
});
