import { ProvenanceTip } from "@/components/ProvenanceTip";
import { SourceBadge } from "@/components/SourceBadge";
import { findFigure } from "@/lib/display";
import { formatFiscalYear, formatMillions } from "@/lib/format";
import type { MetricValue } from "@/lib/types";

const FIGURES = [
  { id: "revenue", label: "Latest annual revenue" },
  { id: "net_income", label: "Latest annual net income" },
] as const;

function Figure({ label, metric }: { label: string; metric: MetricValue | null }) {
  const ok = metric?.status === "ok" && metric.value !== null;
  return (
    <div className="min-w-0 border border-line bg-panel-raised px-3 py-2">
      <p className="label-caps text-muted">{label}</p>
      {metric && ok ? (
        <>
          <p className="mt-1 text-[1.375rem] font-semibold leading-7">
            <ProvenanceTip metric={metric} className="num">
              {formatMillions(metric.value)}
            </ProvenanceTip>{" "}
            <span className="text-table font-normal text-muted">{metric.unit} millions</span>
          </p>
          <p className="num text-left text-table text-muted">{formatFiscalYear(metric.fiscal_year_label, metric.period_end)}</p>
        </>
      ) : (
        <p className="mt-1 flex flex-wrap items-center gap-2">
          <span className="text-[1.375rem] leading-7">—</span>
          <SourceBadge kind="missing" reason={metric?.reason ?? "not in the snapshot"} />
        </p>
      )}
    </div>
  );
}

/** The key-figure strip: the latest reported annual revenue and net income, each with its year and unit. */
export function KeyFigures({ figures }: { figures: readonly MetricValue[] }) {
  return (
    <div data-testid="key-figures" className="grid grid-cols-1 gap-2 sm:grid-cols-2">
      {FIGURES.map((figure) => (
        <Figure key={figure.id} label={figure.label} metric={findFigure(figures, figure.id)} />
      ))}
    </div>
  );
}
