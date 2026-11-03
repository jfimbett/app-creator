// Pure logic for the backend status panel (no React, no network), so it is easy to unit-test.

export type HealthState =
  | { kind: "loading" }
  | { kind: "ok"; app: string }
  | { kind: "error"; message: string };

export const UNREACHABLE =
  "The backend is not reachable. Is it running? Start everything with `npm run dev` at the repository root.";

/**
 * Turns the answer of GET /api/health into a display state.
 * `status` is the HTTP status, or null if the request failed before any answer (network error).
 */
export function interpretHealth(status: number | null, body: unknown): HealthState {
  if (status === null) return { kind: "error", message: UNREACHABLE };
  if (status >= 500) {
    // The Next.js proxy answers 500 when it cannot reach the backend at all.
    return { kind: "error", message: `${UNREACHABLE} (HTTP ${status})` };
  }
  if (status !== 200) return { kind: "error", message: `The backend answered with HTTP ${status}.` };
  if (typeof body === "object" && body !== null && (body as { status?: unknown }).status === "ok") {
    const app = (body as { app?: unknown }).app;
    return { kind: "ok", app: typeof app === "string" ? app : "unknown app" };
  }
  return { kind: "error", message: "The backend answered, but not with the expected health status." };
}
