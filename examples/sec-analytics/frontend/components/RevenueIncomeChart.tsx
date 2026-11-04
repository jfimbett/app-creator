"use client";

import { useState } from "react";
import { CartesianGrid, Legend, Line, LineChart, ReferenceLine, ResponsiveContainer, Tooltip, type TooltipContentProps, XAxis, YAxis } from "recharts";

import { ProvenanceTip } from "@/components/ProvenanceTip";
import { SourceBadge } from "@/components/SourceBadge";
import type { ChartPoint } from "@/lib/display";
import { formatDate, formatFiscalYear, formatMillions } from "@/lib/format";
import type { MetricValue } from "@/lib/types";

export type YearRange = "last5" | "all";

const SERIES = [
  { key: "revenue", name: "Revenue", color: "var(--series-revenue)", metric: (p: ChartPoint) => p.row.revenue },
  { key: "netIncome", name: "Net income", color: "var(--series-net-income)", metric: (p: ChartPoint) => p.row.net_income },
] as const;

type SeriesKey = (typeof SERIES)[number]["key"];

const RANGES: { value: YearRange; label: string }[] = [
  { value: "last5", label: "Last 5 years" },
  { value: "all", label: "All available" },
];

/** Chart tooltip: fiscal year with its end date, then each visible series with value and unit. */
function ChartTooltip({ active, payload }: TooltipContentProps) {
  const point = payload?.[0]?.payload as ChartPoint | undefined;
  if (!active || !point) return null;
  return (
    <div className="border border-line bg-panel-raised px-2 py-1.5 text-table text-fg shadow-lg shadow-black/40">
      <p className="font-semibold">{formatFiscalYear(point.label, point.periodEnd)}</p>
      {SERIES.filter((s) => payload.some((entry) => entry.dataKey === s.key)).map((s) => {
        const metric = s.metric(point);
        return (
          <p key={s.key} className="flex justify-between gap-4">
            <span>
              <span aria-hidden="true" style={{ color: s.color }}>
                ━{" "}
              </span>
              {s.name}
            </span>
            <span className="num">
              {metric.status === "ok" ? `${formatMillions(metric.value)} ${metric.unit} millions` : `— MISSING · ${metric.reason ?? "not reported"}`}
            </span>
          </p>
        );
      })}
    </div>
  );
}

function ValueCell({ metric }: { metric: MetricValue }) {
  if (metric.status !== "ok" || metric.value === null) {
    return (
      <span className="inline-flex items-center gap-1">
        <span>—</span>
        <SourceBadge kind="missing" reason={metric.reason} />
      </span>
    );
  }
  return (
    <ProvenanceTip metric={metric} className="num">
      {formatMillions(metric.value)}
    </ProvenanceTip>
  );
}

type Props = {
  points: ChartPoint[];
  /** The reporting currency of the values, e.g. "USD". */
  unit: string;
  range: YearRange;
  onRangeChange: (range: YearRange) => void;
  notes: string[];
};

/**
 * "Revenue and net income, USD, by fiscal year": a line chart with series toggles and a year-range selector,
 * and the same values in a table underneath. A missing year is a gap, never a zero; zero is always on the axis.
 */
export function RevenueIncomeChart({ points, unit, range, onRangeChange, notes }: Props) {
  const [visible, setVisible] = useState<Record<SeriesKey, boolean>>({ revenue: true, netIncome: true });
  const first = points[0];
  const last = points[points.length - 1];
  const noneVisible = !visible.revenue && !visible.netIncome;

  return (
    <div data-testid="overview-chart" className="flex flex-col gap-3">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div role="group" aria-label="Series shown" className="flex flex-wrap gap-1">
          {SERIES.map((s) => (
            <button
              key={s.key}
              type="button"
              aria-pressed={visible[s.key]}
              onClick={() => setVisible((v) => ({ ...v, [s.key]: !v[s.key] }))}
              className={`inline-flex items-center gap-1.5 rounded-sm border px-2 py-0.5 text-table ${visible[s.key] ? "border-accent text-fg" : "border-line text-muted line-through"}`}
            >
              <span aria-hidden="true" style={{ color: s.color }}>
                ━
              </span>
              {s.name}
            </button>
          ))}
        </div>
        <fieldset className="flex items-center gap-1">
          <legend className="sr-only">Years shown</legend>
          {RANGES.map((r) => (
            <label
              key={r.value}
              className={`cursor-pointer rounded-sm border px-2 py-0.5 text-table has-[:focus-visible]:outline-2 has-[:focus-visible]:outline-offset-2 has-[:focus-visible]:outline-accent ${range === r.value ? "border-accent bg-accent text-on-accent" : "border-line text-fg"}`}
            >
              <input type="radio" name="year-range" value={r.value} checked={range === r.value} onChange={() => onRangeChange(r.value)} className="sr-only" />
              {r.label}
            </label>
          ))}
        </fieldset>
      </div>

      <p className="sr-only">
        Line chart of revenue and net income in {unit} millions, {first?.label} to {last?.label}. The same values are in the table below.
      </p>
      <div aria-hidden="true" className="h-[280px] w-full min-w-0">
        {noneVisible ? (
          <p className="flex h-full items-center justify-center text-muted">Both series are hidden. Turn on Revenue or Net income above.</p>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={points} margin={{ top: 8, right: 12, bottom: 4, left: 4 }}>
              <CartesianGrid stroke="var(--border)" strokeDasharray="2 4" vertical={false} />
              <XAxis dataKey="label" stroke="var(--text-muted)" tick={{ fill: "var(--text-muted)", fontSize: 11 }} tickLine={false} minTickGap={12} />
              <YAxis
                stroke="var(--text-muted)"
                tick={{ fill: "var(--text-muted)", fontSize: 11 }}
                tickFormatter={(value: number) => formatMillions(value)}
                domain={[(dataMin: number) => Math.min(0, dataMin), "auto"]}
                width={64}
                label={{ value: `${unit} millions`, angle: -90, position: "insideLeft", offset: 0, fill: "var(--text-muted)", fontSize: 11, dy: 40 }}
              />
              <ReferenceLine y={0} stroke="var(--text-muted)" />
              <Tooltip content={ChartTooltip} cursor={{ stroke: "var(--border)" }} />
              <Legend wrapperStyle={{ fontSize: 12, color: "var(--text)" }} />
              {SERIES.map((s) => (
                <Line
                  key={s.key}
                  type="linear"
                  dataKey={s.key}
                  name={s.name}
                  stroke={s.color}
                  strokeWidth={2}
                  dot={{ r: 2.5, fill: s.color }}
                  activeDot={{ r: 4 }}
                  connectNulls={false}
                  hide={!visible[s.key]}
                  isAnimationActive={false}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>

      {notes.map((note) => (
        <p key={note} className="text-table text-muted">
          {note}
        </p>
      ))}

      <div className="table-scroll max-h-[360px] overflow-y-auto">
        <table className="data-table">
          <caption className="sr-only">Revenue and net income by fiscal year, {unit} millions</caption>
          <thead>
            <tr>
              <th scope="col">Fiscal year</th>
              <th scope="col" className="num">Period end</th>
              <th scope="col" className="num">Revenue ({unit} millions)</th>
              <th scope="col" className="num">Net income ({unit} millions)</th>
            </tr>
          </thead>
          <tbody>
            {points.map((p) => (
              <tr key={p.periodEnd}>
                <th scope="row" className="text-left font-normal">
                  {p.label}
                </th>
                <td className="num">{formatDate(p.periodEnd)}</td>
                <td className="num">
                  <ValueCell metric={p.row.revenue} />
                </td>
                <td className="num">
                  <ValueCell metric={p.row.net_income} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

