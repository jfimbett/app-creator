import { KindBadge } from "@/components/SourceBadge";
import { ValueCell } from "@/components/ValueCell";
import { findFigure } from "@/lib/display";
import { formatFiscalYear, unitCaption } from "@/lib/format";
import type { MetricValue } from "@/lib/types";

const FIGURES = [
  { id: "revenue", label: "Latest annual revenue" },
  { id: "revenue_growth", label: "Revenue growth (YoY)" },
  { id: "net_income", label: "Latest annual net income" },
  { id: "net_margin", label: "Net margin" },
  { id: "operating_cash_flow", label: "Operating cash flow" },
  { id: "fcf", label: "Free cash flow (FCF)" },
  { id: "debt_to_equity", label: "Debt-to-equity" },
] as const;

function Figure({ label, metric }: { label: string; metric: MetricValue | null }) {
  return (
    <div className="min-w-0 border border-line bg-panel-raised px-3 py-2">
      <p className="label-caps flex flex-wrap items-center justify-between gap-1 text-muted">
        <span>{label}</span>
        {metric ? <KindBadge kind={metric.kind} /> : null}
      </p>
      {metric ? (
        <>
          <p className="mt-1 flex flex-wrap items-baseline gap-x-1.5 text-[1.25rem] font-semibold leading-7">
            <ValueCell metric={metric} />
            {metric.status === "ok" && metric.unit !== "percent" && metric.unit !== "ratio" ? <span className="text-table font-normal text-muted">{unitCaption(metric.unit)}</span> : null}
          </p>
          <p className="num whitespace-normal! text-left text-table text-muted">{formatFiscalYear(metric.fiscal_year_label, metric.period_end)}</p>
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
    <div data-testid="key-figures" className="grid grid-cols-2 gap-2 xl:grid-cols-4">
      {FIGURES.map((figure) => (
        <Figure key={figure.id} label={figure.label} metric={findFigure(figures, figure.id)} />
      ))}
    </div>
  );
}
