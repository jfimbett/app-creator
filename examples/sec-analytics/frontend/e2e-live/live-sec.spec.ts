import { expect, test } from "@playwright/test";

// Live SEC journey, by hand only: never part of `npm run verify`, which must work offline.
// Needs `npm run dev` with SEC_USER_AGENT configured. From this frontend folder:
//   BASE_URL=http://127.0.0.1:3000 npx playwright test --config playwright.live.config.ts
// It reaches SEC through the app's backend. The browser itself must talk only to this machine.
test("Live: look up NVIDIA by ticker, read its statements and explorer, then return to Demo", async ({ page }) => {
  test.setTimeout(180_000);
  const offHost: string[] = [];
  page.on("request", (request) => {
    const host = new URL(request.url()).hostname;
    if (host !== "127.0.0.1" && host !== "localhost") offHost.push(request.url());
  });

  await page.setViewportSize({ width: 1440, height: 900 });
  await page.goto("/");
  const selector = page.getByTestId("mode-selector");
  await expect(selector.getByRole("radio", { name: "Demo" })).toBeChecked();
  await selector.getByText("Live", { exact: true }).click();
  await expect(page).toHaveURL(/source=live/);
  await expect(page.getByText("LIVE", { exact: true }).first()).toBeVisible();

  const search = page.getByRole("combobox");
  await search.fill("NVDA");
  const option = page.getByRole("option", { name: /NVIDIA.*NVDA.*0001045810/ });
  await expect(option).toBeVisible({ timeout: 45_000 });
  await option.click();
  await expect(page).toHaveURL(/companies\/0001045810\?source=live/);

  await expect(page.getByRole("heading", { level: 1 })).toContainText("NVDA", { timeout: 45_000 });
  await expect(page.getByTestId("company-profile")).toContainText("0001045810");
  await expect(page.locator("#income-statement").getByTestId("statement-table")).toBeVisible({ timeout: 60_000 });
  await expect(page.getByText(/^(LIVE|CACHED) · retrieved /).first()).toBeVisible();
  await expect(page.getByText(/RECORDED SEC DEMO/)).toHaveCount(0);
  await expect(page.getByTestId("key-figures").getByRole("button").first()).toBeVisible();

  const income = page.locator("#income-statement");
  await income.getByRole("row", { name: /^Revenue/ }).getByRole("button").last().hover();
  await expect(page.getByTestId("provenance-tip")).toContainText("us-gaap");
  await page.mouse.move(0, 0);

  const explorer = page.locator("#explorer");
  await explorer.getByRole("button", { name: "Free cash flow (FCF)", exact: true }).click();
  await expect(explorer.getByTestId("metric-chart")).toHaveCount(3);
  await page.screenshot({ path: "test-results/live-nvda-1440.png", fullPage: true });

  // Search by name and by CIK, also live, and a CIK outside the ticker file can be offered.
  await search.fill("microsoft");
  await expect(page.getByRole("option", { name: /MICROSOFT/i }).first()).toBeVisible({ timeout: 45_000 });
  await search.fill("320193");
  await expect(page.getByRole("option", { name: /Apple/i })).toBeVisible({ timeout: 45_000 });
  await search.fill("");

  await selector.getByText("Demo", { exact: true }).click();
  await expect(page).not.toHaveURL(/source=live/);
  await expect(page.getByText(/not in the demo snapshot/i).first()).toBeVisible({ timeout: 15_000 });

  expect(offHost, "the browser must not call SEC or any other host").toEqual([]);
});
