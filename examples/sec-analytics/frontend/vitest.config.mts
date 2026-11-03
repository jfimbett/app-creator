// Unit tests for frontend logic and small components (`npm run test`). Browser journeys use Playwright (e2e/).
import react from "@vitejs/plugin-react";
import { defineConfig } from "vitest/config";

export default defineConfig({
  plugins: [react()],
  // Understands the "@/..." import alias from tsconfig.json (built into Vite 8).
  resolve: { tsconfigPaths: true },
  test: {
    environment: "jsdom",
    include: ["**/*.test.{ts,tsx}"],
    exclude: ["node_modules/**", "e2e/**", ".next/**", ".next-verify/**"],
  },
});
