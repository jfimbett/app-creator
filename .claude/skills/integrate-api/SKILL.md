---
name: integrate-api
description: Use when the app must get data from or send data to an external API or data source (public statistics, a web service, an AI model, email), or when such an integration fails, is slow, hits rate limits, or needs offline fixtures.
---

# Integrate an external API into the application

Build the integration **inside the app's backend**: a client module the app calls, settings for secrets, limits,
caching, provenance, and tests that do not need the network. Fetching data once for the conversation is not an
integration.

Paths: `<backend>`, `<frontend>` and `<docs>` are `app.backendDir`, `app.frontendDir` and `app.docsDir` in
`app-creator.config.json` (after `npm run create-app`: `app/backend`, `app/frontend`, `app/docs`). Settings
names go in the root `.env.example`; the launchers pass the person's root `.env` to the backend.

## Inputs

- `<docs>/product.md` (which data, how fresh), `<docs>/architecture.md` (data-access part, external services
  table), `<docs>/acceptance.md` (what the user must see when the service fails).
- The provider's **official documentation**: endpoints, authentication, rate limits, required headers (some
  providers refuse requests without an identifying `User-Agent`), redirects, terms of use (may the data be shown
  to users? stored? for how long?). Read it; do not rely on memory. If it cannot be read, say so and mark the
  details `[unverified]` in `<docs>/architecture.md`.
- Patterns and code: [http-client-patterns.md](http-client-patterns.md).

## Actions

1. **Record the service** in the external services table of `<docs>/architecture.md`: purpose, base URL and the
   paths used, setting names, rate limit, cost and free tier, terms checked (date). Stop and ask before choosing
   anything that costs money.
2. **Settings and secrets.** Add each setting name with a placeholder or safe default to the root `.env.example`.
   The person creates `.env` from it (`cp .env.example .env`); you never read, print or ask them to paste a key.
   Load settings in one place (for example `<backend>/app/config.py`) and fail with a clear message naming the
   missing setting (never its value). The app must start and its tests must pass with **no `.env`**: live
   features then explain that a key is needed, and fixture mode works.
3. **Server side only.** The browser calls the app's own `/api/*` routes; only the backend talks to the provider.
   Keys never reach the frontend bundle (no `NEXT_PUBLIC_` key), and no route forwards an arbitrary URL ("proxy"):
   - build every outgoing URL from a fixed base URL plus a path from an **allowlist** of hosts (scheme, host and
     port) and path patterns;
     validate user input that goes into a path or query (pattern, length) before using it;
   - follow redirects only when the target is still on the allowlist (or turn redirects off);
   - send the identification header the provider requires (an app name and a project contact URL or role
     address taken from settings; never a personal address hard-coded in the code).
4. **Client module** (for example `<backend>/app/clients/<service>.py`): one function per operation, returning
   plain data the app understands (typed models, not raw responses). Inside it:
   - a **timeout** on every request (connect and read) **and an overall limit per attempt** (`asyncio.wait_for`):
     httpx's timeouts are per operation, so a slow trickle of data never trips them;
   - a **response size cap** (for example 5 MB): refuse a larger `Content-Length` and stream the body, stopping
     at the cap, so one huge or endless answer cannot fill memory;
   - a clear error type per failure: unavailable, not found, bad credentials, rate limited, bad data;
   - **throttling** below the provider's limit (requests per second), shared by the whole process;
   - **retries** only for safe requests (GET) and only for timeouts, 429 and 5xx: at most 3 attempts with
     exponential backoff plus jitter, honoring `Retry-After`; never retry 400/401/403/404;
   - **request de-duplication**: concurrent identical requests share one in-flight call;
   - **validation** of shape and units before returning (missing stays missing, never becomes 0).
5. **Caching** when data changes slowly or calls are limited: a disk cache with an expiry per kind of data
   (`manage-data`, [caching-and-storage.md](../manage-data/caching-and-storage.md)). Respect the terms on storage.
6. **Provenance.** Every value shown to users carries its source (provider, endpoint or document), retrieval
   time, and mode: `live`, `cached` (with age) or `fixture`. The interface shows it where users rely on the data.
7. **Fixtures.** Two kinds, kept apart and labelled:
   - **recorded fixtures**: a real response saved once (keys, tokens and personal data removed), stored with a
     small metadata file (source URL without secrets, retrieval date, what was trimmed);
   - **synthetic fixtures**: hand-written data for edge cases, in a separate folder, named and marked synthetic.
   A fixture mode setting (for example `DATA_MODE=fixtures`, put in `demoEnv` of the config) serves recorded
   fixtures with no network and no keys, so `npm run demo` and `npm run verify` work offline.
8. **Use it in the app** through the logic layer, never directly from route or interface code. Show users a
   helpful message when the service fails (`design-interface` error state), plus source and date.
9. **Tests** (`test-and-check`): parsing, units, each error type (timeout, 404, 429 with `Retry-After`, malformed
   body), allowlist refusal, cache hit and expiry, with HTTP mocked by `respx`. One optional live smoke check the
   person runs by hand, never part of `npm run verify`.

### Optional: an AI / LLM provider

Same rules, plus: the provider and model are settings; prompts and limits live in code reviewed like any logic.

- **Keys.** Either a server setting, or a key the user types in the interface for their own session. A
  user-supplied key is sent to the backend in a request header, forwarded to the provider for that one request,
  and then dropped: never stored, logged, cached, put in a URL, echoed in an error, or included in screenshots
  or fixtures. Redact it in exception messages.
- **Bounded requests:** maximum input size (characters or tokens), maximum output tokens, a timeout, and a
  per-session rate limit. Refuse oversized input with a clear message instead of truncating silently.
- **Grounding and labels:** send only the data the feature needs (no personal data unless agreed); label the
  answer as AI-generated; never present model output as a verified fact or number.
- **Tests** use recorded or synthetic model responses; no test needs a key.

## Outputs

Client module, settings in `.env.example`, config loading, allowlist, cache, provenance on returned data,
recorded and synthetic fixtures with labels, fixture mode, tests, updated `<docs>/architecture.md`, a change
report.

## Verification

- `npm run verify` passes with the network off and no `.env` (fixture mode, `respx` mocks).
- A test proves the allowlist refuses a host or path outside it, and a redirect to another host.
- A test proves a 429 with `Retry-After: 2` waits about 2 s (use a fake clock or monkeypatched sleep) and that a
  404 is not retried.
- One live call made by the running app returned real data (when the person has set the key), or the gap is
  stated. Never print the key or full authorised URLs in the report.
- A failing service shows a user-facing message, not a crash (checked with a simulated failure).

## Stop when

- The feature works end to end with real data, or works with fixtures and the live step is clearly left to the
  person.
- **Stop and ask** if the terms forbid the intended use or storage, the service needs payment, the key would have
  to be shipped to browsers, the provider's documentation cannot be found, or the feature would send personal
  data to a provider.

## Common mistakes

- Calling the API from the browser, or exposing a "fetch any URL" endpoint.
- Tests that hit the live API (slow, flaky, use up limits).
- Retrying everything, immediately, forever; ignoring `Retry-After`.
- Mixing recorded and synthetic fixtures so nobody knows which numbers are real.
- Logging the full request including the `Authorization` header or a user's key.
- Committing a key "just for testing"; if it happens, the key must be revoked, not just deleted
  ([env-and-secrets.md](../prepare-deploy/env-and-secrets.md)).

## Example

"Show the latest population figures from a public statistics API." Record the API in the services table (free,
10 requests per second, attribution required). Add `STATS_BASE_URL` and `STATS_CONTACT_URL` to `.env.example`.
Write `clients/stats.py` with an allowlist of `/v1/series/{id}` (id matches `^[A-Z0-9_]{1,32}$`), a 10 s
timeout, throttling to 5 requests per second, retries on 429/5xx, and a 24 h disk cache. Save one recorded
response to `tests/fixtures/recorded/stats_series_pop.json` with its metadata, and a synthetic series with a
missing year to `tests/fixtures/synthetic/`. The route returns `{"values": [...], "source": "Stats API
/v1/series/POP", "retrieved_at": "...", "mode": "cached"}` and the page shows "Source: Stats API, retrieved
3 Nov 2026 (cached 2 h)".
