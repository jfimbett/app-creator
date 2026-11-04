#!/usr/bin/env python3
"""Exact frontend edits for M2 (kept as a record). Run from the frontend folder."""


def sub(path, pairs):
    s = open(path).read()
    for old, new in pairs:
        assert old in s, (path, old[:70])
        s = s.replace(old, new, 1)
    open(path, "w").write(s)


sub("lib/types.ts", [
    ('/** Where the data on a panel comes from. At M1 `mode` is always "demo". */',
     '/** The person\'s choice of data: recorded demo data or live SEC. */\nexport type DataSourceChoice = "demo" | "live";\n\n/** Where the data on a panel comes from. */'),
])
open("lib/types.ts", "a").write('''
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
''')

sub("lib/api.ts", [
    ('''import type {
  CompanyProfile,
  ErrorEnvelope,
  HealthResponse,
  MetaResponse,
  OverviewResponse,
  SearchResponse,
} from "./types";
''', '''import type {
  CompanyProfile,
  DataSourceChoice,
  ErrorEnvelope,
  FinancialsResponse,
  HealthResponse,
  MetaResponse,
  MetricSeriesResponse,
  MetricsCatalog,
  OverviewResponse,
  SearchResponse,
} from "./types";
'''),
    ('''export interface RequestOptions {
  signal?: AbortSignal;
}
''', '''export interface RequestOptions {
  signal?: AbortSignal;
}

/** Calls that can use live data say which source they want; demo is left off the URL. */
export interface SourceOptions extends RequestOptions {
  source?: DataSourceChoice;
}

function sourceParam(source: DataSourceChoice | undefined): DataSourceChoice | undefined {
  return source === "live" ? "live" : undefined;
}
'''),
    ('''    searchCompanies: (q: string, options: RequestOptions & { limit?: number } = {}) =>
      get<SearchResponse>("/companies/search", { q, limit: options.limit }, options),
    getCompany: (cik: string, options?: RequestOptions) =>
      get<CompanyProfile>(`/companies/${encodeURIComponent(cik)}`, {}, options),
    getOverview: (cik: string, options: RequestOptions & { years?: number } = {}) =>
      get<OverviewResponse>(`/companies/${encodeURIComponent(cik)}/overview`, { years: options.years }, options),
''', '''    searchCompanies: (q: string, options: SourceOptions & { limit?: number } = {}) =>
      get<SearchResponse>("/companies/search", { q, limit: options.limit, source: sourceParam(options.source) }, options),
    getCompany: (cik: string, options: SourceOptions = {}) =>
      get<CompanyProfile>(`/companies/${encodeURIComponent(cik)}`, { source: sourceParam(options.source) }, options),
    getOverview: (cik: string, options: SourceOptions & { years?: number } = {}) =>
      get<OverviewResponse>(`/companies/${encodeURIComponent(cik)}/overview`, { years: options.years, source: sourceParam(options.source) }, options),
    getFinancials: (cik: string, options: SourceOptions & { years?: number } = {}) =>
      get<FinancialsResponse>(`/companies/${encodeURIComponent(cik)}/financials`, { years: options.years, source: sourceParam(options.source) }, options),
    getMetricCatalog: (options?: RequestOptions) => get<MetricsCatalog>("/metrics", {}, options),
    getMetricSeries: (cik: string, ids: readonly string[], options: SourceOptions & { years?: number } = {}) =>
      get<MetricSeriesResponse>(`/companies/${encodeURIComponent(cik)}/metrics`, { ids: ids.join(","), years: options.years, source: sourceParam(options.source) }, options),
'''),
])

sub("lib/format.ts", [
    ('''// Display formatting of finished values. No calculations here: values arrive computed from the backend.
''', '''// Display formatting of finished values. No calculations here: values arrive computed from the backend.

import type { MetricValue } from "./types";
'''),
    ('''export const NOT_REPORTED = "Not reported by SEC";
''', '''export const NOT_REPORTED = "Not reported by SEC";
/** Shown for a calculated value whose inputs are missing or whose denominator is zero. */
export const UNAVAILABLE = "unavailable";
'''),
])
open("lib/format.ts", "a").write('''
function withMinus(digits: string, negative: boolean): string {
  return negative ? `${MINUS}${digits}` : digits;
}

/** A decimal ratio as a percentage with one decimal: 0.25 → "25.0%". */
export function formatPercent(value: number | null): string {
  if (!isNumber(value)) return DASH;
  const text = (Math.abs(value) * 100).toFixed(1);
  return `${withMinus(text, value < 0 && Number(text) !== 0)}%`;
}

/** A decimal ratio as a multiple with two decimals: 0.5 → "0.50×". */
export function formatTimes(value: number | null): string {
  if (!isNumber(value)) return DASH;
  const text = Math.abs(value).toFixed(2);
  return `${withMinus(text, value < 0 && Number(text) !== 0)}×`;
}

/** A finished value in its display form: percent, multiple, or money in millions. */
export function formatMetric(metric: Pick<MetricValue, "value" | "unit">): string {
  if (metric.unit === "percent") return formatPercent(metric.value);
  if (metric.unit === "ratio") return formatTimes(metric.value);
  return formatMillions(metric.value);
}

/** The exact value with its unit, for tooltips. */
export function formatExactMetric(metric: Pick<MetricValue, "value" | "unit">): string {
  if (metric.unit === "percent") return formatPercent(metric.value);
  if (metric.unit === "ratio") return formatTimes(metric.value);
  return formatExact(metric.value, metric.unit);
}

/** The unit as a caption: "USD millions", "%" or "×". */
export function unitCaption(unit: string): string {
  if (unit === "percent") return "%";
  if (unit === "ratio") return "×";
  return unit ? `${unit} millions` : "";
}

/** A number on a chart axis, in the same form as the values. */
export function formatAxis(value: number, unit: string): string {
  return formatMetric({ value, unit });
}
''')

sub("components/SourceBadge.tsx", [
    ('''export type SourceBadgeProps =
  | { kind: "demo"; snapshotDate?: string | null; label?: string; className?: string }
''', '''export type SourceBadgeProps =
  | { kind: "demo"; snapshotDate?: string | null; label?: string; className?: string }
  | { kind: "live"; label: string; className?: string }
  | { kind: "cached"; label: string; className?: string }
'''),
    ('''    case "synthetic":
      return props.label || SYNTHETIC_LABEL;
''', '''    case "live":
    case "cached":
      return props.label;
    case "synthetic":
      return props.label || SYNTHETIC_LABEL;
'''),
    ('''  demo: "border-warning text-warning",
''', '''  demo: "border-warning text-warning",
  live: "border-positive text-positive",
  cached: "border-link text-link",
'''),
    ('''export function SourceBadge(props: SourceBadgeProps) {''', '''/** A panel's badge from the API's SourceInfo: the label says it all, and the colour only repeats it. */
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

export function SourceBadge(props: SourceBadgeProps) {'''),
    ('''export type SourceBadgeProps =''', '''import type { MetricKind, SourceInfo } from "@/lib/types";

export type SourceBadgeProps ='''),
])

sub("components/StatePanel.tsx", [
    ('''  action?: { label: string; onClick: () => void };
''', '''  action?: { label: string; onClick: () => void };
  /** A second next step, shown before `action` (for example "Use recorded demo data"). */
  secondaryAction?: { label: string; onClick: () => void };
'''),
    ('''export function StatePanel({ kind, title, message, reference, action, rows = 3, className }: StatePanelProps) {''',
     '''export function StatePanel({ kind, title, message, reference, action, secondaryAction, rows = 3, className }: StatePanelProps) {'''),
    ('''      {action ? (
        <button
          type="button"
          onClick={action.onClick}
          className="mt-2 rounded-sm border border-line bg-panel px-2 py-1 text-fg hover:border-accent"
        >
          {action.label}
        </button>
      ) : null}
''', '''      {action || secondaryAction ? (
        <div className="mt-2 flex flex-wrap gap-2">
          {[secondaryAction, action].filter((item) => item !== undefined).map((item) => (
            <button
              key={item.label}
              type="button"
              onClick={item.onClick}
              className="rounded-sm border border-line bg-panel px-2 py-1 text-fg hover:border-accent"
            >
              {item.label}
            </button>
          ))}
        </div>
      ) : null}
'''),
])

sub("components/AppHeader.tsx", [
    ('''import { SourceBadge } from "@/components/SourceBadge";

''', ''),
    ('''  /** Backend status indicator (BackendStatus). */
  status?: ReactNode;
''', '''  /** The data source: the mode badge and, under `npm run dev`, the Demo / Live selector. */
  mode?: ReactNode;
  /** Backend status indicator (BackendStatus). */
  status?: ReactNode;
'''),
    (''' * Compact app header: wordmark, search slot, the app-wide mode badge and backend status.
''', ''' * Compact app header: wordmark, search slot, the data source and backend status.
'''),
    (''' * No menu items at M1: there are no other screens.
''', ''' * No menu items: there are no other screens.
'''),
    ('''export function AppHeader({ search, status }: AppHeaderProps) {''', '''export function AppHeader({ search, mode, status }: AppHeaderProps) {'''),
    ('''          <SourceBadge kind="demo" />
''', '''          {mode}
'''),
])

sub("app/layout.tsx", [
    ('''import type { Metadata } from "next";
''', '''import type { Metadata } from "next";
import { Suspense } from "react";
'''),
    ('''import { CompanySearch } from "@/components/CompanySearch";
''', '''import { CompanySearch } from "@/components/CompanySearch";
import { ModeSelector } from "@/components/ModeSelector";
'''),
    ('''company profiles and figures from recorded SEC EDGAR data''', '''company profiles and annual figures from SEC EDGAR data'''),
    ('''        <AppHeader search={<CompanySearch />} status={<BackendStatus />} />
        <main id="main" className="mx-auto w-full max-w-[1440px] px-4 py-4">
          {children}
        </main>
''', '''        {/* Suspense: these read the page URL (?source=), which is only known in the browser. */}
        <Suspense fallback={<AppHeader status={<BackendStatus />} />}>
          <AppHeader search={<CompanySearch />} mode={<ModeSelector />} status={<BackendStatus />} />
        </Suspense>
        <main id="main" className="mx-auto w-full max-w-[1440px] px-4 py-4">
          <Suspense fallback={null}>{children}</Suspense>
        </main>
'''),
])

sub("components/CompanySearch.tsx", [
    ('''import { isFocusSearchShortcut } from "@/lib/shortcuts";
''', '''import { isFocusSearchShortcut } from "@/lib/shortcuts";
import { useDataSource } from "@/lib/source";
'''),
    ('''export const NO_MATCH = "No match in the demo universe (3 companies)";
''', '''export const NO_MATCH = "No match in the demo universe (3 companies)";
export const LIVE_UNIVERSE_NOTE = "Live search covers SEC filers listed in the SEC ticker file; other filers can be opened by CIK.";
export const LIVE_NO_MATCH = "No match in the SEC ticker file";
'''),
    (''' * The header search: an accessible combobox over the demo universe (name, ticker or CIK).
''', ''' * The header search: an accessible combobox over the demo universe or, in Live, SEC's ticker file.
'''),
    ('''  const router = useRouter();
  const pathname = usePathname();
''', '''  const router = useRouter();
  const pathname = usePathname();
  const { source, href } = useDataSource();
  const universeNote = source === "live" ? LIVE_UNIVERSE_NOTE : UNIVERSE_NOTE;
  const noMatch = source === "live" ? LIVE_NO_MATCH : NO_MATCH;
'''),
    ('''  type Answer''' if False else '''  const current = answer && answer.query === trimmed ? answer : null;
''', '''  const current = answer && answer.query === trimmed && answer.source === source ? answer : null;
'''),
    ('''type Answer = { query: string; results: SearchResult[]; error: ApiError | null };
''', '''type Answer = { query: string; source: string; results: SearchResult[]; error: ApiError | null };
'''),
    ('''      api.searchCompanies(trimmed, { signal: controller.signal }).then(
        (response) => {
          setAnswer({ query: trimmed, results: response.results, error: null });
''', '''      api.searchCompanies(trimmed, { signal: controller.signal, source }).then(
        (response) => {
          setAnswer({ query: trimmed, source, results: response.results, error: null });
'''),
    ('''          setAnswer({ query: trimmed, results: [], error: apiError });
''', '''          setAnswer({ query: trimmed, source, results: [], error: apiError });
'''),
    ('''  }, [trimmed]);
''', '''  }, [trimmed, source]);
'''),
    ('''    router.push(`/companies/${result.cik}`);
''', '''    router.push(href(`/companies/${result.cik}`));
'''),
    ('''        ? NO_MATCH
        : `${results.length}''', '''        ? noMatch
        : `${results.length}'''),
    ('''              <p className="px-2 pb-1.5 text-fg">{NO_MATCH}</p>
''', '''              <p className="px-2 pb-1.5 text-fg">{noMatch}</p>
'''),
    ('''            <p className="border-t border-line px-2 py-1 text-label text-muted">{UNIVERSE_NOTE}</p>
''', '''            <p className="border-t border-line px-2 py-1 text-label text-muted">{universeNote}</p>
'''),
    ('''        {UNIVERSE_NOTE}
      </p>
''', '''        {universeNote}
      </p>
'''),
])

sub("components/RevenueIncomeChart.tsx", [
    ('''  { value: "all", label: "All in snapshot" },
''', '''  { value: "all", label: "All available" },
'''),
])

sub("next.config.ts", [
    ('''  distDir: process.env.NEXT_DIST_DIR || ".next",
''', '''  distDir: process.env.NEXT_DIST_DIR || ".next",
  // A live request can wait for SEC's Retry-After (up to 30 s, twice) plus its 20 s timeout.
  experimental: { proxyTimeout: 120_000 },
'''),
])

sub("app/page.tsx", [
    ('''import { SourceBadge } from "@/components/SourceBadge";
''', '''import { LIVE_HELP } from "@/components/ModeSelector";
import { SourceBadge } from "@/components/SourceBadge";
'''),
    ('''import { useApiResource } from "@/lib/useApiResource";
''', '''import { useDataSource } from "@/lib/source";
import { useApiResource } from "@/lib/useApiResource";
'''),
    ('''  const meta = useApiResource("meta", loadMeta);
''', '''  const meta = useApiResource("meta", loadMeta);
  const { source, href } = useDataSource();
  const live = source === "live";
'''),
    ('''          Company profiles and annual figures from recorded SEC filings
''', '''          {live ? "Company profiles and annual figures from live SEC data" : "Company profiles and annual figures from recorded SEC filings"}
'''),
    ('''        </p>
      </section>
''', '''        </p>
        {live ? <p className="max-w-3xl text-muted">{LIVE_HELP}</p> : null}
      </section>
'''),
    ('''        badge={meta.status === "ok" ? <SourceBadge kind="demo" snapshotDate={meta.data.snapshot_date} /> : null}
''', '''        badge={meta.status === "ok" && !live ? <SourceBadge kind="demo" snapshotDate={meta.data.snapshot_date} /> : null}
'''),
    ('''                  <Link href={`/companies/${company.cik}`}>{companyLine(company)}</Link>
''', '''                  <Link href={href(`/companies/${company.cik}`)}>{companyLine(company)}</Link>
'''),
])
print("ok")
