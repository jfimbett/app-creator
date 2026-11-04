/**
 * Text badge saying where a value or panel comes from (brief §4). The meaning is always in the words,
 * never in the colour alone.
 *
 * Kinds at M1:
 *  - "demo":      RECORDED SEC DEMO · snapshot <date>   (pass `label` from SourceInfo.label when you have it)
 *  - "synthetic": SYNTHETIC TEST DATA                    (a manifest marked synthetic)
 *  - "missing":   MISSING · <reason>                     (a value SEC did not report for that period)
 */
import type { MetricKind, SourceInfo } from "@/lib/types";

export type SourceBadgeProps =
  | { kind: "demo"; snapshotDate?: string | null; label?: string; className?: string }
  | { kind: "live"; label: string; className?: string }
  | { kind: "cached"; label: string; className?: string }
  | { kind: "synthetic"; label?: string; className?: string }
  | { kind: "missing"; reason?: string | null; className?: string };

export const DEMO_LABEL = "RECORDED SEC DEMO";
export const SYNTHETIC_LABEL = "SYNTHETIC TEST DATA";
export const MISSING_LABEL = "MISSING";

/** The text shown in the badge; exported so other components and tests use the same wording. */
export function sourceBadgeText(props: SourceBadgeProps): string {
  switch (props.kind) {
    case "demo":
      if (props.label) return props.label;
      return props.snapshotDate ? `${DEMO_LABEL} · snapshot ${props.snapshotDate}` : DEMO_LABEL;
    case "live":
    case "cached":
      return props.label;
    case "synthetic":
      return props.label || SYNTHETIC_LABEL;
    case "missing":
      return props.reason ? `${MISSING_LABEL} · ${props.reason}` : `${MISSING_LABEL} · not reported by SEC`;
  }
}

const TONE: Record<SourceBadgeProps["kind"], string> = {
  demo: "border-warning text-warning",
  live: "border-positive text-positive",
  cached: "border-link text-link",
  synthetic: "border-negative text-negative",
  missing: "border-dashed border-line text-muted",
};

/** A panel's badge from the API's SourceInfo: the label says it all, and the colour only repeats it. */
export function InfoBadge({ source }: { source: SourceInfo }) {
  if (source.mode === "live") return <SourceBadge kind="live" label={source.label} />;
  if (source.mode === "cached") return <SourceBadge kind="cached" label={source.label} />;
  return source.label.startsWith(DEMO_LABEL) ? <SourceBadge kind="demo" label={source.label} /> : <SourceBadge kind="synthetic" label={source.label} />;
}

/** Whether a value is taken from a filing or calculated by the app. */
export function KindBadge({ kind }: { kind: MetricKind }) {
  return (
    <span data-testid="kind-badge" className="label-caps rounded-sm border border-line px-1 text-[0.625rem] leading-4 text-muted">
      {kind === "derived" ? "DERIVED" : "REPORTED"}
    </span>
  );
}

export function SourceBadge(props: SourceBadgeProps) {
  return (
    <span
      data-testid="source-badge"
      data-kind={props.kind}
      className={`label-caps inline-flex max-w-full items-center whitespace-normal rounded-sm border px-1.5 py-px leading-4 [overflow-wrap:anywhere] ${TONE[props.kind]} ${props.className ?? ""}`}
    >
      {sourceBadgeText(props)}
    </span>
  );
}
