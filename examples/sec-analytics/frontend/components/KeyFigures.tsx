import { KindBadge } from "@/components/SourceBadge";
import { ValueCell } from "@/components/ValueCell";
import { findFigure } from "@/lib/display";
import { changeDirection, formatFiscalYear, formatSignedPercent, unitCaption } from "@/lib/format";
import type { MetricValue } from "@/lib/types";

const FIGURES = [
  { id: "revenue", label: "Latest annual revenue", change: "revenue_growth" },
  { id: "revenue_growth", label: "Revenue growth (YoY)", change: "revenue_growth" },
  { id: "net_income", label: "Latest annual net income" },
  { id: "net_margin", label: "Net margin" },
  { id: "operating_cash_flow", label: "Operating cash flow" },
  { id: "fcf", label: "Free cash flow (FCF)" },
  { id: "debt_to_equity", label: "Debt-to-equity" },
] as const;

/**
 * The year-on-year change line: the backend's revenue growth for the same period, with an arrow, a sign and the word
 * "up" or "down", so the direction never depends on colour. Nothing is computed here; when the backend has no growth
 * for that exact period, the line is left out.
 */
function Change({ change, period, showValue }: { change: MetricValue | null; period: string; showValue: boolean }) {
  if (!change || change.status !== "ok" || change.value === null || change.period_end !== period) return null;
  const direction = changeDirection(change.value);
  const tone = direction === "up" ? "text-positive" : direction === "down" ? "text-negative" : "text-muted";
  const arrow = direction === "up" ? "▲" : direction === "down" ? "▼" : "▶";
  return (
    <p data-testid="figure-change" data-direction={direction} className="text-table text-muted">
      <span aria-hidden="true" className={`mr-1 text-[0.625rem] ${tone}`}>
        {arrow}
      </span>
      {showValue ? <span className={`mr-1 font-semibold tabular-nums ${tone}`}>{formatSignedPercent(change.value)}</span> : null}
      {direction === "flat" ? "unchanged vs prior year" : `${showValue ? "" : direction === "up" ? "Up " : "Down "}vs prior year`}
    </p>
  );
}

function Figure({ label, metric, change }: { label: string; metric: MetricValue | null; change: MetricValue | null }) {
  return (
    <div className="card flex min-w-0 flex-col gap-1 px-3.5 py-3">
      <p className="flex flex-wrap items-center justify-between gap-1">
        <span className="label-caps text-muted">{label}</span>
        {metric ? <KindBadge kind={metric.kind} /> : null}
      </p>
      {metric ? (
        <>
          <p className="flex flex-wrap items-baseline gap-x-1.5 text-display font-semibold tracking-tight">
            <ValueCell metric={metric} />
            {metric.status === "ok" && metric.unit !== "percent" && metric.unit !== "ratio" ? <span className="text-table font-normal tracking-normal text-muted">{unitCaption(metric.unit)}</span> : null}
          </p>
          <Change change={change} period={metric.period_end} showValue={change !== metric} />
          <p className="num mt-auto whitespace-normal! pt-1 text-left text-xs text-muted">{formatFiscalYear(metric.fiscal_year_label, metric.period_end)}</p>
        </>
      ) : (
        <p className="mt-1 text-muted">Not available for this company.</p>
      )}
    </div>
  );
}

/** The key-figure strip: the latest usable annual values, each with its year, unit, kind and source tooltip. */
export function KeyFigures({ figures }: { figures: readonly MetricValue[] }) {
  return (
    <div className="@container">
      <div data-testid="key-figures" className="grid grid-cols-2 gap-2 @md:gap-3 @2xl:grid-cols-3 @3xl:grid-cols-4">
        {FIGURES.map((figure) => (
          <Figure key={figure.id} label={figure.label} metric={findFigure(figures, figure.id)} change={"change" in figure ? findFigure(figures, figure.change) : null} />
        ))}
      </div>
    </div>
  );
}
