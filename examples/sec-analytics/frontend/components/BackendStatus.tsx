"use client";

import { useCallback, useEffect, useState } from "react";

import { type HealthState, interpretHealth } from "@/lib/health";
import { BACKEND_UNREACHABLE } from "@/lib/api";

/**
 * Compact backend indicator for the header. It asks GET /api/health once when the page loads; when the backend
 * is down it says so in words and offers a re-check. The state is in the text, not only the colour.
 */
export function BackendStatus() {
  const [state, setState] = useState<HealthState>({ kind: "loading" });

  const check = useCallback(async () => {
    try {
      const res = await fetch("/api/health", { cache: "no-store" });
      const body: unknown = await res.json().catch(() => null);
      setState(interpretHealth(res.status, body));
    } catch {
      setState(interpretHealth(null, null));
    }
  }, []);

  useEffect(() => {
    // The answer arrives asynchronously; the state is set when it does.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    void check();
  }, [check]);

  const recheck = () => {
    setState({ kind: "loading" });
    void check();
  };

  const dot = state.kind === "ok" ? "bg-positive" : state.kind === "error" ? "bg-negative" : "bg-muted";
  const text = state.kind === "ok" ? "Backend OK" : state.kind === "error" ? BACKEND_UNREACHABLE : "Backend: checking…";

  return (
    <span className="inline-flex items-center gap-1">
      <span
        role="status"
        aria-live="polite"
        data-testid="health-status"
        data-state={state.kind}
        className={`inline-flex h-7 items-center gap-1.5 rounded-md border px-2 text-xs ${state.kind === "error" ? "border-negative font-medium text-negative" : "border-line text-muted"}`}
      >
        <span aria-hidden="true" className={`h-2 w-2 shrink-0 rounded-full ${dot}`} />
        {text}
      </span>
      {state.kind === "error" ? (
        <button type="button" onClick={recheck} className="btn min-h-7! text-xs!">
          Check again
        </button>
      ) : null}
    </span>
  );
}
