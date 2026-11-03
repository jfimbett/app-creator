import type { ReactNode } from "react";

/**
 * One place for the states of a data area (brief §4 and §3.7), so every screen says the same thing the same way:
 *  - loading: skeleton rows that keep the layout (no spinner on a blank page)
 *  - empty:   nothing to show yet, and what to do
 *  - missing: the data exists but SEC did not report this value
 *  - offline: the backend cannot be reached
 *  - error:   the API answered with an error envelope
 * Each state carries a text tag (LOADING, NO DATA, MISSING, OFFLINE, ERROR), so meaning never depends on colour.
 */
export type StateKind = "loading" | "empty" | "missing" | "offline" | "error";

export type StatePanelProps = {
  kind: StateKind;
  /** Short headline, e.g. "No match in the demo universe (3 companies)". */
  title?: string;
  /** One or two sentences: what happened and what to do next. */
  message?: ReactNode;
  /** Error reference id from the error envelope, shown so a person can quote it. */
  reference?: string | null;
  /** A retry or next-step action. Renders a button when given. */
  action?: { label: string; onClick: () => void };
  /** Number of skeleton rows while loading (default 3). */
  rows?: number;
  className?: string;
};

export const OFFLINE_MESSAGE = "Backend not reachable: start it with npm run demo";

const TAG: Record<StateKind, string> = {
  loading: "LOADING",
  empty: "NO DATA",
  missing: "MISSING",
  offline: "OFFLINE",
  error: "ERROR",
};

const DEFAULT_TITLE: Record<StateKind, string> = {
  loading: "Loading…",
  empty: "Nothing to show yet",
  missing: "Not reported by SEC",
  offline: OFFLINE_MESSAGE,
  error: "Something went wrong",
};

const TONE: Record<StateKind, string> = {
  loading: "border-l-line text-muted",
  empty: "border-l-line text-muted",
  missing: "border-l-line text-muted",
  offline: "border-l-warning text-warning",
  error: "border-l-negative text-negative",
};

export function StatePanel({ kind, title, message, reference, action, rows = 3, className }: StatePanelProps) {
  const isProblem = kind === "error" || kind === "offline";
  const heading = title ?? DEFAULT_TITLE[kind];

  if (kind === "loading") {
    return (
      <div role="status" aria-live="polite" data-testid="state-panel" data-state={kind} className={className}>
        <span className="sr-only">{heading}</span>
        <div aria-hidden="true" className="flex flex-col gap-2 py-1">
          {Array.from({ length: rows }, (_, i) => (
            <span key={i} className="skeleton" style={{ width: `${92 - ((i * 17) % 40)}%` }} />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div
      role={isProblem ? "alert" : "status"}
      aria-live={isProblem ? undefined : "polite"}
      data-testid="state-panel"
      data-state={kind}
      className={`border-l-2 bg-panel-raised px-3 py-2 ${TONE[kind]} ${className ?? ""}`}
    >
      <p className="flex flex-wrap items-baseline gap-x-2">
        <span className="label-caps">{TAG[kind]}</span>
        <span className="font-semibold text-fg">{heading}</span>
      </p>
      {message ? <div className="mt-1 text-fg">{message}</div> : null}
      {reference ? (
        <p className="mt-1 text-muted">
          Reference: <span className="code-id">{reference}</span>
        </p>
      ) : null}
      {action ? (
        <button
          type="button"
          onClick={action.onClick}
          className="mt-2 rounded-sm border border-line bg-panel px-2 py-1 text-fg hover:border-accent"
        >
          {action.label}
        </button>
      ) : null}
    </div>
  );
}
