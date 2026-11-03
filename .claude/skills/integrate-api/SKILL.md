---
name: integrate-api
description: Use when the application must get data from, or send data to, an external API or data source (market data, filings, statistics, an AI model, email, any web service), or when such an integration fails, is slow or hits rate limits.
---

# Integrate an external API into the application

Build the integration **inside the app**: a client module the app calls, settings for secrets, error handling,
caching, and tests that do not need the network. Fetching data once for the conversation is not an integration.

## Inputs

- `docs/product.md` (which data, how fresh), `docs/architecture.md` (data-access part, external services table).
- The provider's **official documentation**: endpoint, authentication, rate limits, terms of use (including whether
  the data may be shown to the app's users or stored). Read it; do not rely on memory. If it cannot be read, say so
  and mark the details `[unverified]` in `docs/architecture.md`.

## Actions

1. **Record the service** in the external services table of `docs/architecture.md`: purpose, setting names, cost
   and free tier, terms checked (date). Stop and ask before choosing anything that costs money.
2. **Settings and secrets.** Add each setting name with a placeholder to `app/.env.example`; the real values go in
   `app/.env`, which is git-ignored and which you never read, print, or ask the student to paste into the chat. Load
   settings in one place (for example `app/config.py`) and fail with a clear message when one is missing. Check
   that `.gitignore` covers `.env`.
3. **Client module** (for example `app/clients/<service>.py`): one function per operation the app needs, returning
   plain data the rest of the app understands (not raw responses). Inside it:
   - timeouts on every request; a clear error type for "service unavailable", "not found", "bad credentials";
   - respect rate limits and any required identification header; retry only safe requests, a few times, with a
     pause;
   - validate the response shape and units before returning; keep source and retrieval time with the data when
     users rely on it.
4. **Caching or storage** when data changes slowly or calls are limited: cache to disk or the database
   (`manage-data`) with a clear expiry.
5. **Use it in the app** through the logic layer, never directly from interface code. Show users a helpful message
   when the service fails, and the data's source and date when that matters.
6. **Tests** (`test-and-check`): save one small, real-shaped response as a fixture (removing any personal data or
   keys) or write a synthetic one labelled as such; test parsing, units, errors (timeout, 404, malformed data) and
   the cache with the network replaced by the fixture. Optionally one live "smoke" check the student runs by hand,
   never part of the default test command.

## Outputs

Client module, settings in `app/.env.example`, config loading, cache if needed, tests with fixtures, updated
`docs/architecture.md`, a change report.

## Verification

- Default tests pass with the network off.
- One live call made by the running app returned real data (when the student has set the key), or the gap is
  stated. Never print the key or full authorised URLs in the report.
- Failing service shows a user-facing message, not a crash (checked with a simulated failure).

## Stop when

- The feature works end to end with real data, or works with fixtures and the live step is clearly left to the
  student.
- **Stop and ask** if the terms forbid the intended use, the service needs payment, the key would have to be
  shipped to users' browsers, or the provider's documentation cannot be found.

## Common mistakes

- Calling the API from the interface on every page load.
- Tests that hit the live API (slow, flaky, use up limits).
- Committing a key "just for testing"; if it happens, the key must be revoked, not just deleted.
