import { ProvenanceTip } from "@/components/ProvenanceTip";
import { formatMetric, formatMissing, UNAVAILABLE } from "@/lib/format";
import type { MetricValue } from "@/lib/types";

/**
 * One value in a table, card or list. Every state is in words, and every word opens the same tooltip with its
 * source, formula or reason. A value that is not there is never drawn as 0 and never left blank.
 */
export function ValueCell({ metric, className }: { metric: MetricValue; className?: string }) {
  if (metric.status === "ok" && metric.value !== null) {
    return (
      <ProvenanceTip metric={metric} className={`num ${className ?? ""}`}>
        {formatMetric(metric)}
      </ProvenanceTip>
    );
  }
  const text =
    metric.status === "missing"
      ? formatMissing(metric.reason)
      : metric.status === "not_meaningful"
        ? metric.reason || "n/m"
        : UNAVAILABLE;
  return (
    <ProvenanceTip metric={metric} className="inline-block max-w-[7.5rem] whitespace-normal text-right text-label leading-tight text-muted [overflow-wrap:anywhere]">
      <span data-status={metric.status}>{text}</span>
    </ProvenanceTip>
  );
}
