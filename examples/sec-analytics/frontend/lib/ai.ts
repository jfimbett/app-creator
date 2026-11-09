// Typed calls to the backend's AI boundary (/api/ai/*, milestones/architecture.md "OpenRouter boundary").
// The browser talks only to its own backend. The person's key goes in the X-OpenRouter-Key header of the
// calls that need it, never in a URL, a body or an error message; the backend uses it for one upstream call.

import { ApiError, BACKEND_UNREACHABLE, clientError, type Fetcher, isEnvelope, readJson, type RequestOptions } from "./api";
import type { AiChatRequest, AiChatResponse, AiConnectionResponse, AiContext, AiModel, AiModelsResponse, AiScope, DataSourceChoice } from "./types";

export const KEY_HEADER = "X-OpenRouter-Key";
export const QUESTION_MAX = 2000;
export const MODEL_ID_PATTERN = /^[A-Za-z0-9._:/-]{1,200}$/;
export const CANCELLED = "Cancelled";
export const LENGTH_CUT = "Answer cut at the output limit";
export const NOT_IN_SOURCES = "Reference not in the supplied sources";

export function isValidModelId(id: string): boolean {
  return MODEL_ID_PATTERN.test(id);
}

export function createAiApi(fetcher: Fetcher = (input, init) => fetch(input, init)) {
  async function send<T>(method: "GET" | "POST", path: string, key: string | null, body: unknown, options: RequestOptions): Promise<T> {
    const headers: Record<string, string> = { Accept: "application/json" };
    if (key) headers[KEY_HEADER] = key;
    if (method === "POST") headers["Content-Type"] = "application/json";

    let response: Response;
    try {
      response = await fetcher(`/api/ai${path}`, {
        method,
        headers,
        body: method === "POST" ? JSON.stringify(body ?? {}) : undefined,
        signal: options.signal,
        cache: "no-store",
      });
    } catch (error) {
      if ((error as { name?: unknown } | null)?.name === "AbortError") throw error;
      throw clientError(null, "backend_unreachable", BACKEND_UNREACHABLE);
    }

    const parsed = await readJson(response);
    if (response.ok) {
      if (parsed === undefined) throw clientError(response.status, "invalid_response", "The backend sent an answer that is not JSON.");
      return parsed as T;
    }
    if (isEnvelope(parsed)) throw new ApiError(response.status, parsed);
    if (response.status >= 500) throw clientError(response.status, "backend_unreachable", BACKEND_UNREACHABLE);
    throw clientError(response.status, "invalid_response", `The backend answered with HTTP ${response.status}.`);
  }

  return {
    listModels: (key: string, options: RequestOptions = {}) => send<AiModelsResponse>("GET", "/models", key, undefined, options),
    testConnection: (key: string, options: RequestOptions = {}) => send<AiConnectionResponse>("POST", "/test-connection", key, {}, options),
    /** The server-built context line for a scope; free, so it needs no key. */
    context: (scope: AiScope, source: DataSourceChoice, options: RequestOptions = {}) =>
      send<AiContext>("POST", "/context", null, { scope, source }, options),
    chat: (key: string, request: AiChatRequest, options: RequestOptions = {}) => send<AiChatResponse>("POST", "/chat", key, request, options),
  };
}

export const aiApi = createAiApi();

/** An app link from a source chip, keeping ?source=live (before any #block anchor). */
export function linkWithSource(link: string, source: DataSourceChoice): string {
  if (source !== "live") return link;
  const hashAt = link.indexOf("#");
  const path = hashAt === -1 ? link : link.slice(0, hashAt);
  const hash = hashAt === -1 ? "" : link.slice(hashAt);
  return `${path}${path.includes("?") ? "&" : "?"}source=live${hash}`;
}

/** A price in USD per million tokens, as sent by the backend (a decimal string); display only. */
export function formatUsdPerMillion(value: string | null): string {
  if (value === null) return "pricing not available";
  const amount = Number(value);
  if (!Number.isFinite(amount)) return "pricing not available";
  if (amount === 0) return "free";
  if (amount < 0.01) return `$${String(amount)}`;
  return `$${amount.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 4 })}`;
}

export function formatContextLength(tokens: number | null): string {
  return tokens === null ? "—" : `${tokens.toLocaleString("en-US")} tokens`;
}

/** The model list for the table: sorted by id, filtered by a case-insensitive match on id or name. */
export function filterModels(models: readonly AiModel[], query: string): AiModel[] {
  const needle = query.trim().toLowerCase();
  return models
    .filter((model) => !needle || model.id.toLowerCase().includes(needle) || model.name.toLowerCase().includes(needle))
    .sort((a, b) => (a.id < b.id ? -1 : a.id > b.id ? 1 : 0));
}

export function usageLine(usage: AiChatResponse["usage"]): string | null {
  if (!usage) return null;
  const tokens = `Usage: ${usage.prompt_tokens.toLocaleString("en-US")} prompt + ${usage.completion_tokens.toLocaleString("en-US")} completion tokens`;
  return usage.cost === null ? tokens : `${tokens} · cost $${String(usage.cost)}`;
}

/** The backend's message for an AI error, with the wait time of a rate limit when given. */
export function aiErrorText(error: ApiError): string {
  const retry = error.envelope.error.details?.retry_after;
  if (error.code === "ai_rate_limited" && (typeof retry === "number" || typeof retry === "string") && String(retry).trim()) {
    return `${error.message} (retry after ${String(retry)} s)`;
  }
  return error.message;
}

const NEXT_STEP: Record<string, string> = {
  ai_key_missing: "Add your key in AI settings.",
  ai_key_invalid: "Check or replace the key in AI settings.",
  ai_insufficient_credits: "Add credit to the key, or ask your instructor for a key with credit left.",
  ai_forbidden: "Rephrase the question, or check the key's permissions on OpenRouter.",
  ai_model_not_found: "Open AI settings and choose another model.",
  ai_rate_limited: "Wait a little, then ask again.",
  ai_timeout: "Ask again, perhaps with a shorter question or another model.",
  ai_busy: "Wait for the running question to finish, then ask again.",
  request_too_large: "Shorten the question.",
  invalid_question: "Write a question of 1 to 2,000 characters.",
  invalid_model: "Open AI settings and choose a model from the list.",
  invalid_scope: "Reload the page and open the analyst again.",
  forbidden_origin: "Open the app at http://127.0.0.1 or http://localhost.",
  ai_unavailable: "The AI provider did not answer properly; try again later or choose another model.",
  backend_unreachable: "Start the app with npm run demo or npm run dev.",
};

export function aiNextStep(code: string): string {
  return NEXT_STEP[code] ?? "Try again.";
}
