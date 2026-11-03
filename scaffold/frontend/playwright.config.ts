import { defineConfig, devices } from "@playwright/test";

// Browser checks. `npm run verify` (repository root) starts the backend and the frontend itself and passes
// BASE_URL, so there is no webServer block here. To run by hand: start `npm run dev` at the root, then
// `BASE_URL=http://127.0.0.1:3000 npm run e2e` in this folder.
export default defineConfig({
  testDir: "./e2e",
  outputDir: "./test-results",
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  // One retry: in a clean-worktree run the first screenshot after a cold browser start once hung for 30 s
  // (2026-11-03, assertions had passed). Playwright labels a pass-on-retry "flaky" in the report, so it stays
  // visible; a real defect still fails twice.
  retries: 1,
  reporter: [["list"]],
  use: {
    baseURL: process.env.BASE_URL || "http://127.0.0.1:3000",
    trace: "retain-on-failure",
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
});
