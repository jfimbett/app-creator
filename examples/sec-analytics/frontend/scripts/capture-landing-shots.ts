// Captures the landing page's screenshots from the running demo app (brief §4.3). Run by hand, not part of verify:
//
//   npm run demo                      (repository root; fixture mode: recorded SEC data, no key, no network)
//   cd examples/sec-analytics/frontend
//   BASE_URL=http://127.0.0.1:3000 node scripts/capture-landing-shots.ts
//
// (Node 22.18+ runs TypeScript directly. Set PLAYWRIGHT_BROWSERS_PATH=../../../.cache/ms-playwright if the browser
// is not found.) It writes public/landing/<stem>-<dark|light>.png. The shots show recorded demo data only: the
// script refuses to run unless the page shows the "Recorded SEC demo" badge, and it never opens the AI settings.

import { mkdirSync, statSync } from "node:fs";
import { join } from "node:path";

import { chromium, type Page } from "@playwright/test";

const BASE_URL = process.env.BASE_URL || "http://127.0.0.1:3000";
const OUT = join(process.cwd(), "public", "landing");
const MAX_BYTES = 400 * 1024;

type Shot = { stem: string; url: string; width: number; height: number; ready: (page: Page) => Promise<void> };

const SHOTS: Shot[] = [
  {
    stem: "app",
    url: "/companies/0000320193",
    width: 1440,
    height: 900,
    ready: async (page) => {
      await page.getByTestId("overview-chart").locator("svg").first().waitFor();
    },
  },
  {
    stem: "feature-compare",
    url: "/compare?ciks=0000320193,0000789019,0001652044&metrics=revenue,net_margin&years=10&index=none",
    width: 1200,
    height: 760,
    ready: async (page) => {
      await page.getByTestId("compare-table").waitFor();
      // Show the chart rather than the table at the top of the crop.
      await page.getByRole("heading", { name: /chart/i }).first().scrollIntoViewIfNeeded().catch(() => undefined);
    },
  },
  {
    stem: "feature-reader",
    url: "/companies/0000320193/filings/0000320193-26-000026",
    width: 1200,
    height: 760,
    ready: async (page) => {
      await page.getByTestId("filing-reader").getByText("FORM 10-K").first().waitFor();
    },
  },
];

async function main() {
  mkdirSync(OUT, { recursive: true });
  const browser = await chromium.launch({ channel: "chromium" });
  try {
    for (const theme of ["dark", "light"] as const) {
      for (const shot of SHOTS) {
        const context = await browser.newContext({ viewport: { width: shot.width, height: shot.height }, deviceScaleFactor: 1 });
        const page = await context.newPage();
        await page.goto(`${BASE_URL}/app`);
        await page.evaluate((value) => localStorage.setItem("sec-analytics.theme", value), theme);
        await page.goto(`${BASE_URL}${shot.url}`);
        await shot.ready(page);
        if ((await page.getByText(/recorded sec demo/i).count()) === 0) throw new Error(`${shot.url}: not in Demo mode; refusing to capture`);
        await page.waitForTimeout(600); // let chart entry animations finish
        const file = join(OUT, `${shot.stem}-${theme}.png`);
        await page.screenshot({ path: file });
        const size = statSync(file).size;
        console.log(`${file}  ${(size / 1024).toFixed(0)} KB${size > MAX_BYTES ? "  (over 400 KB: compress before committing)" : ""}`);
        await context.close();
      }
    }
  } finally {
    await browser.close();
  }
}

main().catch((error: unknown) => {
  console.error(error);
  process.exit(1);
});
