# OpenRouter API — implementation notes

All sources are official OpenRouter documentation, retrieved **2026-11-03** (the Markdown versions listed in `https://openrouter.ai/docs/llms.txt`). Citation keys:

- [AUTH] https://openrouter.ai/docs/api_reference/authentication.md
- [OVR] https://openrouter.ai/docs/api_reference/overview.md
- [PAR] https://openrouter.ai/docs/api_reference/parameters.md
- [CHAT] https://openrouter.ai/docs/api/api-reference/chat/create-a-chat-completion.md (OpenAPI)
- [ATTR] https://openrouter.ai/docs/app-attribution.md
- [ERR] https://openrouter.ai/docs/api_reference/errors-and-debugging.md
- [LIM] https://openrouter.ai/docs/api_reference/limits.md
- [MOD] https://openrouter.ai/docs/guides/overview/models.md
- [MODAPI] https://openrouter.ai/docs/api/api-reference/models/list-all-models-and-their-properties.md
- [KEY] https://openrouter.ai/docs/api/api-reference/api-keys/get-current-api-key.md
- [MGMT] https://openrouter.ai/docs/guides/overview/auth/management-api-keys.md
- [CREATE] https://openrouter.ai/docs/api/api-reference/api-keys/create-a-new-api-key.md
- [FREE] https://openrouter.ai/docs/guides/routing/model-variants/free.md
- [PROV] https://openrouter.ai/docs/guides/routing/provider-selection.md
- [SO] https://openrouter.ai/docs/guides/features/structured-outputs.md
- [CAP] https://openrouter.ai/docs/guides/best-practices/capping-shared-agent-keys.md

## 1. Base URL and authentication

- Base URL: `https://openrouter.ai/api/v1` [AUTH][CHAT].
- Auth: `Authorization: Bearer <OPENROUTER_API_KEY>` [AUTH]. Read the key from an environment variable and never commit it [AUTH].
- Optional attribution headers [OVR][ATTR]:
  - `HTTP-Referer`: your app URL. It is needed to create an app page in the rankings.
  - `X-OpenRouter-Title`: the display name. **`X-Title` still works only for backwards compatibility.** Title alone does not create an app page, and `localhost` apps must send both headers to be tracked.
  - `X-OpenRouter-Categories`: optional, up to 2 categories per request, comma-separated.
  - All of these are optional. Omitting them only means no rankings attribution.

## 2. Chat completions

`POST /api/v1/chat/completions` [OVR]. A Responses-style endpoint `POST /api/v1/responses` also exists [OVR]. Request fields [OVR][PAR][CHAT]:

| Field | Notes |
|---|---|
| `model` | string such as `author/slug`. If omitted, the account default is used [OVR]. |
| `messages` | array of `{role: system/user/assistant/tool, content}`, `minItems: 1` [CHAT] |
| `max_tokens` | integer ≥ 1. **The OpenAPI spec marks it "deprecated, use max_completion_tokens"** and notes some providers enforce a minimum of 16 [CHAT]. On reasoning models it covers reasoning and visible output together, so a small value can return `finish_reason:"length"` with empty content [PAR]. |
| `max_completion_tokens` | integer ≥ 1, same meaning as `max_tokens` [PAR][CHAT] |
| `temperature` | float 0.0–2.0, default 1.0 [PAR] |
| `stream` | boolean. Uses SSE. When streaming, `usage` arrives once, in the final chunk before `[DONE]` [OVR]. |
| `response_format` | `{type:"json_object"}` or `{type:"json_schema", json_schema:{name, strict?, schema}}` [OVR]. Only some models support it. Use `provider.require_parameters: true` so the request routes only to providers that honour it [SO]. |
| `provider` | routing options: `order`, `allow_fallbacks` (default true), `require_parameters` (default false), `data_collection` ("allow"/"deny"), `zdr`, `only`, `ignore`, `quantizations`, `sort`, `max_price`, … [PROV] |
| `models`, `route`, `user`, `tools`, `tool_choice`, `seed`, `top_p`, `stop`, `plugins` | other optional fields [OVR] |

If a model does not support a parameter, the parameter is **silently ignored** [OVR].

**Response** [OVR]: `{id, choices[], created, model, object, system_fingerprint?, usage}`. Each choice has `finish_reason` (normalised to `tool_calls|stop|length|content_filter|error`), `native_finish_reason`, `message{role, content, tool_calls?}` (or `delta` when streaming), and an optional `error`. `usage` has `prompt_tokens`, `completion_tokens`, `total_tokens`, optional `prompt_tokens_details.cached_tokens`, optional `completion_tokens_details.reasoning_tokens`, optional **`cost` (in credits)**, `is_byok`, and `cost_details` [OVR]. For non-streaming requests, usage is always returned [OVR]. Generation stats can be fetched later with `GET /api/v1/generation?id=<id>` [OVR].

## 3. Models list

- `GET /api/v1/models` returns `{data:[Model], total_count, links:{next}}` [MOD]. It returns **text-output models only** unless `output_modalities` is given. Other filters: `supported_parameters` (e.g. `tools`), `sort` (e.g. `pricing-low-to-high`, `newest`), and optional `offset`/`limit` pagination (default 500, max 1000) [MOD].
- Single model: `GET /api/v1/model/{author}/{slug}`. Aliases resolve. It **returns 404 if the model does not exist and is not an alias** [MOD].
- Model fields [MOD]: `id`, `canonical_slug`, `name`, `created`, `description`, `context_length` (tokens), `architecture` (input/output modalities, tokenizer), `pricing`, `top_provider`, `per_request_limits`, `supported_parameters`, `default_parameters`, and **`expiration_date`** (a deprecation date, or null).
- **Pricing units** [MOD]: "All pricing values are in USD per token/request/unit", **sent as strings** (e.g. `"prompt": "0.0000025"`). `"0"` means free. Keys: `prompt`, `completion`, `request`, `image`, `web_search`, `internal_reasoning`, `input_cache_read`, `input_cache_write`, and an optional `overrides[]`. Overrides cover conditional pricing, such as a higher price above a prompt-token threshold or in a UTC time window. Parse with a decimal type and multiply by 1e6 to show USD per million tokens.
- **Auth for /models**: the docs' curl examples send no key [MOD], but the OpenAPI spec declares a global `apiKey` security scheme and lists a `401` response [MODAPI]. Whether the endpoint works without a key is **[unverified]**, so send the key anyway.
- **Retired or unavailable models**: a chat request naming an unknown model returns typed error `not_found` / **404** [ERR][CHAT]. Use `expiration_date` to warn users before a model is removed [MOD]. If no provider meets the routing requirements, the error is **503** [ERR]. What a call to an already-expired slug returns is not documented explicitly **[unverified]**; assume 404.
- **Free variants** [FREE]: the `:free` suffix is a *catalog variant* with its own models-API entry (own pricing, context length and endpoints). Only models that list one support it. Free variants "may have different rate limits or availability". **Warning:** if a `:free` model appears in a `models` fallback array, the fallback to a paid model is billed [FREE].

## 4. Key info: `GET /api/v1/key`

- The path is `/api/v1/key`: "Get information on the API key associated with the current authentication session" [KEY][LIM]. The legacy `/auth/key` path is not mentioned anywhere in the fetched pages **[unverified]**.
- Returns `data` with: `label`, `limit` (USD or null), `limit_reset`, `limit_remaining`, `include_byok_in_limit`, `usage` / `usage_daily` / `usage_weekly` / `usage_monthly` (USD), the `byok_*` counterparts, `is_free_tier`, `free_model_daily_requests{used, limit, remaining}`, `budgets[]`, and `effective_budget`. A `rate_limit` object is deprecated [LIM][KEY].
- The documented responses are `200`, `401` and `500` [KEY]. That makes it a good **connection test**: 200 means the key is valid, 401 means the key is bad or expired [MGMT].
- **Cost**: it calls no model, and none of the pages list a charge for it. However, no page states explicitly that it is free, so "free connection test" is **[unverified]**, though highly likely.

## 5. Errors

Error body: `{"error":{"code":<int>,"message":"...","metadata":{...}}}`. The HTTP status equals `code` only for invalid requests or out-of-credit failures [ERR]. **Once a provider has accepted the request, the status is 200** and any error appears in the body. When streaming, it arrives as an SSE chunk with `finish_reason:"error"`. A non-streaming request can also get `200` with an `error` object and no `choices` [ERR][LIM]. Always check `body.error`, even on a 200.

| Code | Meaning [ERR] |
|---|---|
| 400 | Bad request (invalid or missing params, CORS). Typed variants include `context_length_exceeded` and `invalid_prompt`. |
| 401 | Invalid credentials (disabled or invalid key, expired OAuth session) |
| 402 | Insufficient credits (account or key). `metadata.limit_source` is `openrouter_credits`, `openrouter_key_limit`, or `openrouter_in_flight_budget`. The last one comes with `Retry-After`. [LIM] |
| 403 | Forbidden: insufficient permissions, guardrail block, moderation flag, or budget block. On a moderation error, `metadata` holds `reasons[]`, `flagged_input` (≤100 chars), `provider_name` and `model_slug`. |
| 404 | `not_found`: model or resource does not exist |
| 408 | Request timed out |
| 429 | Rate limited. Honour `Retry-After` and back off. It can also come from the upstream provider (`metadata.provider_code`). [LIM] |
| 502 | Chosen model is down or returned an invalid response (`provider_unavailable`) |
| 503 | No provider meets your routing requirements (`provider_overloaded`). May include `Retry-After`. |

Branch on `error.metadata.error_type` and `limit_source`, not on message text [ERR].

## 6. Rate limits

- Paid models: no platform-level request cap is documented. The only limits are Cloudflare DDoS protection and upstream-provider limits [LIM].
- `:free` variants: **20 requests/min**. The daily cap is **50/day if less than 10 credits were ever purchased, and 1000/day at 10 credits or more** [LIM].
- **Extra accounts or keys do not raise rate limits**, because capacity is governed globally [LIM]. Issuing per-student keys therefore does not multiply free-model quota.
- A negative account balance can cause errors **even on free models** [LIM].

## 7. Per-student limited keys

- In the dashboard, each key gets a name and a credit limit (or no limit). Once a key has used up its limit, it is rejected until the limit is raised or resets (daily, weekly or monthly) [AUTH]. OpenRouter recommends a limit on every key [AUTH].
- Programmatic creation needs a **Management API key**, created at `/settings/management-keys`. Management keys **cannot call completion endpoints** [MGMT]. Endpoints: `GET/POST /api/v1/keys`, `GET/PATCH/DELETE /api/v1/keys/{hash}` [MGMT].
- `POST /api/v1/keys` body [CREATE]: `name`, `limit` (USD), `limit_reset` (`daily|weekly|monthly|null`), `include_byok_in_limit`, `expires_at` (ISO), and optional `workspace_id` / `creator_user_id`. The plaintext `key` is **returned only once**.
- Set an expiration on management keys. After it passes, calls get `401 API key expired` [MGMT].
- Organizations can also cap a group of keys with a workspace budget or guardrail budgets [CAP][LIM].

## 8. Contradictions and caveats

1. **Key-limit exhaustion: 402 or 403?** [LIM]'s "Handling 402" section maps `openrouter_key_limit` to 402. [ERR] and [LIM]'s "Budget limits" section say the key's own spent limit is rejected with **403** and `limit_source: openrouter_key_limit`. Handle both statuses and branch on `limit_source`.
2. `max_tokens` is marked deprecated in the OpenAPI spec [CHAT] but is still documented as a normal parameter [PAR][OVR]. Prefer `max_completion_tokens` and accept either.
3. Attribution header: the current name is `X-OpenRouter-Title`. `X-Title` is legacy [ATTR].
