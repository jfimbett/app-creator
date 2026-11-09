"use client";

import { useCallback, useState } from "react";

import { MetricChart } from "@/components/MetricChart";
import { StatePanel } from "@/components/StatePanel";
import { ValueCell } from "@/components/ValueCell";
import { api } from "@/lib/api";
import { formatDate, unitCaption } from "@/lib/format";
import type { DataSourceChoice, MetricInfo, MetricSeries } from "@/lib/types";
import { useApiResource } from "@/lib/useApiResource";

const MAX_SELECTED = 6;
const DEFAULT_SELECTED = ["revenue", "net_margin"];
const GROUPS: { title: string; kinds: (metric: MetricInfo) => boolean }[] = [
  { title: "Reported by SEC", kinds: (m) => m.kind === "reported" },
  { title: "Calculated", kinds: (m) => m.kind === "derived" },
];

function DataTable({ series }: { series: readonly MetricSeries[] }) {
  const periods = series[0]?.points ?? [];
  return (
    <div className="table-box max-h-[420px]">
      <table className="data-table" data-testid="explorer-data">
        <caption className="sr-only">The selected metrics by fiscal year</caption>
        <thead>
          <tr>
            <th scope="col">Fiscal year</th>
            <th scope="col" className="num">Period end</th>
            {series.map((item) => (
              <th key={item.metric_id} scope="col" className="num">
                {item.label} ({unitCaption(item.unit)})
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {periods.map((period, index) => (
            <tr key={period.period_end}>
              <th scope="row" className="text-left font-normal">
                {period.fiscal_year_label}
              </th>
              <td className="num">{formatDate(period.period_end)}</td>
              {series.map((item) => (
                <td key={item.metric_id} className="num">
                  <ValueCell metric={item.points[index]} />
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

/** Pick 1 to 6 metrics and see one chart per metric stacked on a shared fiscal-year axis, or the same points as a table. */
export function MetricExplorer({ cik, source, years }: { cik: string; source: DataSourceChoice; years: number }) {
  const [selected, setSelected] = useState<string[]>(DEFAULT_SELECTED);
  const [showData, setShowData] = useState(false);
  const idsKey = selected.join(",");

  const loadCatalog = useCallback((signal: AbortSignal) => api.getMetricCatalog({ signal }), []);
  const catalog = useApiResource("metric-catalog", loadCatalog);
  const loadSeries = useCallback(
    (signal: AbortSignal) => api.getMetricSeries(cik, idsKey.split(","), { signal, years, source }),
    [cik, idsKey, years, source],
  );
  const series = useApiResource(`metric-series:${cik}:${idsKey}:${years}:${source}`, loadSeries);

  const toggle = (id: string) =>
    setSelected((current) => {
      if (current.includes(id)) return current.length > 1 ? current.filter((item) => item !== id) : current;
      return current.length < MAX_SELECTED ? [...current, id] : current;
    });

  return (
    <div className="flex flex-col gap-4">
      {catalog.status === "loading" ? <StatePanel kind="loading" title="Loading the metric list…" rows={2} /> : null}
      {catalog.status === "error" ? <StatePanel kind="error" title="Could not load the metric list" message={catalog.error.message} action={{ label: "Try again", onClick: catalog.reload }} /> : null}
      {catalog.status === "ok" ? (
        <div className="flex flex-col gap-2">
          {GROUPS.map((group) => (
            <div key={group.title} role="group" aria-label={group.title}>
              <p className="label-caps mb-1.5 text-muted">{group.title}</p>
              <div className="flex flex-wrap gap-1.5">
                {catalog.data.metrics.filter(group.kinds).map((metric) => {
                  const on = selected.includes(metric.id);
                  return (
                    <button
                      key={metric.id}
                      type="button"
                      aria-pressed={on}
                      disabled={(!on && selected.length >= MAX_SELECTED) || (on && selected.length === 1)}
                      title={metric.formula ?? metric.concepts.join(" → ")}
                      onClick={() => toggle(metric.id)}
                      className="toggle"
                    >
                      {metric.label}
                    </button>
                  );
                })}
              </div>
            </div>
          ))}
          <p className="text-table text-muted" aria-live="polite">
            {selected.length} of {MAX_SELECTED} metrics selected.
          </p>
        </div>
      ) : null}

      {series.status === "loading" ? <StatePanel kind="loading" title="Loading the charts…" rows={6} /> : null}
      {series.status === "error" ? <StatePanel kind="error" title="Could not load the selected metrics" message={series.error.message} reference={series.error.reference} action={{ label: "Try again", onClick: series.reload }} /> : null}
      {series.status === "ok" ? (
        <>
          <div className="flex flex-col gap-4">
            {series.data.series.map((item, index) => (
              <MetricChart key={item.metric_id} series={item} showAxis={index === series.data.series.length - 1} />
            ))}
          </div>
          <div>
            <button type="button" aria-expanded={showData} onClick={() => setShowData((on) => !on)} className="btn">
              {showData ? "Hide data" : "Show data"}
            </button>
          </div>
          {showData ? <DataTable series={series.data.series} /> : null}
        </>
      ) : null}
    </div>
  );
}
