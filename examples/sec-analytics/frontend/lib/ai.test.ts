import { describe, expect, it, vi } from "vitest";

import { ApiError } from "./api";
import { aiErrorText, createAiApi, filterModels, formatUsdPerMillion, isValidModelId, linkWithSource, usageLine } from "./ai";
import type { AiModel, AiScope } from "./types";

const KEY = "test-key-not-real-0000";
const SCOPE: AiScope = { kind: "company", cik: "0000320193" };

function jsonResponse(status: number, body: unknown) {
  return new Response(JSON.stringify(body), { status, headers: { "Content-Type": "application/json" } });
}

function fakeFetch(answer: Response | { throws: unknown }) {
  return vi.fn<(input: string, init?: RequestInit) => Promise<Response>>(async () => {
    if (!(answer instanceof Response)) throw answer.throws;
    return answer.clone();
  });
}

function headersOf(init: RequestInit | undefined): Record<string, string> {
  return Object.fromEntries(new Headers(init?.headers).entries());
}

describe("AI client", () => {
  it("sends the key only in the X-OpenRouter-Key header, never in a URL or body", async () => {
    const fetcher = fakeFetch(jsonResponse(200, {}));
    const ai = createAiApi(fetcher);
    await ai.listModels(KEY);
    await ai.testConnection(KEY);
    await ai.chat(KEY, { model: "example/model-a", scope: SCOPE, question: "Why?", source: "demo" });
    expect(fetcher.mock.calls.map(([url, init]) => [url, init?.method])).toEqual([
      ["/api/ai/models", "GET"],
      ["/api/ai/test-connection", "POST"],
      ["/api/ai/chat", "POST"],
    ]);
    for (const [url, init] of fetcher.mock.calls) {
      expect(headersOf(init)["x-openrouter-key"]).toBe(KEY);
      expect(url).not.toContain(KEY);
      expect(String(init?.body ?? "")).not.toContain(KEY);
    }
    expect(JSON.parse(String(fetcher.mock.calls[2][1]?.body))).toEqual({ model: "example/model-a", scope: SCOPE, question: "Why?", source: "demo" });
  });

  it("asks for the context line without any key", async () => {
    const fetcher = fakeFetch(jsonResponse(200, { line: "Context: AAPL", facts: 1, passages: 0, chars: 10 }));
    await createAiApi(fetcher).context(SCOPE, "live");
    const [url, init] = fetcher.mock.calls[0];
    expect(url).toBe("/api/ai/context");
    expect(headersOf(init)["x-openrouter-key"]).toBeUndefined();
    expect(JSON.parse(String(init?.body))).toEqual({ scope: SCOPE, source: "live" });
  });

  it("passes the abort signal through and lets an abort reject unchanged", async () => {
    const controller = new AbortController();
    const ok = fakeFetch(jsonResponse(200, {}));
    await createAiApi(ok).chat(KEY, { model: "m", scope: SCOPE, question: "q", source: "demo" }, { signal: controller.signal });
    expect(ok.mock.calls[0][1]?.signal).toBe(controller.signal);
    const abort = new DOMException("The operation was aborted.", "AbortError");
    await expect(createAiApi(fakeFetch({ throws: abort })).chat(KEY, { model: "m", scope: SCOPE, question: "q", source: "demo" })).rejects.toBe(abort);
  });

  it("turns an error envelope into an ApiError with the backend's message", async () => {
    const body = { error: { code: "ai_key_invalid", message: "Key rejected", details: null, reference: null } };
    const error = await createAiApi(fakeFetch(jsonResponse(401, body))).listModels(KEY).catch((e: unknown) => e);
    expect(error).toBeInstanceOf(ApiError);
    expect([(error as ApiError).status, (error as ApiError).code, (error as ApiError).message]).toEqual([401, "ai_key_invalid", "Key rejected"]);
    expect((error as ApiError).message).not.toContain(KEY);
  });

  it("reports an unreachable backend without the key", async () => {
    const error = (await createAiApi(fakeFetch({ throws: new TypeError("Failed to fetch") })).testConnection(KEY).catch((e: unknown) => e)) as ApiError;
    expect(error.code).toBe("backend_unreachable");
  });
});

describe("AI display helpers", () => {
  it("validates manual model ids", () => {
    expect(isValidModelId("openai/gpt-x:free")).toBe(true);
    expect(isValidModelId("a.b_c-d/e:f")).toBe(true);
    expect(isValidModelId("")).toBe(false);
    expect(isValidModelId("has space")).toBe(false);
    expect(isValidModelId("x".repeat(201))).toBe(false);
    expect(isValidModelId("<script>")).toBe(false);
  });

  it("keeps ?source=live in source links, before the #block anchor", () => {
    expect(linkWithSource("/companies/0000320193/filings/0000320193-26-000026#block-12", "live")).toBe(
      "/companies/0000320193/filings/0000320193-26-000026?source=live#block-12",
    );
    expect(linkWithSource("/companies/0000320193", "live")).toBe("/companies/0000320193?source=live");
    expect(linkWithSource("/companies/0000320193#block-1", "demo")).toBe("/companies/0000320193#block-1");
  });

  it("shows prices per million tokens, free, or that pricing is not available", () => {
    expect(formatUsdPerMillion("0.15")).toBe("$0.15");
    expect(formatUsdPerMillion("2.500000")).toBe("$2.50");
    expect(formatUsdPerMillion("0.0000123")).toBe("$0.0000123");
    expect(formatUsdPerMillion("0")).toBe("free");
    expect(formatUsdPerMillion(null)).toBe("pricing not available");
  });

  it("filters models by id or name, sorted by id", () => {
    const model = (id: string, name: string): AiModel => ({ id, name, context_length: null, prompt_usd_per_million: null, completion_usd_per_million: null, expiration_date: null });
    const list = [model("zeta/one", "Zeta One"), model("alpha/two", "Alpha Two"), model("beta/x", "Fast Model")];
    expect(filterModels(list, "").map((m) => m.id)).toEqual(["alpha/two", "beta/x", "zeta/one"]);
    expect(filterModels(list, "FAST").map((m) => m.id)).toEqual(["beta/x"]);
    expect(filterModels(list, " zeta ").map((m) => m.id)).toEqual(["zeta/one"]);
  });

  it("writes the usage line, with cost only when given", () => {
    expect(usageLine({ prompt_tokens: 1234, completion_tokens: 56, cost: null })).toBe("Usage: 1,234 prompt + 56 completion tokens");
    expect(usageLine({ prompt_tokens: 10, completion_tokens: 2, cost: 0.00123 })).toBe("Usage: 10 prompt + 2 completion tokens · cost $0.00123");
    expect(usageLine(null)).toBeNull();
  });

  it("adds the retry time to a rate limit", () => {
    const limited = new ApiError(429, { error: { code: "ai_rate_limited", message: "Rate limited; try again later", details: { retry_after: 30 }, reference: null } });
    expect(aiErrorText(limited)).toBe("Rate limited; try again later (retry after 30 s)");
    const plain = new ApiError(401, { error: { code: "ai_key_invalid", message: "Key rejected", details: null, reference: null } });
    expect(aiErrorText(plain)).toBe("Key rejected");
  });
});
