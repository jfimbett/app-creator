"use client";

import { useCallback, useEffect, useState } from "react";

import { type HealthState, interpretHealth } from "@/lib/health";

/** Asks the backend (through the same-origin /api proxy) whether it is up, and shows the answer. */
export function HealthStatus() {
  const [state, setState] = useState<HealthState>({ kind: "loading" });

  const check = useCallback(async () => {
    setState({ kind: "loading" });
    try {
      const res = await fetch("/api/health", { cache: "no-store" });
      const body: unknown = await res.json().catch(() => null);
      setState(interpretHealth(res.status, body));
    } catch {
      setState(interpretHealth(null, null));
    }
  }, []);

  useEffect(() => {
    // Runs once after the page loads in the browser; the result arrives asynchronously.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    void check();
  }, [check]);

  const tone =
    state.kind === "ok"
      ? "border-[var(--ok)] text-[var(--ok)]"
      : state.kind === "error"
        ? "border-[var(--error)] text-[var(--error)]"
        : "border-[var(--border)] text-[var(--muted)]";

  return (
    <section aria-labelledby="status-heading" className="rounded-lg border border-[var(--border)] bg-[var(--surface)] p-5">
      <h2 id="status-heading" className="text-lg font-semibold">
        Backend status
      </h2>
      <div role="status" aria-live="polite" data-testid="health-status" data-state={state.kind} className={`mt-3 rounded-md border-l-4 px-3 py-2 ${tone}`}>
        {state.kind === "loading" && <p>Checking the backend…</p>}
        {state.kind === "ok" && (
          <p>
            <span className="font-semibold">OK</span>: the backend ({state.app}) is running.
          </p>
        )}
        {state.kind === "error" && (
          <p>
            <span className="font-semibold">Error</span>: {state.message}
          </p>
        )}
      </div>
      <button
        type="button"
        onClick={() => void check()}
        disabled={state.kind === "loading"}
        className="mt-4 rounded-md border border-[var(--border)] px-3 py-1.5 text-sm hover:bg-[var(--border)] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--focus)] disabled:opacity-50"
      >
        Check again
      </button>
    </section>
  );
}
