// TypeScript mirrors of the backend's pydantic models (milestones/architecture.md "API", brief §5).
// Dates are ISO strings "YYYY-MM-DD"; timestamps are ISO 8601 in UTC with a "Z".
// Money values are whole currency units (USD, not millions); the UI scales them for display.

/** Where the data on a panel comes from. At M1 `mode` is always "demo". */
export interface SourceInfo {
  mode: "demo" | "live" | "cached";
  label: string;
  retrieved_at: string | null;
  snapshot_date: string | null;
  source_urls: string[];
}

/** The SEC fact a reported value was taken from. */
export interface Provenance {
  concept: string;
  taxonomy: string;
  unit: string;
  start: string | null;
  end: string;
  form: string;
  accession: string;
  filed: string;
  fy: number | null;
  fp: string | null;
  source_url: string;
}

export type MetricKind = "reported" | "derived";
export type MetricStatus = "ok" | "missing" | "unavailable" | "not_meaningful";

/** One value for one period. `value` is null whenever `status` is not "ok"; it is never 0 for missing. */
export interface MetricValue {
  metric_id: string;
  period_start: string | null;
  period_end: string;
  fiscal_year_label: string;
  value: number | null;
  unit: string;
  kind: MetricKind;
  status: MetricStatus;
  reason: string | null;
  formula: string | null;
  inputs: MetricValue[];
  provenance: Provenance | null;
  note: string | null;
}

/** Body of every error answer: `{"error": {...}}`. */
export interface ErrorEnvelope {
  error: {
    code: string;
    message: string;
    details: Record<string, unknown> | null;
    reference: string | null;
  };
}

/** GET /api/health */
export interface HealthResponse {
  status: "ok";
  app: string;
}

export interface DemoCompany {
  cik: string;
  ticker: string;
  name: string;
}

/** GET /api/meta */
export interface MetaResponse {
  data_mode: "fixtures" | "live";
  live_available: boolean;
  live_configured: boolean;
  snapshot_date: string;
  demo_universe: DemoCompany[];
}

export type SearchMatchKind = "ticker" | "name" | "cik";

export interface SearchResult {
  cik: string;
  ticker: string;
  name: string;
  match: SearchMatchKind;
}

/** GET /api/companies/search */
export interface SearchResponse {
  query: string;
  results: SearchResult[];
  universe_note: string;
  source: SourceInfo;
}

/** A former company name as listed in the SEC submissions file. */
export interface FormerName {
  name: string;
  from: string | null;
  to: string | null;
}

/** GET /api/companies/{cik} */
export interface CompanyProfile {
  cik: string;
  name: string;
  tickers: string[];
  exchanges: string[];
  sic: string | null;
  sic_description: string | null;
  /** "MMDD", e.g. "0928"; shown as "09-28". */
  fiscal_year_end: string | null;
  state_of_incorporation: string | null;
  former_names: FormerName[];
  source: SourceInfo;
}

/** One fiscal year in the overview chart and table. */
export interface OverviewChartRow {
  fiscal_year_label: string;
  period_end: string;
  revenue: MetricValue;
  net_income: MetricValue;
}

/** GET /api/companies/{cik}/overview */
export interface OverviewResponse {
  cik: string;
  key_figures: MetricValue[];
  chart: OverviewChartRow[];
  notes: string[];
  source: SourceInfo;
}
