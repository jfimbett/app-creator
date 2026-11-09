"use client";

import { useState } from "react";

import { api, ApiError } from "@/lib/api";
import { COMPARE_METRICS, type CompareState, MAX_METRICS, MONEY_METRICS, YEAR_CHOICES } from "@/lib/compare-state";

/** 1–6 metrics from the comparison set, as toggle buttons. */
export function MetricPicker({ selected, onToggle }: { selected: readonly string[]; onToggle: (id: string) => void }) {
  return (
    <div role="group" aria-label="Metrics" className="flex flex-wrap items-center gap-1.5">
      <span className="label-caps mr-1 w-full text-muted sm:w-auto">Metrics</span>
      {COMPARE_METRICS.map((metric) => {
        const on = selected.includes(metric.id);
        return (
          <button
            key={metric.id}
            type="button"
            aria-pressed={on}
            data-metric={metric.id}
            disabled={(!on && selected.length >= MAX_METRICS) || (on && selected.length === 1)}
            onClick={() => onToggle(metric.id)}
            className="toggle"
          >
            {metric.label}
          </button>
        );
      })}
    </div>
  );
}

export function YearsPicker({ years, onChange }: { years: number; onChange: (years: number) => void }) {
  return (
    <label className="flex items-center gap-2 text-table">
      <span className="label-caps text-muted">Years</span>
      <select value={years} onChange={(event) => onChange(Number(event.target.value))} className="field py-0.5 tabular-nums">
        {YEAR_CHOICES.map((choice) => (
          <option key={choice} value={choice}>
            {choice}
          </option>
        ))}
      </select>
    </label>
  );
}

export const INDEX_LABEL = "Index = 100 at first common fiscal year";
export const NO_COMMON_YEAR = "No common fiscal year to index from";
export const INDEX_NEEDS_MONEY = "Indexing applies to revenue, operating cash flow and FCF";

/**
 * The indexing switch. It is disabled, with the reason, when no fiscal year is common to every company
 * (the backend says so in `index_available`) or when no amount metric is selected.
 */
export function IndexToggle({
  on,
  available,
  metrics,
  onChange,
}: {
  on: boolean;
  available: boolean | null;
  metrics: readonly string[];
  onChange: (on: boolean) => void;
}) {
  const hasMoney = metrics.some((metric) => MONEY_METRICS.has(metric));
  const reason = !hasMoney ? INDEX_NEEDS_MONEY : available === false ? NO_COMMON_YEAR : null;
  const disabled = reason !== null || available === null;
  return (
    <div className="flex flex-wrap items-center gap-x-2 text-table">
      <label className={`inline-flex items-center gap-1.5 ${disabled ? "cursor-not-allowed text-muted" : "cursor-pointer"}`}>
        <input type="checkbox" data-testid="index-toggle" checked={on && !disabled} disabled={disabled} onChange={(event) => onChange(event.target.checked)} className="h-4 w-4 accent-[var(--accent)]" />
        {INDEX_LABEL}
      </label>
      {reason ? (
        <span data-testid="index-unavailable" className="text-muted">
          {reason}
        </span>
      ) : null}
    </div>
  );
}

/**
 * Downloads /api/compare.csv with the same parameters as the table, so the file holds exactly the rows shown.
 * The file is fetched first, so a failure is shown here instead of an empty download.
 */
export function ExportCsvButton({ state, disabled }: { state: CompareState; disabled: boolean }) {
  const [status, setStatus] = useState<"idle" | "working" | "failed">("idle");
  const [error, setError] = useState<string | null>(null);

  const download = async () => {
    setStatus("working");
    setError(null);
    try {
      const { blob, filename } = await api.downloadCompareCsv(state);
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.setTimeout(() => URL.revokeObjectURL(url), 1000);
      setStatus("idle");
    } catch (failure) {
      setStatus("failed");
      setError(failure instanceof ApiError ? failure.message : "The file could not be made.");
    }
  };

  return (
    <div className="flex flex-wrap items-center gap-2">
      <button
        type="button"
        data-testid="export-csv"
        disabled={disabled || status === "working"}
        onClick={download}
        className="btn"
      >
        {status === "working" ? "Preparing CSV…" : "Export CSV"}
      </button>
      {status === "failed" ? (
        <span role="alert" className="text-table text-negative">
          Export failed: {error}
        </span>
      ) : null}
    </div>
  );
}
