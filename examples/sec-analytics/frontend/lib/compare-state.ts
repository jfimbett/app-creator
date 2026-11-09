// The Compare screen's state, kept in the page URL so a reload or a shared link shows the same comparison:
// /compare?ciks=0000320193,0000789019&metrics=revenue,net_margin&years=10&index=none&source=demo
// Pure functions: parsing, writing and the 2–4 companies rule the screen applies before asking the backend.

import type { DataSourceChoice } from "./types";

export type IndexChoice = "none" | "first_common_year";

export interface CompareState {
  ciks: string[];
  metrics: string[];
  years: number;
  index: IndexChoice;
  source: DataSourceChoice;
}

/** The comparison metrics, in the order the picker shows them, with their display names. */
export const COMPARE_METRICS: readonly { id: string; label: string }[] = [
  { id: "revenue", label: "Revenue" },
  { id: "revenue_growth", label: "Revenue growth" },
  { id: "operating_margin", label: "Operating margin" },
  { id: "net_margin", label: "Net margin" },
  { id: "operating_cash_flow", label: "Operating cash flow" },
  { id: "fcf", label: "Free cash flow (FCF)" },
  { id: "fcf_margin", label: "FCF margin" },
  { id: "debt_to_equity", label: "Debt-to-equity" },
];
/** Amounts in the reporting currency: the only metrics that can be indexed. */
export const MONEY_METRICS: ReadonlySet<string> = new Set(["revenue", "operating_cash_flow", "fcf"]);
export const PERCENT_METRICS: ReadonlySet<string> = new Set(["revenue_growth", "operating_margin", "net_margin", "fcf_margin"]);

export const MIN_COMPANIES = 2;
export const MAX_COMPANIES = 4;
export const MAX_METRICS = 6;
export const YEAR_CHOICES = [5, 6, 7, 8, 9, 10] as const;
export const COUNT_RULE = "Compare 2–4 companies";
export const ALREADY_ADDED = "Already in the comparison";
export const NEED_TWO = "Add at least 2 companies to compare";

export const DEFAULT_STATE: CompareState = {
  ciks: [],
  metrics: ["revenue", "net_margin"],
  years: 10,
  index: "none",
  source: "demo",
};

const KNOWN = new Set(COMPARE_METRICS.map((metric) => metric.id));

export function metricLabel(id: string): string {
  return COMPARE_METRICS.find((metric) => metric.id === id)?.label ?? id;
}

/** "320193", "CIK320193" or "0000320193" → "0000320193"; anything else → null (the backend rule). */
export function normalizeCik(raw: string): string | null {
  const text = raw.trim().replace(/^cik/i, "").trim();
  return /^\d{1,10}$/.test(text) ? text.padStart(10, "0") : null;
}

function list(value: string | null): string[] {
  return (value ?? "")
    .split(",")
    .map((part) => part.trim())
    .filter(Boolean);
}

/** The state from the URL. Anything unusable is dropped, never guessed. */
export function parseCompareState(params: URLSearchParams): CompareState {
  const ciks = [...new Set(list(params.get("ciks")).map(normalizeCik).filter((cik): cik is string => cik !== null))].slice(0, MAX_COMPANIES);
  const metrics = [...new Set(list(params.get("metrics")).filter((id) => KNOWN.has(id)))].slice(0, MAX_METRICS);
  const years = Number(params.get("years"));
  return {
    ciks,
    metrics: metrics.length > 0 ? metrics : DEFAULT_STATE.metrics,
    years: Number.isInteger(years) && years >= 5 && years <= 10 ? years : DEFAULT_STATE.years,
    index: params.get("index") === "first_common_year" ? "first_common_year" : "none",
    source: params.get("source") === "live" ? "live" : "demo",
  };
}

/** The URL query for a state, in a fixed order. */
export function serializeCompareState(state: CompareState): string {
  return new URLSearchParams({
    ciks: state.ciks.join(","),
    metrics: state.metrics.join(","),
    years: String(state.years),
    index: state.index,
    source: state.source,
  }).toString();
}

/** Add a company: refused past four ("Compare 2–4 companies"), ignored when already present. */
export function addCompany(state: CompareState, raw: string): { state: CompareState; message: string | null } {
  const cik = normalizeCik(raw);
  if (cik === null) return { state, message: null };
  if (state.ciks.includes(cik)) return { state, message: ALREADY_ADDED };
  if (state.ciks.length >= MAX_COMPANIES) return { state, message: COUNT_RULE };
  return { state: { ...state, ciks: [...state.ciks, cik] }, message: null };
}

export function removeCompany(state: CompareState, cik: string): CompareState {
  return { ...state, ciks: state.ciks.filter((item) => item !== cik) };
}

/** Turn a metric on or off, keeping 1 to 6 selected. */
export function toggleMetric(state: CompareState, id: string): CompareState {
  if (state.metrics.includes(id)) {
    return state.metrics.length > 1 ? { ...state, metrics: state.metrics.filter((item) => item !== id) } : state;
  }
  if (!KNOWN.has(id) || state.metrics.length >= MAX_METRICS) return state;
  return { ...state, metrics: [...state.metrics, id] };
}

/** True when there are enough companies to ask the backend for a comparison. */
export function canCompare(state: CompareState): boolean {
  return state.ciks.length >= MIN_COMPANIES;
}
