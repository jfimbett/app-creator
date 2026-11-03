# PROMPT — B04-research-openrouter

- Sender: owner (top-level Claude Code session)
- Receiver: default Claude Code agent (`--agent default`; the toolkit's agents do not exist yet — orchestrator B01 risk 4)
- Starting commit: 10e8c6f
- Skills: none; instruction paths: GOAL.md, PROGRESS.md
- Dispatch: `node scripts/dispatch-step.mjs --step runs/bootstrap/B04-research-openrouter --agent default --mode bypassPermissions --milestone bootstrap`
- Plan reference: runs/bootstrap/B01-orchestrator-bootstrap-plan/RESPONSE.md

<!-- DISPATCH:BEGIN -->
Research task for the App Creator build (see GOAL.md §7). Topic: OpenRouter API, from https://openrouter.ai/docs (API reference, authentication, errors, limits, models). Answer precisely: base URL; chat completions endpoint and request fields (model, messages, max_tokens / max_completion_tokens, temperature, stream, response_format, provider options); authentication header; optional attribution headers (HTTP-Referer, X-Title); response shape incl. usage; the models list endpoint (GET /api/v1/models) and its pricing fields and units (per-token strings?), context_length, how retired/unavailable models fail; key-info endpoint (GET /api/v1/key or /auth/key) — does it cost anything, what it returns (limit, usage), can it serve as a free connection test; error codes and meanings (400, 401, 402, 403 moderation, 408, 429, 502, 503) and error body shape; rate limits for free vs paid; key creation with credit limits (per-key spending limits / provisioning keys) for issuing separate limited keys per student. Do NOT recommend a specific model as "cheap/free" from memory; if the docs list free variants (":free" suffix), describe the mechanism only.
Rules: use only official documentation (fetch the pages; do not answer from memory), cite every claim with its URL and the retrieval date 2026-11-03, and mark anything you could not fetch as [unverified]. Write ONLY the one file named below (create docs/research/ if needed); do not edit any other file, do not install anything, do not commit. Keep the file under about 1300 words, as practical implementation notes. Never print or write secrets or email addresses. End your final message with:
## Handoff
Changes: <file written>
Verification evidence: <pages fetched (URLs) and any failures>
Remaining findings: <surprises, contradictions with the notes in PROGRESS.md decisions D5/D6>
Next action: <one line>
File: docs/research/openrouter.md

<!-- DISPATCH:END -->
