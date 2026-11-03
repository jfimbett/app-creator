/**
 * Text badge saying where a value or panel comes from (brief §4). The meaning is always in the words,
 * never in the colour alone.
 *
 * Kinds at M1:
 *  - "demo":      RECORDED SEC DEMO · snapshot <date>   (pass `label` from SourceInfo.label when you have it)
 *  - "synthetic": SYNTHETIC TEST DATA                    (a manifest marked synthetic)
 *  - "missing":   MISSING · <reason>                     (a value SEC did not report for that period)
 */
export type SourceBadgeProps =
  | { kind: "demo"; snapshotDate?: string | null; label?: string; className?: string }
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
    case "synthetic":
      return props.label || SYNTHETIC_LABEL;
    case "missing":
      return props.reason ? `${MISSING_LABEL} · ${props.reason}` : `${MISSING_LABEL} · not reported by SEC`;
  }
}

const TONE: Record<SourceBadgeProps["kind"], string> = {
  demo: "border-warning text-warning",
  synthetic: "border-negative text-negative",
  missing: "border-dashed border-line text-muted",
};

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
