import { describe, expect, it, vi } from "vitest";

import { ApiError, BACKEND_UNREACHABLE, createApi } from "./api";
import type { ErrorEnvelope } from "./types";

function jsonResponse(status: number, body: unknown) {
  return new Response(JSON.stringify(body), { status, headers: { "Content-Type": "application/json" } });
}

/** A fake fetch: `answer` is a response (cloned per call) or a thrown failure. */
function fakeFetch(answer: Response | { throws: unknown }) {
  return vi.fn<(input: string, init?: RequestInit) => Promise<Response>>(async () => {
    if (!(answer instanceof Response)) throw answer.throws;
    return answer.clone();
  });
}

async function caught(promise: Promise<unknown>): Promise<ApiError> {
  try {
    await promise;
  } catch (error) {
    if (error instanceof ApiError) return error;
    throw error;
  }
  throw new Error("expected an ApiError");
}

const envelope = (code: string, message: string): ErrorEnvelope => ({
  error: { code, message, details: null, reference: null },
});

describe("api paths", () => {
  it("calls only same-origin /api paths with encoded parameters", async () => {
    const fetcher = fakeFetch(jsonResponse(200, {}));
    const api = createApi(fetcher);
    await api.getMeta();
    await api.searchCompanies("AT&T inc", { limit: 5 });
    await api.getCompany("CIK 320193");
    await api.getOverview("0000320193");
    await api.getOverview("0000320193", { years: 5 });
    const urls = fetcher.mock.calls.map(([url]) => String(url));
    expect(urls).toEqual([
      "/api/meta",
      "/api/companies/search?q=AT%26T+inc&limit=5",
      "/api/companies/CIK%20320193",
      "/api/companies/0000320193/overview",
      "/api/companies/0000320193/overview?years=5",
    ]);
  });

  it("passes the abort signal through", async () => {
    const fetcher = fakeFetch(jsonResponse(200, {}));
    const controller = new AbortController();
    await createApi(fetcher).searchCompanies("aapl", { signal: controller.signal });
    expect(fetcher.mock.calls[0][1]?.signal).toBe(controller.signal);
  });

  it("returns the parsed body on success", async () => {
    const body = { status: "ok", app: "SEC Analytics" };
    await expect(createApi(fakeFetch(jsonResponse(200, body))).getHealth()).resolves.toEqual(body);
  });
});

describe("ApiError", () => {
  it("carries the error envelope of a 422", async () => {
    const api = createApi(fakeFetch(jsonResponse(422, envelope("invalid_cik", "A CIK has up to 10 digits"))));
    const error = await caught(api.getCompany("abc"));
    expect(error.status).toBe(422);
    expect(error.code).toBe("invalid_cik");
    expect(error.message).toBe("A CIK has up to 10 digits");
    expect(error.envelope.error.code).toBe("invalid_cik");
  });

  it("carries a 404 company_not_found", async () => {
    const api = createApi(fakeFetch(jsonResponse(404, envelope("company_not_found", "not in the demo snapshot"))));
    const error = await caught(api.getCompany("1"));
    expect([error.status, error.code]).toEqual([404, "company_not_found"]);
  });

  it("keeps the reference of a backend 500 but no detail", async () => {
    const body = { error: { code: "internal_error", message: "Something went wrong.", details: null, reference: "ab12" } };
    const error = await caught(createApi(fakeFetch(jsonResponse(500, body))).getMeta());
    expect([error.code, error.reference]).toEqual(["internal_error", "ab12"]);
  });

  it("reports an unreachable backend when the request fails", async () => {
    const error = await caught(createApi(fakeFetch({ throws: new TypeError("Failed to fetch") })).getMeta());
    expect([error.status, error.code, error.message]).toEqual([null, "backend_unreachable", BACKEND_UNREACHABLE]);
    expect(BACKEND_UNREACHABLE).toBe("Backend not reachable: start it with npm run demo");
  });

  it("treats a proxy 500 without an envelope as an unreachable backend", async () => {
    const proxy = new Response("Internal Server Error", { status: 500 });
    const error = await caught(createApi(fakeFetch(proxy)).getMeta());
    expect([error.status, error.code]).toEqual([500, "backend_unreachable"]);
  });

  it("reports an unexpected answer without leaking the body", async () => {
    const error = await caught(createApi(fakeFetch(new Response("<html>oops</html>", { status: 200 }))).getMeta());
    expect(error.code).toBe("invalid_response");
    expect(error.message).not.toContain("oops");
    const notFound = await caught(createApi(fakeFetch(new Response("nope", { status: 404 }))).getMeta());
    expect([notFound.status, notFound.code]).toEqual([404, "invalid_response"]);
  });

  it("lets an abort pass through unchanged", async () => {
    const abort = new DOMException("The operation was aborted.", "AbortError");
    await expect(createApi(fakeFetch({ throws: abort })).getMeta()).rejects.toBe(abort);
  });
});
