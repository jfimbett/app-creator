import { expect, type Page, test } from "@playwright/test";

// M3 browser journeys in offline fixture mode (milestones/acceptance.md, M3). Run by `npm run verify`.
// The recorded snapshot holds the latest 10-K and 10-Q documents of Apple, Microsoft and Alphabet.
// Tests named "(mocked backend)" use page.route for states the recorded data cannot produce.
const APPLE = "/companies/0000320193";
const ALPHABET = "/companies/0001652044";
const APPLE_10K = "0000320193-26-000026";
const APPLE_10K_URL = "https://www.sec.gov/Archives/edgar/data/320193/000032019326000026/aapl-20260926.htm";
const APPLE_OLD_10K = "0000320193-25-000079"; // in the history, document not recorded
const ALPHABET_10KA = "0001193125-19-028757"; // a real 10-K/A in the recorded submissions

function recordHosts(page: Page) {
  const offHost: string[] = [];
  page.on("request", (request) => {
    const host = new URL(request.url()).hostname;
    if (host !== "127.0.0.1" && host !== "localhost") offHost.push(request.url());
  });
  return () => expect(offHost, "no request may leave the machine").toEqual([]);
}


/** M3-E4: in demo mode, app text that says "latest" names the snapshot (the filing's own text is excluded). */
async function expectLatestAlwaysNamesTheSnapshot(page: Page) {
  const texts = await page.evaluate(() => {
    const found: string[] = [];
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    for (let node = walker.nextNode(); node; node = walker.nextNode()) {
      const text = node.textContent ?? "";
      const parent = node.parentElement;
      if (!parent || parent.closest('[data-testid="filing-reader"], script, style, noscript, template')) continue;
      if (/latest/i.test(text)) found.push(text.trim());
    }
    return found;
  });
  expect(texts.length).toBeGreaterThan(0);
  for (const text of texts) expect(text).toMatch(/Latest in snapshot \(as of 2026-11-03\)|not necessarily the latest/i);
}

test("Filings tab shows the latest 10-K and 10-Q in the snapshot (M3-AC1, M3-E4)", async ({ page }) => {
  const assertLocalOnly = recordHosts(page);
  await page.goto(APPLE);
  await page.getByRole("navigation", { name: "Company views" }).getByRole("link", { name: "Filings" }).click();
  await expect(page).toHaveURL(new RegExp(`${APPLE}/filings$`));

  await expect(page.getByTestId("latest-label")).toHaveText("Latest in snapshot (as of 2026-11-03)");
  const annual = page.getByTestId("latest-10-K");
  await expect(annual).toContainText("10-K");
  await expect(annual).toContainText("2026-11-03"); // filed
  await expect(annual).toContainText("2026-09-26"); // period
  await expect(annual).toContainText(APPLE_10K);
  const quarterly = page.getByTestId("latest-10-Q");
  await expect(quarterly).toContainText("2026-07-31");
  await expect(quarterly).toContainText("2026-06-27");
  await expect(quarterly).toContainText("0000320193-26-000020");
  await expectLatestAlwaysNamesTheSnapshot(page);
  assertLocalOnly();
});

test("history lists only 10-K/10-Q forms and labels amendments (M3-AC2, M3-E1)", async ({ page }) => {
  await page.goto(`${ALPHABET}/filings`);
  const history = page.getByTestId("filing-history");
  await expect(history).toBeVisible();
  const forms = await page.getByTestId("filing-row").evaluateAll((rows) => rows.map((row) => row.getAttribute("data-form")));
  expect(forms.length).toBeGreaterThan(30);
  expect(new Set(forms)).toEqual(new Set(["10-K", "10-Q", "10-K/A"]));

  const amended = page.locator(`[data-testid="filing-row"]:has-text("${ALPHABET_10KA}")`);
  await expect(amended.getByTestId("amendment-label")).toHaveText(/amendment/i);

  await page.getByText("Include amendments").click();
  await expect(page.locator('[data-testid="filing-row"][data-form="10-K/A"]')).toHaveCount(0);
  await page.locator("label", { hasText: /^Annual$/ }).click();
  const annualForms = await page.getByTestId("filing-row").evaluateAll((rows) => rows.map((row) => row.getAttribute("data-form")));
  expect(new Set(annualForms)).toEqual(new Set(["10-K"]));
});

test("reader shows sanitized text, sections, search and the exact source link (M3-AC3–AC6, M3-E2)", async ({ page }) => {
  const assertLocalOnly = recordHosts(page);
  await page.goto(`${APPLE}/filings`);
  await page.getByTestId("latest-10-K").getByRole("link", { name: /^Read 10-K/ }).click();
  await expect(page).toHaveURL(new RegExp(`${APPLE}/filings/${APPLE_10K}$`));

  // M3-AC3: readable text, a labelled section list.
  const reader = page.getByTestId("filing-reader");
  await expect(reader).toContainText("FORM 10-K");
  await expect(reader).toContainText("Apple Inc.");
  await expect(page.getByTestId("section-note")).toHaveText("Sections detected automatically; may be imperfect");
  const rail = page.getByTestId("section-rail");
  for (const item of ["Item 1", "Item 1A", "Item 7", "Item 8"]) {
    await expect(rail.getByText(item, { exact: true })).toBeVisible();
  }
  await expect(page.getByTestId("reader-scope")).toContainText("Not necessarily the latest report on EDGAR");
  await expectLatestAlwaysNamesTheSnapshot(page);

  // M3-E2: no active content from the filing reaches the page.
  expect(await reader.locator("script, iframe, object, embed, form, style").count()).toBe(0);
  expect(await reader.locator('[href^="javascript:" i], [onclick], [onerror], [onload]').count()).toBe(0);

  // M3-AC4: Item 7 jumps to its body heading, not the table of contents.
  await rail.getByText("Item 7", { exact: true }).click();
  const item7 = reader.getByText(/^Item 7\.\s+Management.s Discussion and Analysis/).last();
  await expect(item7).toBeInViewport();
  await expect(reader.locator("p, div").filter({ hasText: /^The following discussion should be read in conjunction/ }).first()).toBeInViewport();

  // M3-AC5: highlighted matches, a count, next and previous.
  await page.getByTestId("filing-search").fill("revenue");
  const count = page.getByTestId("search-count");
  await expect(count).toHaveText(/^1 of \d+$/);
  const total = Number((await count.textContent())!.split(" of ")[1]);
  expect(total).toBeGreaterThan(10);
  await expect(reader.getByTestId("search-hit").first()).toBeVisible();
  await page.getByTestId("search-next").click();
  await expect(count).toHaveText(`2 of ${total}`);
  await expect(reader.locator('[data-testid="search-hit"][data-current="true"]')).toBeInViewport();
  await page.getByTestId("search-previous").click();
  await page.getByTestId("search-previous").click();
  await expect(count).toHaveText(`${total} of ${total}`);
  await page.getByTestId("search-clear").click();
  await expect(reader.getByTestId("search-hit")).toHaveCount(0);

  // M3-AC6: the exact archive document, in a new tab.
  const source = page.getByTestId("reader-source").getByRole("link");
  await expect(source).toHaveAttribute("href", APPLE_10K_URL);
  await expect(source).toHaveAttribute("target", "_blank");
  await expect(source).toHaveAttribute("rel", /noopener/);
  assertLocalOnly();
});

test("a filing without a recorded document and an invalid accession show clear states (M3-E5)", async ({ page }) => {
  await page.goto(`${APPLE}/filings/${APPLE_OLD_10K}`);
  await expect(page.getByText("This filing's document is not in the recorded demo snapshot")).toBeVisible();
  await expect(page.getByRole("link", { name: "Back to the filing list" })).toBeVisible();

  await page.goto(`${APPLE}/filings/not-an-accession`);
  await expect(page.getByText("This is not a valid accession number", { exact: true })).toBeVisible();
  await expect(page.getByText(/looks like 0000320193-26-000026/)).toBeVisible();
});

test("reader falls back to the full text when no sections are found (M3-AC7, mocked backend)", async ({ page }) => {
  await page.route(`**/api/companies/*/filings/${APPLE_10K}*`, async (route) => {
    const response = await route.fetch();
    const body = await response.json();
    await route.fulfill({
      response,
      json: { ...body, sections: [], section_status: "not_detected", note: "Section boundaries not detected; showing full text" },
    });
  });
  await page.goto(`${APPLE}/filings/${APPLE_10K}`);
  await expect(page.getByTestId("section-note")).toHaveText("Section boundaries not detected; showing full text");
  await expect(page.getByTestId("section-rail")).toHaveCount(0);
  await expect(page.getByTestId("filing-reader")).toContainText("FORM 10-K");
  await page.getByTestId("filing-search").fill("iPhone");
  await expect(page.getByTestId("search-count")).toHaveText(/^1 of \d+$/);
});

test("phone width: Read links fit the screen and sections are a select (390 px)", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto(`${APPLE}/filings`);
  const firstRead = page.getByTestId("filing-row").first().getByRole("link", { name: /^Read/ });
  await expect(firstRead).toBeInViewport();
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
  expect(overflow).toBeLessThanOrEqual(0);

  await firstRead.click();
  const select = page.getByTestId("section-select");
  await expect(select).toBeVisible();
  await expect(page.getByTestId("section-rail")).toBeHidden();
  const item7 = await select.locator("option", { hasText: /^Item 7 ·/ }).first().getAttribute("value");
  await select.selectOption(item7!);
  await expect(page.getByTestId("filing-reader").getByText(/^Item 7\.\s+Management.s Discussion and Analysis/).last()).toBeInViewport();
});
