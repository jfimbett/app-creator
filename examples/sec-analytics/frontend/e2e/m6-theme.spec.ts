import { expect, type Page, test } from "@playwright/test";

// M6 theme journeys (brief §4.1, §7.2) in offline fixture mode. The theme is a display preference stored in
// localStorage under "sec-analytics.theme"; dark is the default.
const APPLE = "/companies/0000320193";
const LIGHT_BG = "rgb(245, 247, 250)"; // --bg in light (globals.css)
const DARK_BG = "rgb(10, 16, 32)"; // --bg in dark

const html = (page: Page) => page.locator("html");
const bodyBackground = (page: Page) => page.evaluate(() => getComputedStyle(document.body).backgroundColor);

for (const start of ["/app", APPLE, "/"]) {
  test(`theme: dark by default, toggles to light and back, and is remembered on ${start} (M6-AC1)`, async ({ page }) => {
    await page.goto(start);
    await expect(html(page)).toHaveAttribute("data-theme", "dark");
    expect(await bodyBackground(page)).toBe(DARK_BG);

    const toggle = page.getByTestId("theme-toggle").first();
    await expect(toggle).toHaveAccessibleName("Switch to light theme");
    await expect(toggle).not.toHaveAttribute("aria-pressed");
    await toggle.click();
    await expect(html(page)).toHaveAttribute("data-theme", "light");
    await expect(toggle).toHaveAccessibleName("Switch to dark theme");
    await expect.poll(() => bodyBackground(page)).toBe(LIGHT_BG);
    expect(await page.evaluate(() => Object.entries(localStorage))).toEqual([["sec-analytics.theme", "light"]]);

    await page.reload();
    await expect(html(page)).toHaveAttribute("data-theme", "light");

    // Keyboard: the toggle is a real button.
    await page.getByTestId("theme-toggle").first().focus();
    await page.keyboard.press("Enter");
    await expect(html(page)).toHaveAttribute("data-theme", "dark");
    expect(await page.evaluate(() => localStorage.getItem("sec-analytics.theme"))).toBe("dark");
  });
}

test("theme: the stored choice applies before any app JavaScript runs, so there is no dark flash (M6-AC1)", async ({ page }) => {
  await page.goto("/app");
  await page.evaluate(() => localStorage.setItem("sec-analytics.theme", "light"));
  // Block every JavaScript bundle: React never hydrates, so only the inline <head> script can set the theme.
  await page.route("**/*.js", (route) => route.abort());
  await page.route("**/*.js?*", (route) => route.abort());
  await page.goto("/app");
  await expect(html(page)).toHaveAttribute("data-theme", "light");
  expect(await bodyBackground(page)).toBe(LIGHT_BG);
});

test("theme: an invalid stored value means dark (M6-AC1)", async ({ page }) => {
  await page.goto("/app");
  await page.evaluate(() => localStorage.setItem("sec-analytics.theme", "purple"));
  await page.reload();
  await expect(html(page)).toHaveAttribute("data-theme", "dark");
});
