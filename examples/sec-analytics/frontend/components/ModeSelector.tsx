"use client";

import { useCallback } from "react";

import { DEMO_LABEL, SourceBadge } from "@/components/SourceBadge";
import { api } from "@/lib/api";
import { useDataSource } from "@/lib/source";
import type { DataSourceChoice } from "@/lib/types";
import { useApiResource } from "@/lib/useApiResource";

export const LIVE_HELP =
  "Live asks SEC through this app's backend, at most once per second, and keeps answers for 24 hours. A class sharing one public IP address should use Demo.";

const OPTIONS: { value: DataSourceChoice; label: string }[] = [
  { value: "demo", label: "Demo" },
  { value: "live", label: "Live" },
];

/**
 * The app-wide data source: the mode badge, and under `npm run dev` the Demo / Live selector. It starts on Demo, and
 * only the person can change it; a failed live request does not switch it.
 */
export function ModeSelector() {
  const { source, setSource } = useDataSource();
  const loadMeta = useCallback((signal: AbortSignal) => api.getMeta({ signal }), []);
  const meta = useApiResource("meta", loadMeta);
  const offered = meta.status === "ok" && meta.data.live_available;

  return (
    <div className="flex flex-wrap items-center justify-end gap-2">
      {offered ? (
        <fieldset className="flex items-center gap-1" title={LIVE_HELP} data-testid="mode-selector">
          <legend className="label-caps float-left mr-1 text-muted">Data source</legend>
          {OPTIONS.map((option) => (
            <label
              key={option.value}
              className="toggle min-h-7!"
            >
              <input type="radio" name="data-source" value={option.value} checked={source === option.value} onChange={() => setSource(option.value)} className="sr-only" />
              {option.label}
            </label>
          ))}
        </fieldset>
      ) : null}
      {source === "live" ? <SourceBadge kind="live" label="LIVE" /> : <SourceBadge kind="demo" label={DEMO_LABEL} />}
    </div>
  );
}
