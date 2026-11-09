import { expect, type Page, test } from "@playwright/test";

// M6 screenshots (brief §7.3): every screen in both themes at 1440, 1366 and 390 px, into
// test-results/m6-<screen>-<theme>-<width>.png for inspection. Offline fixture mode; no key, no AI calls.
// Each run also asserts there is no sideways page scroll (wide tables scroll inside their own box).
const APPLE = "/companies/0000320193";
const READER = `${APPLE}/filings/0000320193-26-000026`;
const COMPARE = "/compare?ciks=0000320193,0000789019,0001652044&metrics=revenue,net_margin&years=10&index=none";
const widths = [
  { width: 1440, height: 900 },
  { width: 1366, height: 900 },
  { width: 390, height: 844 },
];

type Screen = { name: string; url: string; ready: (page: Page) => Promise<void>; fullPage?: boolean };

const SCREENS: Screen[] = [
  { name: "landing", url: "/", ready: async (page) => expect(page.locator("h1").first()).toBeVisible(), fullPage: true },
  { name: "app", url: "/app", ready: async (page) => expect(page.getByRole("link", { name: /AAPL/ }).first()).toBeVisible(), fullPage: true },
  { name: "overview", url: APPLE, ready: async (page) => expect(page.getByTestId("overview-chart").locator("svg").first()).toBeVisible(), fullPage: true },
  { name: "filings", url: `${APPLE}/filings`, ready: async (page) => expect(page.getByText("0000320193-26-000026").first()).toBeVisible() },
  { name: "reader", url: READER, ready: async (page) => expect(page.getByTestId("filing-reader")).toContainText("FORM 10-K") },
  { name: "compare", url: COMPARE, ready: async (page) => expect(page.getByTestId("compare-table")).toBeVisible(), fullPage: true },
  {
    name: "analyst",
    url: APPLE,
    ready: async (page) => {
      await page.getByTestId("analyst-open").click();
      await expect(page.getByTestId("analyst-panel")).toContainText("AI not configured");
    },
  },
  {
    name: "ai-settings",
    url: APPLE,
    ready: async (page) => {
      await page.getByTestId("analyst-open").click();
      await page.getByTestId("analyst-panel").getByTestId("ai-settings-open").click();
      await expect(page.getByTestId("ai-settings")).toBeVisible();
    },
  },
];

for (const theme of ["dark", "light"] as const) {
  for (const { width, height } of widths) {
    test(`screens in ${theme} at ${width} px: screenshots, no sideways scroll (M6-AC2, M6-AC8)`, async ({ page }) => {
      test.setTimeout(120_000);
      await page.setViewportSize({ width, height });
      await page.goto("/app");
      await page.evaluate((value) => localStorage.setItem("sec-analytics.theme", value), theme);
      for (const screen of SCREENS) {
        await page.goto(screen.url);
        await expect(page.locator("html")).toHaveAttribute("data-theme", theme);
        await screen.ready(page);
        // Let charts finish their entry animation before the shot.
        await page.waitForTimeout(400);
        const scrollWidth = await page.evaluate(() => document.documentElement.scrollWidth);
        expect(scrollWidth, `${screen.name} (${theme}, ${width}) must not scroll sideways`).toBeLessThanOrEqual(width);
        await page.screenshot({ path: `test-results/m6-${screen.name}-${theme}-${width}.png`, fullPage: screen.fullPage ?? false });
      }
    });
  }
}
