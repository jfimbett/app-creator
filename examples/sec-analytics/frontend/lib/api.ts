// Typed client for the backend. The browser calls only same-origin /api/* (Next.js rewrites it to the backend).

import type {
  CompanyProfile,
  CompareResponse,
  DataSourceChoice,
  ErrorEnvelope,
  FilingDocumentResponse,
  FilingsResponse,
  FinancialsResponse,
  HealthResponse,
  MetaResponse,
  MetricSeriesResponse,
  MetricsCatalog,
  OverviewResponse,
  SearchResponse,
} from "./types";
import type { CompareState } from "./compare-state";

export const BACKEND_UNREACHABLE = "Backend not reachable: start it with npm run demo";

/** Every failed call throws this. `status` is null when no answer arrived at all. */
export class ApiError extends Error {
  readonly status: number | null;
  readonly envelope: ErrorEnvelope;

  constructor(status: number | null, envelope: ErrorEnvelope) {
    super(envelope.error.message);
    this.name = "ApiError";
    this.status = status;
    this.envelope = envelope;
  }

  get code(): string {
    return this.envelope.error.code;
  }

  get reference(): string | null {
    return this.envelope.error.reference;
  }
}

export function clientError(status: number | null, code: string, message: string): ApiError {
  return new ApiError(status, { error: { code, message, details: null, reference: null } });
}

export function isEnvelope(body: unknown): body is ErrorEnvelope {
  if (typeof body !== "object" || body === null) return false;
  const error = (body as { error?: unknown }).error;
  return (
    typeof error === "object" &&
    error !== null &&
    typeof (error as { code?: unknown }).code === "string" &&
    typeof (error as { message?: unknown }).message === "string"
  );
}

export async function readJson(response: Response): Promise<unknown> {
  try {
    return await response.json();
  } catch {
    return undefined;
  }
}

export type Fetcher = (input: string, init?: RequestInit) => Promise<Response>;

export interface RequestOptions {
  signal?: AbortSignal;
}

/** Calls that can use live data say which source they want; demo is left off the URL. */
export interface SourceOptions extends RequestOptions {
  source?: DataSourceChoice;
}

function sourceParam(source: DataSourceChoice | undefined): DataSourceChoice | undefined {
  return source === "live" ? "live" : undefined;
}

/** The query of /api/compare and /api/compare.csv; demo is left off the URL like every other call. */
export function compareParams(state: CompareState): Record<string, string | number | undefined> {
  return {
    ciks: state.ciks.join(","),
    metrics: state.metrics.join(","),
    years: state.years,
    index: state.index,
    source: sourceParam(state.source),
  };
}

/** Builds the client around a fetch function (the browser's by default; a fake one in tests). */
export function createApi(fetcher: Fetcher = (input, init) => fetch(input, init)) {
  async function get<T>(path: string, params: Record<string, string | number | undefined> = {}, options: RequestOptions = {}): Promise<T> {
    const query = new URLSearchParams();
    for (const [key, value] of Object.entries(params)) {
      if (value !== undefined) query.set(key, String(value));
    }
    const url = query.size > 0 ? `/api${path}?${query}` : `/api${path}`;

    let response: Response;
    try {
      response = await fetcher(url, { signal: options.signal, headers: { Accept: "application/json" } });
    } catch (error) {
      if ((error as { name?: unknown } | null)?.name === "AbortError") throw error;
      throw clientError(null, "backend_unreachable", BACKEND_UNREACHABLE);
    }

    const body = await readJson(response);
    if (response.ok) {
      if (body === undefined) throw clientError(response.status, "invalid_response", "The backend sent an answer that is not JSON.");
      return body as T;
    }
    if (isEnvelope(body)) throw new ApiError(response.status, body);
    // No envelope: the Next.js proxy itself answered (it returns 500 when the backend is down).
    if (response.status >= 500) throw clientError(response.status, "backend_unreachable", BACKEND_UNREACHABLE);
    throw clientError(response.status, "invalid_response", `The backend answered with HTTP ${response.status}.`);
  }

  /** A file answer (the CSV): its bytes and the file name from Content-Disposition. Errors are the JSON envelope. */
  async function getFile(path: string, params: Record<string, string | number | undefined>, options: RequestOptions = {}): Promise<{ blob: Blob; filename: string }> {
    const query = new URLSearchParams();
    for (const [key, value] of Object.entries(params)) {
      if (value !== undefined) query.set(key, String(value));
    }
    let response: Response;
    try {
      response = await fetcher(`/api${path}?${query}`, { signal: options.signal });
    } catch (error) {
      if ((error as { name?: unknown } | null)?.name === "AbortError") throw error;
      throw clientError(null, "backend_unreachable", BACKEND_UNREACHABLE);
    }
    if (!response.ok) {
      const body = await readJson(response);
      if (isEnvelope(body)) throw new ApiError(response.status, body);
      if (response.status >= 500) throw clientError(response.status, "backend_unreachable", BACKEND_UNREACHABLE);
      throw clientError(response.status, "invalid_response", `The backend answered with HTTP ${response.status}.`);
    }
    const disposition = response.headers.get("Content-Disposition") ?? "";
    const filename = /filename="([^"]+)"/.exec(disposition)?.[1] ?? "sec-analytics-compare.csv";
    return { blob: await response.blob(), filename };
  }

  return {
    getHealth: (options?: RequestOptions) => get<HealthResponse>("/health", {}, options),
    getMeta: (options?: RequestOptions) => get<MetaResponse>("/meta", {}, options),
    searchCompanies: (q: string, options: SourceOptions & { limit?: number } = {}) =>
      get<SearchResponse>("/companies/search", { q, limit: options.limit, source: sourceParam(options.source) }, options),
    getCompany: (cik: string, options: SourceOptions = {}) =>
      get<CompanyProfile>(`/companies/${encodeURIComponent(cik)}`, { source: sourceParam(options.source) }, options),
    getOverview: (cik: string, options: SourceOptions & { years?: number } = {}) =>
      get<OverviewResponse>(`/companies/${encodeURIComponent(cik)}/overview`, { years: options.years, source: sourceParam(options.source) }, options),
    getFinancials: (cik: string, options: SourceOptions & { years?: number } = {}) =>
      get<FinancialsResponse>(`/companies/${encodeURIComponent(cik)}/financials`, { years: options.years, source: sourceParam(options.source) }, options),
    getFilings: (cik: string, options: SourceOptions = {}) =>
      get<FilingsResponse>(`/companies/${encodeURIComponent(cik)}/filings`, { source: sourceParam(options.source) }, options),
    getFilingDocument: (cik: string, accession: string, options: SourceOptions = {}) =>
      get<FilingDocumentResponse>(`/companies/${encodeURIComponent(cik)}/filings/${encodeURIComponent(accession)}`, { source: sourceParam(options.source) }, options),
    getMetricCatalog: (options?: RequestOptions) => get<MetricsCatalog>("/metrics", {}, options),
    getMetricSeries: (cik: string, ids: readonly string[], options: SourceOptions & { years?: number } = {}) =>
      get<MetricSeriesResponse>(`/companies/${encodeURIComponent(cik)}/metrics`, { ids: ids.join(","), years: options.years, source: sourceParam(options.source) }, options),
    getCompare: (state: CompareState, options: RequestOptions = {}) => get<CompareResponse>("/compare", compareParams(state), options),
    downloadCompareCsv: (state: CompareState, options: RequestOptions = {}) => getFile("/compare.csv", compareParams(state), options),
  };
}

/** The client used by the screens. */
export const api = createApi();
