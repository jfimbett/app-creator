/**
 * A small inline-SVG trend line (no axes). It only places the given values on the drawing: a null is a gap in the
 * line, never a zero. Decorative next to a text that states the figure and its years (pass that text to readers).
 */
export function Sparkline({ values, width = 160, height = 40, stroke = "var(--series-1)" }: { values: readonly (number | null)[]; width?: number; height?: number; stroke?: string }) {
  const present = values.filter((value): value is number => value !== null);
  if (present.length < 2) return null;
  const low = Math.min(0, ...present);
  const high = Math.max(...present);
  const span = high - low || 1;
  const pad = 3;
  const x = (index: number) => pad + (index * (width - 2 * pad)) / Math.max(1, values.length - 1);
  const y = (value: number) => pad + ((high - value) * (height - 2 * pad)) / span;

  // One path segment per run of present values, so a missing year breaks the line.
  let d = "";
  let open = false;
  values.forEach((value, index) => {
    if (value === null) {
      open = false;
      return;
    }
    d += `${open ? "L" : "M"}${x(index).toFixed(1)},${y(value).toFixed(1)}`;
    open = true;
  });
  const lastIndex = values.findLastIndex((value) => value !== null);
  const last = values[lastIndex];

  return (
    <span aria-hidden="true" className="relative block" style={{ height }}>
      <svg width="100%" height={height} viewBox={`0 0 ${width} ${height}`} preserveAspectRatio="none" className="block overflow-visible">
        <line x1={pad} x2={width - pad} y1={y(0)} y2={y(0)} stroke="var(--border)" strokeWidth="1" vectorEffect="non-scaling-stroke" />
        <path d={d} fill="none" stroke={stroke} strokeWidth="2" strokeLinejoin="round" strokeLinecap="round" vectorEffect="non-scaling-stroke" />
      </svg>
      {/* The end dot is HTML, so the stretched drawing does not turn it into an ellipse. */}
      {last !== null && last !== undefined ? (
        <span
          className="absolute h-1.5 w-1.5 -translate-x-1/2 -translate-y-1/2 rounded-full"
          style={{ left: `${(x(lastIndex) / width) * 100}%`, top: `${(y(last) / height) * 100}%`, background: stroke }}
        />
      ) : null}
    </span>
  );
}
