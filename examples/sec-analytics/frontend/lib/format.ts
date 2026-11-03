// Display formatting of finished values. No calculations here: values arrive computed from the backend.

/** True minus sign (U+2212), used instead of the hyphen for negative numbers. */
export const MINUS = "−";
/** Shown in place of any missing number or date; never 0 and never blank. */
export const DASH = "—";
/** Shown for a profile field the SEC submissions file does not contain. */
export const NOT_REPORTED = "Not reported by SEC";

const WHOLE = new Intl.NumberFormat("en-US", { maximumFractionDigits: 0 });
const ISO_DATE = /^(\d{4}-\d{2}-\d{2})(T.*)?$/;

function isNumber(value: number | null | undefined): value is number {
  return typeof value === "number" && Number.isFinite(value);
}

/** Whole-number formatting with thousands separators and a true minus sign; never "−0". */
function formatWhole(value: number): string {
  const rounded = Math.round(value);
  if (rounded === 0) return "0";
  const digits = WHOLE.format(Math.abs(rounded));
  return rounded < 0 ? `${MINUS}${digits}` : digits;
}

/** Money in whole currency units, shown in millions: 1,234,567,000,000 → "1,234,567". */
export function formatMillions(value: number | null): string {
  return isNumber(value) ? formatWhole(value / 1_000_000) : DASH;
}

/** The exact value with its unit, for tooltips: "1,234,567,000,000 USD". */
export function formatExact(value: number | null, unit: string): string {
  return isNumber(value) ? `${formatWhole(value)} ${unit}` : DASH;
}

/** An ISO date or timestamp as "YYYY-MM-DD"; anything else becomes the dash. */
export function formatDate(value: string | null): string {
  const match = value ? ISO_DATE.exec(value) : null;
  return match ? match[1] : DASH;
}

/** A period as "start – end". */
export function formatPeriod(start: string | null, end: string | null): string {
  return `${formatDate(start)} – ${formatDate(end)}`;
}

/** The SEC fiscal year-end "MMDD" as "MM-DD", or "Not reported by SEC". */
export function formatFiscalYearEnd(value: string | null): string {
  return value && /^\d{4}$/.test(value) ? `${value.slice(0, 2)}-${value.slice(2)}` : NOT_REPORTED;
}

/** A fiscal year label always shown with its end date: "FY2024 (ends 2024-09-28)". */
export function formatFiscalYear(label: string, periodEnd: string | null): string {
  return `${label} (ends ${formatDate(periodEnd)})`;
}

/** The text badge for a missing value: "MISSING · <reason>". */
export function formatMissing(reason: string | null): string {
  return `MISSING · ${reason || "not reported"}`;
}
