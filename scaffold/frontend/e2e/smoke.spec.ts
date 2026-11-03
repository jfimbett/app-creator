import { expect, test } from "@playwright/test";

// The smallest end-to-end journey: the page loads, reaches the backend through /api, and says OK.
// Screenshots at a laptop and a phone size go to test-results/ for a person to look at.
const sizes = [
  { name: "desktop", width: 1366, height: 900 },
  { name: "mobile", width: 390, height: 844 },
];

for (const size of sizes) {
  test(`home page shows the backend as OK (${size.width}x${size.height})`, async ({ page }) => {
    await page.setViewportSize({ width: size.width, height: size.height });
    await page.goto("/");

    await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
    const status = page.getByTestId("health-status");
    await expect(status).toHaveAttribute("data-state", "ok", { timeout: 15_000 });
    await expect(status).toContainText("OK");

    await page.screenshot({ path: `test-results/smoke-${size.name}-${size.width}x${size.height}.png`, fullPage: true });
  });
}
