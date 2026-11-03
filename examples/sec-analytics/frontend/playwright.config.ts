import { defineConfig, devices } from "@playwright/test";

// Browser checks. `npm run verify` (repository root) starts the backend and the frontend itself and passes
// BASE_URL, so there is no webServer block here. To run by hand: start `npm run dev` at the root, then
// `BASE_URL=http://127.0.0.1:3000 npm run e2e` in this folder.
export default defineConfig({
  testDir: "./e2e",
  outputDir: "./test-results",
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: 0,
  reporter: [["list"]],
  use: {
    baseURL: process.env.BASE_URL || "http://127.0.0.1:3000",
    trace: "retain-on-failure",
  },
  // channel "chromium" = Playwright's full Chromium in new headless mode (installed by `npm run setup`).
  // The separate headless shell was dropped: on macOS (2026-11-03) its screenshots hung while the full
  // Chromium, tested at the same moment, captured in about 1 s (diagnosis in PROGRESS.md, failures log).
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"], channel: "chromium" } }],
});
