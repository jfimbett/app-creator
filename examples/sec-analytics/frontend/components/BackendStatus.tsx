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

  const tone = state.kind === "ok" ? "border-positive text-positive" : state.kind === "error" ? "border-negative text-negative" : "border-line text-muted";
  const text = state.kind === "ok" ? "Backend OK" : state.kind === "error" ? BACKEND_UNREACHABLE : "Backend: checking…";

  return (
    <span className="inline-flex items-center gap-1">
      <span
        role="status"
        aria-live="polite"
        data-testid="health-status"
        data-state={state.kind}
        className={`inline-flex items-center rounded-sm border px-1.5 py-px leading-4 ${state.kind === "error" ? "text-table font-medium" : "label-caps"} ${tone}`}
      >
        {text}
      </span>
      {state.kind === "error" ? (
        <button type="button" onClick={recheck} className="label-caps rounded-sm border border-line px-1.5 py-px leading-4 text-fg hover:border-accent">
          Check again
        </button>
      ) : null}
    </span>
  );
}
