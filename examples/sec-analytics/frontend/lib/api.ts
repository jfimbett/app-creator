// Typed client for the backend. The browser calls only same-origin /api/* (Next.js rewrites it to the backend).

import type {
  CompanyProfile,
  ErrorEnvelope,
  HealthResponse,
  MetaResponse,
  OverviewResponse,
  SearchResponse,
} from "./types";

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

function clientError(status: number | null, code: string, message: string): ApiError {
  return new ApiError(status, { error: { code, message, details: null, reference: null } });
}

function isEnvelope(body: unknown): body is ErrorEnvelope {
  if (typeof body !== "object" || body === null) return false;
  const error = (body as { error?: unknown }).error;
  return (
    typeof error === "object" &&
    error !== null &&
    typeof (error as { code?: unknown }).code === "string" &&
    typeof (error as { message?: unknown }).message === "string"
  );
}

async function readJson(response: Response): Promise<unknown> {
  try {
    return await response.json();
  } catch {
    return undefined;
  }
}

type Fetcher = (input: string, init?: RequestInit) => Promise<Response>;

export interface RequestOptions {
  signal?: AbortSignal;
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

  return {
    getHealth: (options?: RequestOptions) => get<HealthResponse>("/health", {}, options),
    getMeta: (options?: RequestOptions) => get<MetaResponse>("/meta", {}, options),
    searchCompanies: (q: string, options: RequestOptions & { limit?: number } = {}) =>
      get<SearchResponse>("/companies/search", { q, limit: options.limit }, options),
    getCompany: (cik: string, options?: RequestOptions) =>
      get<CompanyProfile>(`/companies/${encodeURIComponent(cik)}`, {}, options),
    getOverview: (cik: string, options: RequestOptions & { years?: number } = {}) =>
      get<OverviewResponse>(`/companies/${encodeURIComponent(cik)}/overview`, { years: options.years }, options),
  };
}

/** The client used by the screens. */
export const api = createApi();
