"use client";

import { useState } from "react";
import { Bar, BarChart, CartesianGrid, Cell, Legend, Line, LineChart, ReferenceLine, ResponsiveContainer, Tooltip, type TooltipContentProps, XAxis, YAxis } from "recharts";

import { metricLabel, MONEY_METRICS, PERCENT_METRICS } from "@/lib/compare-state";
import { barDefaultLabel, cellText, chartPoints, indexLabel, rowAt, rowUnitCaption, SERIES_COLOURS, sharedAxisBlocked } from "@/lib/compare-view";
import { formatMillions, formatPercent, formatPeriod, formatTimes } from "@/lib/format";
import type { CompareResponse } from "@/lib/types";

function axisText(value: number, metric: string, indexed: boolean): string {
  if (indexed) return value.toFixed(0);
  if (MONEY_METRICS.has(metric)) return formatMillions(value);
  if (PERCENT_METRICS.has(metric)) return formatPercent(value);
  return formatTimes(value);
}

function RowTooltip({ response, metric, cik, label }: { response: CompareResponse; metric: string; cik: string; label: string }) {
  const row = rowAt(response, cik, metric, label);
  const company = response.companies.find((item) => item.cik === cik);
  if (!row || !company) return null;
  return (
    <div className="border-t border-line pt-1 first:border-t-0 first:pt-0">
      <p className="font-semibold">
        {company.ticker || company.cik} · {row.fiscal_year_label}
      </p>
      <p className="text-muted">{formatPeriod(row.period_start, row.period_end)}</p>
      <p>
        {cellText(row)} {row.status === "ok" ? rowUnitCaption(metric, row.unit, row.indexed) : `(${row.reason ?? "no reason given"})`}
      </p>
      <p className="text-muted">
        {row.kind}
        {row.indexed ? ", indexed" : ""}
      </p>
    </div>
  );
}

/**
 * Charts of one metric: a line per company over its own fiscal year labels (trend), or bars for one fiscal year
 * label. The zero line is drawn; a missing value is a gap or an absent bar, never zero. Money in different
 * currencies is not drawn on one axis.
 */
export function CompareChart({ response }: { response: CompareResponse }) {
  const [metric, setMetric] = useState(response.metrics[0]);
  const [view, setView] = useState<"trend" | "year">("trend");
  const current = response.metrics.includes(metric) ? metric : response.metrics[0];
  const indexed = response.rows.some((row) => row.metric_id === current && row.indexed);
  const points = chartPoints(response, current);
  const defaultYear = barDefaultLabel(response, current);
  const [chosenYear, setChosenYear] = useState<string | null>(null);
  const year = chosenYear && points.some((point) => point.label === chosenYear) ? chosenYear : (defaultYear ?? points.at(-1)?.label ?? null);
  const blocked = sharedAxisBlocked(response, current);
  const name = metricLabel(current);
  const title = (indexed ? indexLabel(response, name) : null) ?? name;
  const unit = rowUnitCaption(current, response.companies[0]?.currency ?? "", indexed);
  const domain: [(min: number) => number, (max: number) => number] = [(min) => Math.min(0, min), (max) => Math.max(0, max)];

  const tooltip = (label: string, ciks: string[]) => (
    <div className="popover flex max-w-xs flex-col gap-1 px-2.5 py-2 text-table">
      {ciks.map((cik) => (
        <RowTooltip key={cik} response={response} metric={current} cik={cik} label={label} />
      ))}
    </div>
  );
  const trendTooltip = ({ active, label }: TooltipContentProps) =>
    active && typeof label === "string" ? tooltip(label, response.companies.map((company) => company.cik)) : null;
  const barTooltip = ({ active, payload }: TooltipContentProps) => {
    const cik = (payload?.[0]?.payload as { cik?: string } | undefined)?.cik;
    return active && cik && year ? tooltip(year, [cik]) : null;
  };
  const bars = response.companies.map((company, index) => {
    const row = year ? rowAt(response, company.cik, current, year) : undefined;
    return { cik: company.cik, ticker: company.ticker || company.cik, value: row && row.status === "ok" ? row.value : null, colour: SERIES_COLOURS[index] };
  });

  return (
    <div className="flex flex-col gap-2">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div role="tablist" aria-label="Chart metric" className="flex flex-wrap gap-1">
          {response.metrics.map((id) => (
            <button
              key={id}
              type="button"
              role="tab"
              aria-selected={id === current}
              onClick={() => setMetric(id)}
              className={`btn ${id === current ? "border-accent! font-semibold shadow-[inset_0_-2px_0_var(--accent)]" : "text-muted!"}`}
            >
              {metricLabel(id)}
            </button>
          ))}
        </div>
        <div role="group" aria-label="Chart view" className="flex gap-1">
          {(["trend", "year"] as const).map((choice) => (
            <button
              key={choice}
              type="button"
              aria-pressed={view === choice}
              onClick={() => setView(choice)}
              className="toggle"
            >
              {choice === "trend" ? "Trend" : "One year"}
            </button>
          ))}
        </div>
      </div>

      <figure data-testid="compare-chart" data-metric={current} data-view={view} className="min-w-0">
        <figcaption className="flex flex-wrap items-baseline gap-x-2 text-table">
          {indexed ? (
            <span data-testid="chart-indexed-badge" className="tag border-accent! text-accent!">
              INDEXED
            </span>
          ) : null}
          <span data-testid="chart-title" className="font-semibold">
            {title}
          </span>
          <span className="text-muted">{blocked ? "" : unit}</span>
          {response.warnings.some((warning) => warning.code === "fiscal_years_not_aligned") ? (
            <span data-testid="chart-not-aligned" className="text-warning">
              · Fiscal years are not aligned
            </span>
          ) : null}
        </figcaption>
        {blocked ? (
          <p data-testid="chart-blocked" className="mt-2 text-table text-warning">
            <span aria-hidden="true">⚠ </span>
            {response.warnings.find((warning) => warning.code === "currencies_differ")?.message}. No shared axis is drawn; the table shows each value in its own currency. Ratios can still be charted.
          </p>
        ) : view === "trend" ? (
          <div aria-hidden="true" className="h-[260px] w-full min-w-0">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={points} margin={{ top: 8, right: 12, bottom: 0, left: 4 }}>
                <CartesianGrid stroke="var(--border)" strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="label" stroke="var(--border-strong)" tick={{ fill: "var(--text-muted)", fontSize: 11 }} tickLine={false} minTickGap={6} />
                <YAxis stroke="var(--border-strong)" tickLine={false} axisLine={false} tick={{ fill: "var(--text-muted)", fontSize: 11 }} tickFormatter={(value: number) => axisText(value, current, indexed)} domain={domain} width={64} />
                <ReferenceLine y={0} stroke="var(--text-muted)" />
                {indexed ? <ReferenceLine y={100} stroke="var(--border)" strokeDasharray="4 4" /> : null}
                <Tooltip content={trendTooltip} cursor={{ stroke: "var(--border-strong)", strokeDasharray: "3 3" }} />
                <Legend iconType="plainline" wrapperStyle={{ fontSize: 12, color: "var(--text-muted)", paddingTop: 4 }} />
                {response.companies.map((company, index) => (
                  <Line
                    key={company.cik}
                    type="linear"
                    dataKey={company.cik}
                    name={company.ticker || company.cik}
                    stroke={SERIES_COLOURS[index]}
                    strokeWidth={2}
                    dot={{ r: 2.5, fill: SERIES_COLOURS[index], strokeWidth: 0 }}
                    activeDot={{ r: 4.5, stroke: "var(--panel)", strokeWidth: 2 }}
                    connectNulls={false}
                    isAnimationActive={false}
                  />
                ))}
              </LineChart>
            </ResponsiveContainer>
          </div>
        ) : (
          <div className="flex flex-col gap-1">
            <label className="flex items-center gap-1.5 text-table">
              <span className="label-caps text-muted">Fiscal year</span>
              <select value={year ?? ""} onChange={(event) => setChosenYear(event.target.value)} className="field py-0.5">
                {points.map((point) => (
                  <option key={point.label} value={point.label}>
                    {point.label}
                  </option>
                ))}
              </select>
              <span className="text-muted">each company&apos;s own fiscal year with this label</span>
            </label>
            <div aria-hidden="true" className="h-[240px] w-full min-w-0">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={bars} margin={{ top: 8, right: 12, bottom: 0, left: 4 }}>
                  <CartesianGrid stroke="var(--border)" strokeDasharray="3 3" vertical={false} />
                  <XAxis dataKey="ticker" stroke="var(--border-strong)" tick={{ fill: "var(--text-muted)", fontSize: 11 }} tickLine={false} />
                  <YAxis stroke="var(--border-strong)" tickLine={false} axisLine={false} tick={{ fill: "var(--text-muted)", fontSize: 11 }} tickFormatter={(value: number) => axisText(value, current, indexed)} domain={domain} width={64} />
                  <ReferenceLine y={0} stroke="var(--text-muted)" />
                  <Tooltip content={barTooltip} cursor={{ fill: "var(--panel-raised)" }} />
                  <Bar dataKey="value" maxBarSize={96} isAnimationActive={false}>
                    {bars.map((bar) => (
                      <Cell key={bar.cik} fill={bar.colour} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
            {bars.some((bar) => bar.value === null) ? (
              <p className="text-table text-muted">No bar: {bars.filter((bar) => bar.value === null).map((bar) => bar.ticker).join(", ")} (no value for {year}; see the table).</p>
            ) : null}
          </div>
        )}
        <p className="sr-only">
          {name} by fiscal year:{" "}
          {response.companies
            .map((company) => `${company.ticker}: ${points.map((point) => `${point.label} ${typeof point[company.cik] === "number" ? axisText(point[company.cik] as number, current, indexed) : "no value"}`).join(", ")}`)
            .join("; ")}
          .
        </p>
      </figure>
    </div>
  );
}
