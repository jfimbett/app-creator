"use client";

import { CartesianGrid, Line, LineChart, ReferenceLine, ResponsiveContainer, Tooltip, type TooltipContentProps, XAxis, YAxis } from "recharts";

import { formatAxis, formatFiscalYear, formatMetric, formatMissing, UNAVAILABLE, unitCaption } from "@/lib/format";
import type { MetricSeries, MetricValue } from "@/lib/types";

type Point = { label: string; value: number | null; metric: MetricValue };

function statusText(metric: MetricValue): string {
  if (metric.status === "ok") return formatMetric(metric);
  if (metric.status === "missing") return formatMissing(metric.reason);
  if (metric.status === "not_meaningful") return metric.reason || "n/m";
  return `${UNAVAILABLE}: ${metric.reason ?? "no reason given"}`;
}

function PointTooltip({ active, payload }: TooltipContentProps) {
  const point = payload?.[0]?.payload as Point | undefined;
  if (!active || !point) return null;
  const { metric } = point;
  return (
    <div className="max-w-xs border border-line bg-panel-raised px-2 py-1.5 text-table text-fg shadow-lg shadow-black/40">
      <p className="font-semibold">{formatFiscalYear(metric.fiscal_year_label, metric.period_end)}</p>
      <p className="num text-left">
        {statusText(metric)} {metric.status === "ok" && metric.unit !== "percent" && metric.unit !== "ratio" ? unitCaption(metric.unit) : ""}
      </p>
      {metric.provenance ? <p className="code-id text-muted [overflow-wrap:anywhere]">{metric.provenance.concept}</p> : null}
      {metric.formula ? <p className="text-muted">{metric.formula}</p> : null}
    </div>
  );
}

/**
 * One compact line chart for one metric. Each metric has its own chart, so currency and percentage series never
 * share an axis. The zero line is always drawn and a missing year is a gap, never a zero.
 */
export function MetricChart({ series, showAxis }: { series: MetricSeries; showAxis: boolean }) {
  const points: Point[] = series.points.map((metric) => ({
    label: metric.fiscal_year_label,
    value: metric.status === "ok" ? metric.value : null,
    metric,
  }));
  const plotted = points.filter((point) => point.value !== null).length;

  return (
    <figure data-testid="metric-chart" data-metric={series.metric_id} className="min-w-0">
      <figcaption className="flex flex-wrap items-baseline justify-between gap-x-2 text-table">
        <span className="font-semibold">{series.label}</span>
        <span className="text-muted">{unitCaption(series.unit)}</span>
      </figcaption>
      <p className="sr-only">
        {series.label} by fiscal year: {points.map((point) => `${point.label} ${statusText(point.metric)}`).join("; ")}.
      </p>
      {plotted === 0 ? (
        <p className="flex h-20 items-center text-muted">No value for this metric in these years. The table under “Show data” gives each reason.</p>
      ) : (
        <div aria-hidden="true" className={`${showAxis ? "h-[150px]" : "h-[125px]"} w-full min-w-0`}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={points} margin={{ top: 6, right: 12, bottom: 0, left: 4 }}>
              <CartesianGrid stroke="var(--border)" strokeDasharray="2 4" vertical={false} />
              <XAxis
                dataKey="label"
                stroke="var(--text-muted)"
                tick={showAxis ? { fill: "var(--text-muted)", fontSize: 11 } : false}
                height={showAxis ? 24 : 4}
                tickLine={false}
                minTickGap={8}
              />
              <YAxis
                stroke="var(--text-muted)"
                tick={{ fill: "var(--text-muted)", fontSize: 11 }}
                tickFormatter={(value: number) => formatAxis(value, series.unit)}
                domain={[(min: number) => Math.min(0, min), (max: number) => Math.max(0, max)]}
                width={64}
              />
              <ReferenceLine y={0} stroke="var(--text-muted)" />
              <Tooltip content={PointTooltip} cursor={{ stroke: "var(--border)" }} />
              <Line
                type="linear"
                dataKey="value"
                name={series.label}
                stroke="var(--series-revenue)"
                strokeWidth={2}
                dot={{ r: 2.5, fill: "var(--series-revenue)" }}
                activeDot={{ r: 4 }}
                connectNulls={false}
                isAnimationActive={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </figure>
  );
}
