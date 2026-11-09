import { expect, type Page, type Route, test } from "@playwright/test";

// A mocked request can still be in flight when a test ends; drop the mocks quietly so it cannot fail the test.
test.afterEach(async ({ page }) => {
  await page.unrouteAll({ behavior: "ignoreErrors" });
});

// M5 browser journeys in offline fixture mode (milestone brief §9). No real key exists in `npm run verify`, so every
// /api/ai/* call is mocked with page.route and the tests are named "(mocked backend)". The mocked replies are
// SYNTHETIC: invented for tests, not real AI answers. The key below is a clearly fake test value.
const KEY = "test-key-not-real-0000";

/**
 * The security property of M5-AC2, kept after M6 added a theme preference (brief §4.5): localStorage may hold only
 * "sec-analytics.theme" with the value "dark" or "light", and no key or value holds the test key or any part of it.
 */
const KEY_PARTS = [KEY, ...KEY.split("-").filter((part) => part.length >= 4)];
async function expectLocalStorageSafe(page: Page) {
  const entries = await page.evaluate(() => Object.entries(localStorage));
  for (const [name, value] of entries) {
    expect(name).toBe("sec-analytics.theme");
    expect(["dark", "light"]).toContain(value);
    for (const part of KEY_PARTS) {
      expect(name).not.toContain(part);
      expect(value).not.toContain(part);
    }
  }
}
const APPLE = "/companies/0000320193";
const APPLE_10K = "0000320193-26-000026";
const READER = `${APPLE}/filings/${APPLE_10K}`;
const COMPARE_TWO = "/compare?ciks=0000320193,0000789019&metrics=revenue,net_margin&years=10&index=none&source=demo";
const NOT_CONFIGURED = "AI not configured: add your own OpenRouter key";
const NOTICE = "Source links are checked; the claims themselves may still be wrong.";
const PASSAGE_BLOCK = 150;
const widths = [
  { width: 1440, height: 900 },
  { width: 1366, height: 900 },
  { width: 390, height: 844 },
];

const MODELS = {
  models: [
    { id: "example/zeta-large", name: "Zeta Large (SYNTHETIC)", context_length: null, prompt_usd_per_million: null, completion_usd_per_million: null, expiration_date: null },
    { id: "example/alpha-small", name: "Alpha Small (SYNTHETIC)", context_length: 131072, prompt_usd_per_million: "0.15", completion_usd_per_million: "0.6", expiration_date: null },
    { id: "example/beta-free:free", name: "Beta Free (SYNTHETIC)", context_length: 32768, prompt_usd_per_million: "0", completion_usd_per_million: "0", expiration_date: "2026-12-31" },
    // Not a valid model id: never offered in the table.
    { id: "bad id <x>", name: "Invalid id (SYNTHETIC)", context_length: null, prompt_usd_per_million: null, completion_usd_per_million: null, expiration_date: null },
  ],
  fetched_at: "2026-11-09T10:00:00Z",
};

const CONTEXT = { line: "Context: AAPL facts FY2017–FY2026 + 10-K passages", facts: 60, passages: 8, chars: 21500 };

const ANSWER = {
  answer:
    "SYNTHETIC TEST DATA (mocked reply). Net margin rose in FY2026 compared with FY2025 [F2]. The 10-K attributes part of the change to a higher share of services revenue [P1]. A further claim cites a source that was not supplied [F99].",
  citations: [
    {
      source_id: "F2",
      valid: true,
      kind: "fact",
      label: "Net margin · FY2026 · 10-K 0000320193-26-000026",
      period: "2025-09-28 – 2026-09-26",
      date: "2026-11-03",
      link: APPLE,
    },
    {
      source_id: "P1",
      valid: true,
      kind: "passage",
      label: `10-K ${APPLE_10K} · Item 7`,
      period: `blocks ${PASSAGE_BLOCK}–${PASSAGE_BLOCK + 6}`,
      date: "2026-11-03",
      link: `${READER}#block-${PASSAGE_BLOCK}`,
    },
  ],
  invalid_references: ["F99"],
  citation_note: null,
  refusal: null,
  context: CONTEXT,
  model: "example/alpha-small",
  usage: { prompt_tokens: 6120, completion_tokens: 142, cost: 0.00101 },
  finish_reason: "stop",
  notice: NOTICE,
};

type Scope = { kind: string; cik?: string; accession?: string; ciks?: string[]; metrics?: string[] };
const TICKERS: Record<string, string> = { "0000320193": "AAPL", "0000789019": "MSFT", "0001652044": "GOOGL" };
const METRIC_LABELS: Record<string, string> = { revenue: "revenue", net_margin: "net margin" };

/** The context line the mocked server builds for a scope, in the shape the brief gives. */
function contextLine(scope: Scope): string {
  if (scope.kind === "filing") return `Context: AAPL 10-K ${scope.accession} passages + AAPL facts`;
  if (scope.kind === "comparison") {
    return `Context: ${(scope.ciks ?? []).map((cik) => TICKERS[cik] ?? cik).join(", ")} facts for ${(scope.metrics ?? []).map((m) => METRIC_LABELS[m] ?? m).join(", ")}`;
  }
  return CONTEXT.line;
}

type ChatHandler = (route: Route) => Promise<void>;
type Calls = { models: number; test: number; chat: number; contextScopes: Scope[]; chatBodies: Record<string, unknown>[]; keyHeaders: Record<string, string | undefined> };

/** Mocks every /api/ai/* endpoint (mocked backend) and records what the page sent. */
async function mockAi(page: Page, chat: ChatHandler = (route) => route.fulfill({ json: ANSWER })): Promise<Calls> {
  const calls: Calls = { models: 0, test: 0, chat: 0, contextScopes: [], chatBodies: [], keyHeaders: {} };
  const note = (route: Route, name: string) => {
    calls.keyHeaders[name] = route.request().headers()["x-openrouter-key"];
  };
  await page.route("**/api/ai/context", async (route) => {
    note(route, "context");
    const body = route.request().postDataJSON() as { scope: Scope; source: string };
    calls.contextScopes.push(body.scope);
    await route.fulfill({ json: { ...CONTEXT, line: contextLine(body.scope) } });
  });
  await page.route("**/api/ai/models", async (route) => {
    calls.models += 1;
    note(route, "models");
    await route.fulfill({ json: MODELS });
  });
  await page.route("**/api/ai/test-connection", async (route) => {
    calls.test += 1;
    note(route, "test");
    await route.fulfill({ json: { ok: true, label: "group-3 (SYNTHETIC)", limit_remaining_usd: 4.5, message: "Key accepted" } });
  });
  await page.route("**/api/ai/chat", async (route) => {
    calls.chat += 1;
    note(route, "chat");
    calls.chatBodies.push(route.request().postDataJSON() as Record<string, unknown>);
    await chat(route);
  });
  return calls;
}

/** Records every request: none may leave the machine, and the key may appear in no URL and no body. */
function recordRequests(page: Page) {
  const offHost: string[] = [];
  const leaks: string[] = [];
  page.on("request", (request) => {
    const url = request.url();
    const host = new URL(url).hostname;
    if (host !== "127.0.0.1" && host !== "localhost") offHost.push(url);
    if (url.includes(KEY) || (request.postData() ?? "").includes(KEY)) leaks.push(url);
  });
  return () => {
    expect(offHost, "no request may leave the machine").toEqual([]);
    expect(leaks, "the key may only travel in the X-OpenRouter-Key header").toEqual([]);
  };
}

const panel = (page: Page) => page.getByTestId("analyst-panel");
const dialog = (page: Page) => page.getByTestId("ai-settings");

async function openAnalyst(page: Page) {
  await page.getByTestId("analyst-open").click();
  await expect(panel(page)).toBeVisible();
}

async function saveKey(page: Page, { remember = false } = {}) {
  await panel(page).getByTestId("ai-settings-open").click();
  await expect(dialog(page)).toBeVisible();
  await dialog(page).getByTestId("ai-key-input").fill(KEY);
  if (remember) await dialog(page).getByTestId("ai-remember").check();
  await dialog(page).getByTestId("ai-key-save").click();
  await expect(dialog(page).getByTestId("ai-key-input")).toHaveValue("");
}

/** Key and model set through the settings dialog, then the dialog closed. */
async function configure(page: Page) {
  await saveKey(page);
  await dialog(page).getByRole("radio", { name: /example\/alpha-small/ }).check();
  await expect(dialog(page).getByTestId("model-choice")).toContainText("example/alpha-small");
  await dialog(page).getByRole("button", { name: "Done" }).click();
  await expect(dialog(page)).toBeHidden();
}

async function ask(page: Page, question = "Why did net margin change?") {
  await panel(page).getByTestId("ai-question").fill(question);
  await panel(page).getByTestId("ai-ask").click();
}

async function noSidewaysScroll(page: Page) {
  // Measured after layout settles (fonts, tables and charts have their final size).
  await page.waitForTimeout(300);
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
  expect(overflow).toBeLessThanOrEqual(0);
}

test("no key: Overview, Filings, the reader and Compare work; the panel says AI not configured (M5-AC1, mocked backend)", async ({ page }) => {
  const assertLocal = recordRequests(page);
  const calls = await mockAi(page);
  await page.goto("/app");
  await expect(page.getByTestId("analyst-open")).toHaveCount(0);

  await page.goto(APPLE);
  await expect(page.getByTestId("key-figures")).toBeVisible();
  await openAnalyst(page);
  await expect(panel(page).getByRole("heading", { name: "Analyst" })).toBeFocused();
  await expect(panel(page)).toContainText(NOT_CONFIGURED);
  await expect(panel(page).getByTestId("ai-status")).toHaveText("AI not configured");
  await expect(panel(page).getByTestId("ai-question")).toHaveCount(0);
  await panel(page).getByTestId("analyst-close").click();
  await expect(panel(page)).toHaveCount(0);
  await expect(page.getByTestId("analyst-open")).toBeFocused();

  await page.getByRole("navigation", { name: "Company views" }).getByRole("link", { name: "Filings" }).click();
  await expect(page.getByTestId("latest-10-K")).toBeVisible();
  await expect(page.getByTestId("analyst-open")).toHaveCount(0); // only company, reader and compare

  await page.goto(READER);
  await expect(page.getByTestId("filing-reader")).toBeVisible();
  await openAnalyst(page);
  await expect(panel(page)).toContainText(NOT_CONFIGURED);
  await page.keyboard.press("Escape");
  await expect(panel(page)).toHaveCount(0);

  await page.goto(COMPARE_TWO);
  await expect(page.getByTestId("compare-table")).toBeVisible();
  await openAnalyst(page);
  await expect(panel(page)).toContainText(NOT_CONFIGURED);
  await page.getByRole("button", { name: "Remove MSFT" }).click();
  await expect(page.getByTestId("analyst-open")).toHaveCount(0); // fewer than 2 companies: nothing to analyse
  await expect(panel(page)).toHaveCount(0);

  expect([calls.models, calls.test, calls.chat]).toEqual([0, 0, 0]);
  assertLocal();
});

test("settings: masked key, sessionStorage off by default with its warning, no key in localStorage (M5-AC2, M6 §4.5, mocked backend)", async ({ page }) => {
  const assertLocal = recordRequests(page);
  await mockAi(page);
  await page.goto(APPLE);
  // A theme choice first, so localStorage really holds the app's one allowed entry while the key is handled.
  await page.getByTestId("theme-toggle").click();
  await expect(page.locator("html")).toHaveAttribute("data-theme", "light");
  expect(await page.evaluate(() => Object.entries(localStorage))).toEqual([["sec-analytics.theme", "light"]]);
  await openAnalyst(page);
  await panel(page).getByTestId("ai-settings-open").click();
  const settings = dialog(page);
  await expect(settings).toBeVisible();
  await expect(settings).toContainText(
    "Use your own OpenRouter key with a credit limit. Your instructor may give you a limited key for your group. This is separate from any model your coding assistant (Claude Code or Cline) uses.",
  );
  const input = settings.getByLabel("OpenRouter key");
  await expect(input).toHaveAttribute("type", "password");
  await expect(input).toHaveAttribute("autocomplete", "off");
  await expect(input).toBeFocused();

  const remember = settings.getByTestId("ai-remember");
  await expect(remember).not.toBeChecked();
  await expect(settings.getByTestId("ai-storage-warning")).toHaveCount(0);
  await remember.check();
  await expect(settings.getByTestId("ai-storage-warning")).toHaveText(/Scripts on this page can read browser storage; this is not secure storage/);
  await remember.uncheck();

  await input.fill(KEY);
  // Typed but not saved: the key is never mirrored into a value attribute or the page's HTML.
  expect(await input.getAttribute("value")).not.toContain(KEY);
  expect(await page.content()).not.toContain(KEY);
  await settings.getByRole("button", { name: "Show" }).click();
  await expect(input).toHaveAttribute("type", "text");
  await settings.getByRole("button", { name: "Hide" }).click();
  await expect(input).toHaveAttribute("type", "password");
  await settings.getByTestId("ai-key-save").click();
  await expect(settings.getByTestId("ai-status")).toHaveText("Key set (memory only)");
  await expect(input).toHaveValue("");

  await expectLocalStorageSafe(page);
  expect(await page.evaluate(() => Object.keys(sessionStorage))).toEqual([]);
  expect(await page.evaluate(() => document.cookie)).toBe("");
  expect(await page.content()).not.toContain(KEY);

  // With a key already saved, ticking "Remember" only shows the warning; nothing is written until confirmed.
  await remember.check();
  await expect(settings.getByTestId("ai-storage-warning")).toHaveText(/Scripts on this page can read browser storage; this is not secure storage/);
  expect(await page.evaluate(() => Object.keys(sessionStorage))).toEqual([]);
  await expect(settings.getByTestId("ai-status")).toHaveText("Key set (memory only)");
  await settings.getByRole("button", { name: "Keep in this tab" }).click();
  await expect(settings.getByTestId("ai-status")).toHaveText("Key set (this tab)");
  expect(await page.evaluate(() => Object.keys(sessionStorage))).toEqual(["sec-analytics.ai"]);
  await remember.uncheck(); // turning it off applies at once: the stored copy is removed
  await expect(settings.getByTestId("ai-status")).toHaveText("Key set (memory only)");
  expect(await page.evaluate(() => Object.keys(sessionStorage))).toEqual([]);
  await expectLocalStorageSafe(page);

  // Esc closes the dialog and returns focus to the button that opened it.
  await page.keyboard.press("Escape");
  await expect(settings).toBeHidden();
  await expect(panel(page).getByTestId("ai-settings-open")).toBeFocused();
  await expect(panel(page).getByTestId("ai-status")).toHaveText("Key set (memory only)");
  assertLocal();
});

test("test connection warns about a charge first; models listed with prices and none chosen; Clear key (M5-AC3, mocked backend)", async ({ page }) => {
  const assertLocal = recordRequests(page);
  const calls = await mockAi(page);
  await page.goto(APPLE);
  await openAnalyst(page);
  await saveKey(page, { remember: true });
  const settings = dialog(page);
  expect(await page.evaluate(() => Object.keys(sessionStorage))).toEqual(["sec-analytics.ai"]);
  await expectLocalStorageSafe(page);

  // The model list loads only once a key is set, sorted by id, with prices per million tokens; nothing chosen.
  const rows = settings.getByTestId("model-row");
  await expect(rows).toHaveCount(3);
  expect(await rows.evaluateAll((all) => all.map((row) => row.getAttribute("data-model-id")))).toEqual([
    "example/alpha-small",
    "example/beta-free:free",
    "example/zeta-large",
  ]);
  await expect(settings.getByTestId("model-table")).toContainText("Prompt $/M");
  await expect(rows.nth(0)).toContainText("131,072 tokens");
  await expect(rows.nth(0)).toContainText("$0.15");
  await expect(rows.nth(0)).toContainText("$0.60");
  await expect(rows.nth(1)).toContainText("free");
  await expect(rows.nth(1)).toContainText("expires 2026-12-31");
  await expect(rows.nth(2)).toContainText("pricing not available");
  await expect(settings.getByRole("radio", { checked: true })).toHaveCount(0);
  await expect(settings.getByTestId("model-choice")).toContainText("No model chosen yet");
  await settings.getByTestId("model-filter").fill("beta");
  await expect(rows).toHaveCount(1);
  await settings.getByTestId("model-filter").fill("");

  // A manual id must match the allowed pattern.
  await settings.getByTestId("model-manual").fill("bad id with spaces");
  await settings.getByRole("button", { name: "Use this id" }).click();
  await expect(settings.getByRole("alert")).toContainText("Use 1–200 letters");
  await settings.getByTestId("model-manual").fill("example/manual-model:beta");
  await settings.getByRole("button", { name: "Use this id" }).click();
  await expect(settings.getByTestId("model-choice")).toContainText("example/manual-model:beta");

  // The charge warning comes before the test call.
  await settings.getByTestId("ai-test").click();
  await expect(settings.getByTestId("ai-charge-confirm")).toContainText("This may incur a small charge");
  expect(calls.test).toBe(0);
  await settings.getByTestId("ai-test-run").click();
  await expect(settings.getByTestId("ai-test-result")).toHaveText("Connected · group-3 (SYNTHETIC) · $4.50 limit remaining");
  await expect(settings.getByTestId("ai-status")).toHaveText("Connected · group-3 (SYNTHETIC)");
  expect(calls.test).toBe(1);
  expect(calls.keyHeaders.test).toBe(KEY);
  expect(calls.keyHeaders.models).toBe(KEY);

  await settings.getByTestId("ai-clear").click();
  await expect(settings.getByTestId("ai-status")).toHaveText("AI not configured");
  await expect(settings.getByTestId("model-choice")).toContainText("No model chosen yet");
  await expect(settings.getByTestId("ai-remember")).not.toBeChecked();
  expect(await page.evaluate(() => Object.keys(sessionStorage))).toEqual([]);
  await settings.getByRole("button", { name: "Done" }).click();
  await expect(panel(page)).toContainText(NOT_CONFIGURED);
  assertLocal();
});

test("Apple Overview → Analyst → ask: answer as text with two linked source chips and the notice (M5-AC4, mocked backend)", async ({ page }) => {
  const assertLocal = recordRequests(page);
  const calls = await mockAi(page);
  await page.goto(APPLE);
  await openAnalyst(page);
  await saveKey(page);
  await dialog(page).getByRole("button", { name: "Done" }).click();

  // A key without a model: Ask stays disabled.
  await panel(page).getByTestId("ai-question").fill("Why did net margin change?");
  await expect(panel(page).getByTestId("ai-ask")).toBeDisabled();
  await expect(panel(page)).toContainText("Choose a model in AI settings to ask.");
  await panel(page).getByTestId("ai-settings-open").click();
  await dialog(page).getByRole("radio", { name: /example\/alpha-small/ }).check();
  await dialog(page).getByRole("button", { name: "Done" }).click();
  await expect(panel(page).getByTestId("ai-count")).toHaveText("26 / 2,000 characters");

  await panel(page).getByTestId("ai-ask").click();
  await expect(panel(page).getByTestId("ai-answer")).toContainText("Net margin rose in FY2026");
  expect(calls.chatBodies).toEqual([{ model: "example/alpha-small", scope: { kind: "company", cik: "0000320193" }, question: "Why did net margin change?", source: "demo" }]);
  expect(calls.keyHeaders.chat).toBe(KEY);
  expect(calls.keyHeaders.context).toBeUndefined();

  const chips = panel(page).getByTestId("source-chip");
  await expect(chips).toHaveCount(2);
  await expect(chips.nth(0)).toHaveText("[F2]Net margin · FY2026 · 10-K 0000320193-26-000026");
  await expect(chips.nth(0)).toHaveAttribute("href", APPLE);
  await expect(chips.nth(0)).toHaveAttribute("title", "2025-09-28 – 2026-09-26 · filed 2026-11-03");
  await expect(chips.nth(1)).toHaveAttribute("href", `${READER}#block-${PASSAGE_BLOCK}`);
  await expect(panel(page).getByTestId("ai-invalid-refs")).toContainText("Reference not in the supplied sources");
  await expect(panel(page).getByTestId("ai-invalid-refs")).toContainText("[F99]");
  await expect(panel(page).getByTestId("ai-notice")).toHaveText(NOTICE);
  await expect(panel(page).getByTestId("ai-usage")).toContainText("Usage: 6,120 prompt + 142 completion tokens · cost $0.00101");
  // Plain text: the answer element holds no child elements.
  expect(await panel(page).getByTestId("ai-answer").evaluate((element) => element.children.length)).toBe(0);

  // The passage chip opens the reader at that block.
  await chips.nth(1).click();
  await expect(page).toHaveURL(new RegExp(`${READER}#block-${PASSAGE_BLOCK}$`));
  await expect(page.locator(`#block-${PASSAGE_BLOCK}`)).toBeInViewport();
  assertLocal();
});

test("no valid source, a refusal and a cut answer are shown as such (mocked backend)", async ({ page }) => {
  const replies = [
    { ...ANSWER, answer: "SYNTHETIC TEST DATA (mocked reply) without references.", citations: [], invalid_references: [], citation_note: "No valid sources cited", notice: "" },
    { ...ANSWER, answer: "", citations: [], invalid_references: [], refusal: { code: "out_of_scope", message: "This analyst only explains the loaded SEC data; it does not forecast prices or give investment advice" }, usage: null },
    {
      ...ANSWER,
      finish_reason: "length",
      // A chip whose link is not an app path is shown as plain text, never as a link.
      citations: [...ANSWER.citations, { ...ANSWER.citations[0], source_id: "F3", link: "//evil.example/companies" }],
    },
  ];
  await mockAi(page, (route) => route.fulfill({ json: replies.shift() }));
  await page.goto(APPLE);
  await openAnalyst(page);
  await configure(page);

  await ask(page, "Summarise the results");
  await expect(panel(page).getByTestId("ai-citation-note")).toHaveText("No valid sources cited");
  await expect(panel(page).getByTestId("source-chip")).toHaveCount(0);
  await expect(panel(page).getByTestId("ai-notice")).toHaveText(NOTICE);

  await ask(page, "Should I buy AAPL?");
  await expect(panel(page).getByTestId("ai-refusal")).toContainText("it does not forecast prices or give investment advice");
  await expect(panel(page).getByTestId("ai-answer")).toHaveCount(0);

  await ask(page, "Why did net margin change?");
  await expect(panel(page).getByTestId("ai-cut")).toContainText("Answer cut at the output limit");
  await expect(panel(page).getByTestId("ai-answer")).toContainText("Net margin rose");
  const unsafe = panel(page).locator('[data-testid="source-chip"][data-source-id="F3"]');
  await expect(unsafe).toBeVisible();
  expect(await unsafe.evaluate((element) => element.tagName)).toBe("SPAN");
  await expect(unsafe).not.toHaveAttribute("href", /.*/);
  await expect(panel(page).locator('a[href*="evil.example"]')).toHaveCount(0);
});

test("the context line names the scope on the company, reader and Compare screens (M5-AC6, mocked backend)", async ({ page }) => {
  const calls = await mockAi(page);
  await page.goto(APPLE);
  await openAnalyst(page);
  await expect(panel(page).getByTestId("ai-context")).toHaveText("Context: AAPL facts FY2017–FY2026 + 10-K passages");

  await page.goto(READER);
  await openAnalyst(page);
  await expect(panel(page).getByTestId("ai-context")).toHaveText(`Context: AAPL 10-K ${APPLE_10K} passages + AAPL facts`);

  await page.goto(COMPARE_TWO);
  await openAnalyst(page);
  await expect(panel(page).getByTestId("ai-context")).toHaveText("Context: AAPL, MSFT facts for revenue, net margin");

  // Distinct scopes: under `next dev` React's Strict Mode starts each effect twice (the first request is aborted).
  expect([...new Set(calls.contextScopes.map((scope) => JSON.stringify(scope)))].map((text) => JSON.parse(text))).toEqual([
    { kind: "company", cik: "0000320193" },
    { kind: "filing", cik: "0000320193", accession: APPLE_10K },
    { kind: "comparison", ciks: ["0000320193", "0000789019"], metrics: ["revenue", "net_margin"] },
  ]);
});

test("a slow reply can be cancelled and the panel is usable again (M5-AC8, mocked backend)", async ({ page }) => {
  let first = true;
  const calls = await mockAi(page, async (route) => {
    if (first) {
      first = false;
      await new Promise((resolve) => setTimeout(resolve, 4000));
      await route.fulfill({ json: ANSWER }).catch(() => undefined); // already aborted by the page
      return;
    }
    await route.fulfill({ json: ANSWER });
  });
  await page.goto(APPLE);
  await openAnalyst(page);
  await configure(page);

  await ask(page);
  const askButton = panel(page).getByTestId("ai-ask");
  await expect(askButton).toBeDisabled(); // one request at a time in this tab
  await expect(askButton).toHaveText("Asking…");
  await panel(page).getByTestId("ai-cancel").click();
  await expect(panel(page).getByTestId("ai-cancelled")).toContainText("Cancelled");
  await expect(panel(page).getByTestId("ai-cancel")).toHaveCount(0);
  await expect(askButton).toBeEnabled();

  await askButton.click();
  await expect(panel(page).getByTestId("source-chip")).toHaveCount(2);
  await expect(panel(page).getByTestId("ai-cancelled")).toHaveCount(0);
  expect(calls.chat).toBe(2);
});

const FAILURES = [
  { status: 401, code: "ai_key_invalid", message: "Key rejected", shown: "Key rejected" },
  { status: 402, code: "ai_insufficient_credits", message: "Out of credits", shown: "Out of credits" },
  { status: 404, code: "ai_model_not_found", message: "Model not available; choose another", shown: "Model not available; choose another" },
  { status: 429, code: "ai_rate_limited", message: "Rate limited; try again later", details: { retry_after: 30 }, shown: "Rate limited; try again later (retry after 30 s)" },
  { status: 504, code: "ai_timeout", message: "The AI did not answer within 60 s", shown: "The AI did not answer within 60 s" },
  { status: 409, code: "ai_busy", message: "Another question is still running", shown: "Another question is still running" },
];

test("mocked 401, 402, 404, 429, timeout and busy answers show the plain messages, each after one call (M5-AC7, mocked backend)", async ({ page }) => {
  let failure = FAILURES[0];
  const calls = await mockAi(page, (route) =>
    route.fulfill({ status: failure.status, json: { error: { code: failure.code, message: failure.message, details: failure.details ?? null, reference: null } } }),
  );
  await page.goto(APPLE);
  await openAnalyst(page);
  await configure(page);
  for (const [index, next] of FAILURES.entries()) {
    failure = next;
    await ask(page);
    const error = panel(page).getByTestId("ai-error");
    await expect(error).toHaveAttribute("data-code", next.code);
    await expect(error).toContainText(next.shown);
    expect(calls.chat, "no automatic retry").toBe(index + 1);
    if (next.code === "ai_key_invalid") await expect(panel(page).getByTestId("ai-status")).toHaveText("Key rejected");
  }
  await expect(panel(page)).not.toContainText(KEY);
});

test("a connection test for a replaced key cannot mark the new key connected (mocked backend)", async ({ page }) => {
  await mockAi(page);
  let release: () => void = () => undefined;
  const held = new Promise<void>((resolve) => (release = resolve));
  await page.route("**/api/ai/test-connection", async (route) => {
    await held;
    await route.fulfill({ json: { ok: true, label: "key-A (SYNTHETIC)", limit_remaining_usd: 1, message: "Key accepted" } }).catch(() => undefined);
  });
  await page.goto(APPLE);
  await openAnalyst(page);
  await saveKey(page);
  const settings = dialog(page);
  await settings.getByTestId("ai-test").click();
  await settings.getByTestId("ai-test-run").click();
  await expect(settings.getByTestId("ai-test")).toHaveText("Testing…");
  // Replace the key while the test for the first key is still running, then let the old answer arrive.
  await settings.getByTestId("ai-key-input").fill("test-key-not-real-1111");
  await settings.getByTestId("ai-key-save").click();
  release();
  await page.waitForTimeout(500);
  await expect(settings.getByTestId("ai-status")).toHaveText("Key set (memory only)");
  await expect(settings.getByTestId("ai-test-result")).toHaveCount(0);
});

test("a running question is stopped when the key is cleared or the scope changes, and its answer never shows (mocked backend)", async ({ page }) => {
  const failed: string[] = [];
  page.on("requestfailed", (request) => {
    if (request.url().endsWith("/api/ai/chat")) failed.push(request.url());
  });
  await mockAi(page, async (route) => {
    await new Promise((resolve) => setTimeout(resolve, 1500));
    await route.fulfill({ json: ANSWER }).catch(() => undefined);
  });
  await page.goto(APPLE);
  await openAnalyst(page);
  await configure(page);

  // Clear key while the question runs.
  await ask(page);
  await expect(panel(page).getByTestId("ai-cancel")).toBeVisible();
  await panel(page).getByTestId("ai-settings-open").click();
  await dialog(page).getByTestId("ai-clear").click();
  await dialog(page).getByRole("button", { name: "Done" }).click();
  await page.waitForTimeout(2000);
  await expect(panel(page)).toContainText(NOT_CONFIGURED);
  await expect(panel(page).getByTestId("ai-answer")).toHaveCount(0);
  expect(failed).toHaveLength(1);

  // A new key, then a scope change (Compare metrics) while the question runs.
  await page.goto(COMPARE_TWO);
  await openAnalyst(page);
  await configure(page);
  await ask(page);
  await expect(panel(page).getByTestId("ai-cancel")).toBeVisible();
  await page.locator('button[data-metric="fcf"]').click();
  await expect(panel(page).getByTestId("ai-context")).toHaveText("Context: AAPL, MSFT facts for revenue, net margin, fcf");
  await page.waitForTimeout(2000);
  await expect(panel(page).getByTestId("ai-answer")).toHaveCount(0);
  await expect(panel(page).getByTestId("ai-ask")).toBeEnabled();
  expect(failed).toHaveLength(2);
});

for (const size of widths) {
  test(`screenshots at ${size.width} px: not configured, settings, answer; no key visible, no sideways scroll (mocked backend)`, async ({ page }) => {
    const assertLocal = recordRequests(page);
    await page.setViewportSize(size);
    await mockAi(page);
    await page.goto(APPLE);
    await expect(page.getByTestId("key-figures")).toBeVisible();
    await openAnalyst(page);
    await expect(panel(page)).toContainText(NOT_CONFIGURED);
    await expect(panel(page).getByTestId("ai-context")).toHaveText(CONTEXT.line);
    await noSidewaysScroll(page);
    await page.screenshot({ path: `test-results/m5-not-configured-${size.width}.png` });

    await saveKey(page);
    await dialog(page).getByRole("radio", { name: /example\/alpha-small/ }).check();
    await dialog(page).getByTestId("ai-test").click();
    await expect(dialog(page).getByTestId("ai-charge-confirm")).toBeVisible();
    await noSidewaysScroll(page);
    expect(await page.content()).not.toContain(KEY);
    await page.screenshot({ path: `test-results/m5-settings-${size.width}.png` });
    await dialog(page).getByRole("button", { name: "Done" }).click();

    await ask(page);
    await expect(panel(page).getByTestId("source-chip")).toHaveCount(2);
    await noSidewaysScroll(page);
    expect(await page.content()).not.toContain(KEY);
    await page.screenshot({ path: `test-results/m5-answer-${size.width}.png` });
    assertLocal();
  });
}
