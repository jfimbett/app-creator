import base from "./playwright.config";

// The live SEC journey is run by hand, never by `npm run verify` (see e2e-live/live-sec.spec.ts).
const liveConfig = { ...base, testDir: "./e2e-live" };

export default liveConfig;
