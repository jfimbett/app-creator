# RESPONSE — B04-research-openrouter

- From: default → to: owner (top-level Claude Code session)
- Captured by: scripts/dispatch-step.mjs from the `result` field of `claude -p --output-format json`
- Session id: f5ca7688-f326-48df-afa0-cdd89e198f99 (local Claude Code transcript; not committed)
- Finished: 2026-11-03T17:08:26.702Z; exit code 0; status completed
- Redaction: only explicit [REDACTED:<kind>] markers were inserted; otherwise verbatim.

<!-- VERBATIM:BEGIN -->
I've written `docs/research/openrouter.md` from 18 official OpenRouter doc pages. I didn't edit any other file, install anything or commit. The file is about 1,450 words, a bit over the ~1,300 target, because about 150 of those are the list of cited URLs. The new `docs/TOOLKIT.md` and `runs/bootstrap/B06-agents/` in the working tree are not mine.

Things in the docs that differ from what you might expect:

- **Title header renamed:** the attribution header is now `X-OpenRouter-Title`. `X-Title` still works, but only for backwards compatibility.
- **`max_tokens` deprecated:** the API spec marks it deprecated in favour of `max_completion_tokens`, though the parameters page still lists it normally. On reasoning models it covers reasoning as well as visible output, so a small value can return empty content.
- **Key spending limit hit, 402 or 403:** the docs contradict each other on the status code. One section says 402, another says 403. Both cases carry `limit_source: openrouter_key_limit`, so the app should handle both codes and branch on that field.
- **Errors can arrive with HTTP 200:** once a provider has accepted the request, failures come back in the body (or as a stream event). The app must check `body.error` even on a 200.
- **Per-student keys don't add quota:** OpenRouter applies rate limits globally, so extra keys or accounts don't raise them. Free variants are capped at 20 requests/min, plus 50/day (or 1000/day once 10+ credits have ever been bought).
- **Free models can still fail:** a negative account balance can cause errors even on free models.
- **Fallbacks can cost money:** if a `:free` model is listed with fallbacks, a fallback to a paid model is billed.
- **Separate admin key needed:** issuing keys programmatically needs a management key, which cannot call the chat endpoint. Each new key's secret is shown only once.

## Handoff
Changes: `docs/research/openrouter.md` (new; `docs/research/` created).
Verification evidence: all fetched with HTTP 200 on 2026-11-03: https://openrouter.ai/docs/llms.txt, …/_llms/docs.txt, …/_llms/api-reference.txt, …/quickstart.md, …/api_reference/{overview,authentication,errors-and-debugging,limits,parameters}.md, …/app-attribution.md, …/guides/overview/models.md, …/guides/overview/auth/management-api-keys.md, …/guides/routing/model-variants/free.md, …/guides/routing/provider-selection.md, …/guides/features/structured-outputs.md, …/guides/best-practices/capping-shared-agent-keys.md, …/api/api-reference/api-keys/{get-current-api-key,create-a-new-api-key}.md, …/api/api-reference/models/list-all-models-and-their-properties.md, …/api/api-reference/chat/create-a-chat-completion.md, …/faq.md. No fetch failures. Four points the docs don't state are marked [unverified]: whether `GET /models` works without a key; whether `GET /api/v1/key` is free (no charge is documented, but nothing says it's free); the legacy `/auth/key` path; and the exact error for a retired model slug (assumed 404).
Remaining findings: D5/D6 only pin package versions and say nothing about OpenRouter, so there is no direct contradiction. Note for the backend: no OpenRouter SDK is needed, because httpx with a Bearer header plus respx mocks covers it. Surprises: key-limit exhaustion is documented as both 402 and 403; `max_tokens` is deprecated; the title header is renamed; errors can arrive with HTTP 200; and per-key rate limits don't multiply.
Next action: run B05 (stack research), then build the OpenRouter client with tests that mock 401/402/403/429 and the error-inside-a-200 case.
<!-- VERBATIM:END -->
