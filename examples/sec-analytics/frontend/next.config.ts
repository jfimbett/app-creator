import type { NextConfig } from "next";

// Where the FastAPI backend listens. The root launchers (npm run dev / demo / verify) set BACKEND_URL;
// the default matches the backend's default port.
// Note: `next build` records this rewrite, so a production build talks to the backend URL it was built with.
const backendUrl = process.env.BACKEND_URL || "http://127.0.0.1:8000";

// This folder is the project root for Next.js. Without this, Next.js sees the repository's own
// package-lock.json one level up and warns that it had to guess the workspace root.
// (The launchers and `npm run ...` always run Next.js from this folder.)
const projectRoot = process.cwd();

const nextConfig: NextConfig = {
  // No floating Next.js dev badge on screen during classroom demos (npm run demo uses the dev server).
  devIndicators: false,
  outputFileTracingRoot: projectRoot,
  turbopack: { root: projectRoot },
  // `npm run verify` builds into .next-verify so it never disturbs a running `npm run dev` (which uses .next).
  distDir: process.env.NEXT_DIST_DIR || ".next",
  // A live request can wait for SEC's Retry-After (up to 30 s, twice) plus its 20 s timeout.
  experimental: { proxyTimeout: 120_000 },
  // The browser only ever calls /api/* on this same site; Next.js forwards those requests to the backend.
  async rewrites() {
    return [{ source: "/api/:path*", destination: `${backendUrl}/api/:path*` }];
  },
};

export default nextConfig;
