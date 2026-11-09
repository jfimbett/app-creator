// TypeScript mirrors of the backend's pydantic models (milestones/architecture.md "API", brief §5).
// Dates are ISO strings "YYYY-MM-DD"; timestamps are ISO 8601 in UTC with a "Z".
// Money values are whole currency units (USD, not millions); the UI scales them for display.

/** The person's choice of data: recorded demo data or live SEC. */
export type DataSourceChoice = "demo" | "live";

/** Where the data on a panel comes from. */
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

/** One metric the explorer can show. GET /api/metrics */
export interface MetricInfo {
  id: string;
  label: string;
  unit_kind: "currency" | "ratio" | "percent";
  kind: MetricKind;
  formula: string | null;
  concepts: string[];
}

export interface MetricsCatalog {
  metrics: MetricInfo[];
}

/** An annual period, identified by its dates. */
export interface PeriodInfo {
  fiscal_year_label: string;
  start: string;
  end: string;
}

/** One row of a statement summary: one value per period, in the order of `periods`. */
export interface Line {
  metric_id: string;
  label: string;
  kind: MetricKind;
  unit: string;
  values: MetricValue[];
}

/** GET /api/companies/{cik}/financials */
export interface FinancialsResponse {
  cik: string;
  currency: string | null;
  fiscal_year_end: string | null;
  periods: PeriodInfo[];
  statements: { income: Line[]; balance: Line[]; cash_flow: Line[] };
  ratios: Line[];
  notes: string[];
  source: SourceInfo;
}

export interface MetricSeries {
  metric_id: string;
  label: string;
  unit: string;
  kind: MetricKind;
  formula: string | null;
  points: MetricValue[];
}

/** GET /api/companies/{cik}/metrics */
export interface MetricSeriesResponse {
  cik: string;
  series: MetricSeries[];
  source: SourceInfo;
}

/** One 10-K or 10-Q from a company's SEC list. The addresses are null if SEC lists no primary document. */
export interface FilingMeta {
  accession: string;
  form: string;
  is_amendment: boolean;
  filing_date: string;
  report_date: string | null;
  primary_document: string | null;
  document_url: string | null;
  index_url: string;
  /** Demo: whether the full document is recorded. Live: null. */
  document_in_snapshot: boolean | null;
}

export interface LatestFilings {
  annual: FilingMeta | null;
  quarterly: FilingMeta | null;
  annual_amended_by: FilingMeta | null;
  quarterly_amended_by: FilingMeta | null;
  label: string;
}

export interface FilingsResponse {
  cik: string;
  latest: LatestFilings;
  history: FilingMeta[];
  coverage: { from_date: string | null; to_date: string | null; complete: boolean; note: string | null };
  source: SourceInfo;
}

export interface FilingSection {
  id: string;
  item: string;
  title: string;
  block_start: number;
}

export type FilingBlockKind = "text" | "heading" | "table_row";

/** Plain text from a filing. It is shown as text, never as HTML. */
export interface FilingBlock {
  id: number;
  section_id: string | null;
  kind: FilingBlockKind;
  text: string;
}

export interface FilingDocumentResponse {
  meta: FilingMeta;
  section_status: "detected" | "not_detected";
  note: string;
  sections: FilingSection[];
  blocks: FilingBlock[];
  source_link: string;
  scope: string;
  truncated: boolean;
  document_retrieved_at: string;
  amends: FilingMeta | null;
  amended_by: FilingMeta | null;
  source: SourceInfo;
}

// ------------------------------------------------------------------ M4 comparison (GET /api/compare)

export interface CompareCompany {
  cik: string;
  ticker: string;
  name: string;
  /** MM-DD of the company's latest period end in the window, or null without data. */
  fiscal_year_end: string | null;
  currency: string | null;
}

/** One data point. `unit` is a currency code, "index" or "ratio"; `value` is null unless status is "ok". */
export interface CompareRow {
  cik: string;
  metric_id: string;
  fiscal_year_label: string;
  period_start: string | null;
  period_end: string;
  value: number | null;
  unit: string;
  kind: "reported" | "derived";
  status: "ok" | "missing" | "unavailable" | "not_meaningful";
  reason: string | null;
  indexed: boolean;
  source_concept: string | null;
  accession: string | null;
  data_source: string;
}

export interface CompareWarning {
  code: "fiscal_years_not_aligned" | "currencies_differ" | "no_common_fiscal_year" | "index_base_unavailable";
  message: string;
}

export interface CompareResponse {
  companies: CompareCompany[];
  metrics: string[];
  rows: CompareRow[];
  index_base: { fiscal_year_by_cik: Record<string, string>; period_end_by_cik: Record<string, string> } | null;
  warnings: CompareWarning[];
  /** True when "Index = 100 at first common fiscal year" can be used for these companies and metrics. */
  index_available: boolean;
  source: SourceInfo;
}

// ------------------------------------------------------------------ M5 AI analyst (/api/ai/*)
// The OpenRouter key is never part of these shapes: the browser sends it only in the X-OpenRouter-Key header.

/** One model from GET /api/ai/models. Prices are USD per million tokens as decimal strings, or null. */
export interface AiModel {
  id: string;
  name: string;
  context_length: number | null;
  prompt_usd_per_million: string | null;
  completion_usd_per_million: string | null;
  /** "YYYY-MM-DD" when OpenRouter has announced the model's retirement. */
  expiration_date: string | null;
}

export interface AiModelsResponse {
  models: AiModel[];
  fetched_at: string;
}

/** POST /api/ai/test-connection */
export interface AiConnectionResponse {
  ok: boolean;
  label: string | null;
  limit_remaining_usd: number | null;
  message: string;
}

/** What the analyst may use: one company, one filing, or the current comparison. */
export type AiScope =
  | { kind: "company"; cik: string }
  | { kind: "filing"; cik: string; accession: string }
  | { kind: "comparison"; ciks: string[]; metrics: string[] };

/** POST /api/ai/context, and the `context` of a chat answer: the line is built by the server. */
export interface AiContext {
  line: string;
  facts: number;
  passages: number;
  chars: number;
}

export interface AiCitation {
  source_id: string;
  valid: boolean;
  kind: "fact" | "passage";
  label: string;
  period: string;
  date: string | null;
  /** An app path, e.g. /companies/0000320193 or …/filings/<accession>#block-12. */
  link: string;
}

export interface AiChatRequest {
  model: string;
  scope: AiScope;
  question: string;
  source: DataSourceChoice;
}

/** POST /api/ai/chat. A refusal is a 200 with `refusal` set and an empty answer. */
export interface AiChatResponse {
  answer: string;
  citations: AiCitation[];
  invalid_references: string[];
  citation_note: string | null;
  refusal: { code: string; message: string } | null;
  context: AiContext;
  model: string;
  usage: { prompt_tokens: number; completion_tokens: number; cost: number | null } | null;
  finish_reason: string | null;
  notice: string;
}
