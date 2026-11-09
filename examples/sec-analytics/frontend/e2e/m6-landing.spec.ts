import { expect, type Page, test } from "@playwright/test";

// M6 landing page journeys (brief §4.3, §6, §7.1) in offline fixture mode.
const REVIEWS_LABEL = "Fictional testimonials written for this teaching demo.";
const PRICING_NOTE = "Prices are illustrative. This teaching app has no accounts and takes no payments.";
const ABOUT_LABEL = "SEC Analytics and its team are fictional, created for a programming course.";
const DISCLAIMER = "not affiliated with or endorsed by the U.S. Securities and Exchange Commission";
const ALLOWED_EXTERNAL = ["https://github.com/jfimbett/app-creator", "mailto:hello@example.com"];
const SECTIONS = ["top", "features", "how-it-works", "reviews", "pricing", "about", "faq"];

/** Records every request that leaves this machine (the page must load nothing from elsewhere). */
function recordOffHost(page: Page) {
  const offHost: string[] = [];
  page.on("request", (request) => {
    const url = new URL(request.url());
    if (!["127.0.0.1", "localhost"].includes(url.hostname) && url.protocol !== "data:") offHost.push(request.url());
  });
  return offHost;
}

test("landing: every section, the three labels and the SEC disclaimer; nothing leaves this machine (M6-AC4, M6-AC6)", async ({ page }) => {
  const offHost = recordOffHost(page);
  await page.goto("/");
  await expect(page).toHaveTitle("SEC Analytics: understand public companies from their SEC filings");
  await expect(page.getByRole("heading", { level: 1 })).toHaveText("Understand public companies from their SEC filings");
  for (const id of SECTIONS) await expect(page.locator(`section#${id}`)).toHaveCount(1);
  await expect(page.locator("#reviews")).toContainText(REVIEWS_LABEL);
  await expect(page.locator("#pricing")).toContainText(PRICING_NOTE);
  await expect(page.locator("#about")).toContainText(ABOUT_LABEL);
  await expect(page.getByTestId("landing-disclaimer")).toContainText(DISCLAIMER);
  await expect(page.getByText("© 2026 SEC Analytics (fictional)")).toBeVisible();

  // The label sits directly under the Reviews heading, before any testimonial.
  const order = await page.locator("#reviews").evaluate((section) => {
    const label = section.querySelector('[data-testid="reviews-label"]');
    const firstQuote = section.querySelector("blockquote");
    return label && firstQuote ? label.compareDocumentPosition(firstQuote) & Node.DOCUMENT_POSITION_FOLLOWING : 0;
  });
  expect(order).toBeTruthy();

  // Hero screenshot: a real image that loaded, with meaningful alt text.
  const shot = page.locator("#top img:visible");
  await expect(shot).toHaveCount(1);
  expect(await shot.evaluate((img: HTMLImageElement) => img.complete && img.naturalWidth > 0)).toBe(true);
  expect((await shot.getAttribute("alt"))?.length ?? 0).toBeGreaterThan(40);

  // No payment, sign-up or data-sending controls anywhere on the page.
  await expect(page.locator("form")).toHaveCount(0);
  await expect(page.locator("input")).toHaveCount(0);
  const text = (await page.locator("body").innerText()).toLowerCase();
  for (const banned of ["card number", "checkout", "sign up", "subscribe now", "credit card", "billing", "cvv"]) expect(text).not.toContain(banned);
  expect(offHost).toEqual([]);
});

test("landing: every link and button goes somewhere real (M6-AC4, brief §6)", async ({ page, request }) => {
  await page.goto("/");
  const hrefs = await page.locator("a[href]").evaluateAll((links) => links.map((link) => link.getAttribute("href") ?? ""));
  expect(hrefs.length).toBeGreaterThan(10);
  for (const href of new Set(hrefs)) {
    if (href.startsWith("#")) {
      await expect(page.locator(href), `anchor ${href}`).toHaveCount(1);
    } else if (href.startsWith("/")) {
      const response = await request.get(href);
      expect(response.status(), `link ${href}`).toBe(200);
    } else {
      expect(ALLOWED_EXTERNAL, `external link ${href}`).toContain(href);
    }
  }
  // Every button does something: the only buttons are the theme toggle and the mobile menu button.
  // (Scoped to the page's own header, main and footer; the dev server adds its own overlay elsewhere.)
  const buttons = await page.locator("body > header button, body > main button, body > footer button").evaluateAll((all) => all.map((b) => b.getAttribute("data-testid")));
  expect(new Set(buttons)).toEqual(new Set(["theme-toggle", "landing-menu-button"]));
});

test("landing: Open the app goes to /app and the demo companies load; See pricing scrolls to #pricing (M6-AC4)", async ({ page }) => {
  await page.goto("/");
  await page.locator("#top").getByRole("link", { name: "See pricing" }).click();
  await expect(page).toHaveURL(/#pricing$/);
  await expect(page.locator("#pricing-title")).toBeInViewport();

  await page.locator("#top").getByRole("link", { name: "Open the app" }).click();
  await expect(page).toHaveURL(/\/app$/);
  await expect(page.getByRole("link", { name: /AAPL/ }).first()).toBeVisible({ timeout: 15_000 });
});

test("landing: renders with the backend stopped (M6-AC4)", async ({ page }) => {
  const apiCalls: string[] = [];
  await page.route("**/api/**", (route) => {
    apiCalls.push(route.request().url());
    return route.abort();
  });
  await page.goto("/");
  await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
  await expect(page.locator("#faq details")).toHaveCount(5);
  expect(apiCalls).toEqual([]);
});

test("landing at 390 px: the menu opens, closes with Esc and returns focus; no sideways scroll (M6-AC4)", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");
  const button = page.getByTestId("landing-menu-button");
  const menu = page.getByTestId("landing-menu");
  await expect(menu).toBeHidden();
  await expect(button).toHaveAttribute("aria-expanded", "false");
  await button.click();
  await expect(menu).toBeVisible();
  await expect(button).toHaveAttribute("aria-expanded", "true");
  await menu.getByRole("link", { name: "FAQ" }).focus();
  await page.keyboard.press("Escape");
  await expect(menu).toBeHidden();
  await expect(button).toBeFocused();

  // Choosing a section closes the menu and goes there.
  await button.click();
  await menu.getByRole("link", { name: "Pricing" }).click();
  await expect(menu).toBeHidden();
  await expect(page).toHaveURL(/#pricing$/);

  expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(390);
});

test("app footer: the same SEC disclaimer and a link back to the landing page (M6-AC6)", async ({ page }) => {
  await page.goto("/app");
  await expect(page.getByTestId("app-disclaimer")).toContainText(DISCLAIMER);
  await page.getByRole("contentinfo").getByRole("link", { name: "About SEC Analytics" }).click();
  await expect(page).toHaveURL(/\/$/);
  await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
});

test("app home in Live mode loads no company data before a company is opened (no prefetching from SEC)", async ({ page }) => {
  const companyCalls: string[] = [];
  page.on("request", (request) => {
    if (new URL(request.url()).pathname.startsWith("/api/companies/")) companyCalls.push(request.url());
  });
  await page.goto("/app?source=live");
  await expect(page.getByRole("link", { name: /AAPL/ }).first()).toBeVisible({ timeout: 15_000 });
  await expect(page.getByText("Open the company to load its live figures.").first()).toBeVisible();
  await page.waitForTimeout(1_000);
  expect(companyCalls).toEqual([]);
});
