# Security checklist before sharing the app

Companion to [SKILL.md](SKILL.md). Go through it before anyone other than the team uses the app, and before a
`security-reviewer` pass (`review-changes`). Mark each line ok / missing / not applicable in the readiness report.
Snippets are FastAPI and Next.js sketches: add a test for each one you adopt.

## 1. Network exposure and host binding

- [ ] The launchers bind backend and frontend to `127.0.0.1` (only this computer). Do not change it to `0.0.0.0`
      for a demo; on a shared network that exposes the app to everyone on it.
- [ ] The backend is reached only through the frontend's `/api/*` rewrite; in production it is not publicly
      exposed on its own port unless the host's design requires it.
- [ ] Containers bind `0.0.0.0` inside, but publish ports as `127.0.0.1:3000:3000` locally ([docker.md](docker.md)).
- [ ] No "fetch any URL" endpoint; outgoing calls use an allowlist (`integrate-api`).

## 2. CORS (cross-origin resource sharing)

With the same-origin `/api/*` rewrite, the browser never makes cross-origin calls, so the backend needs **no CORS
at all**. Add CORS only if another origin must call the API, and then list origins exactly:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,   # e.g. ["https://app.example.org"], from a setting; never ["*"]
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
    allow_credentials=False,                  # True only with exact origins and a real need
)
```

- [ ] No `allow_origins=["*"]` together with cookies or credentials.
- [ ] A test sends `Origin: https://evil.example` and checks no `access-control-allow-origin` header comes back.

## 3. Security headers

Set them in `next.config.ts` (the frontend serves the pages):

```ts
async headers() {
  return [{
    source: "/:path*",
    headers: [
      { key: "X-Content-Type-Options", value: "nosniff" },
      { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
      { key: "X-Frame-Options", value: "DENY" },
      { key: "Permissions-Policy", value: "camera=(), microphone=(), geolocation=()" },
    ],
  }];
},
```

- [ ] The headers above present (check with `curl -sI http://127.0.0.1:3000/ | grep -i -E "x-content|referrer|x-frame"`).
- [ ] A Content-Security-Policy, if added, is tested with the Playwright journeys (a too-strict policy breaks
      scripts and styles; Next.js documents a nonce-based setup).
- [ ] `Strict-Transport-Security` only on the HTTPS production host (usually set by the host).

## 4. Debug, errors and input

- [ ] Debug off by default (`DEBUG=0`); the app refuses to start with debug on and a non-local host.
- [ ] FastAPI's interactive docs (`/docs`, `/openapi.json`) disabled in production if the API is not meant to be
      public: `FastAPI(docs_url=None, redoc_url=None, openapi_url=None)` when not in development.
- [ ] Error responses are short and friendly; no stack traces, SQL or file paths to the browser.
- [ ] Every input is validated on the server (Pydantic models, path patterns, size limits); uploads checked for
      type and size and stored outside any served folder.
- [ ] SQL uses parameters only; no `dangerouslySetInnerHTML` with user or external content.

## 5. Logging without secrets or personal data

- [ ] Logs contain method, path (no query string if it can carry data), status, duration, and an error message;
      never headers, cookies, request bodies, keys, tokens, passwords or full external URLs with keys.
- [ ] Exceptions from HTTP clients are re-raised with redacted messages (`raise Unavailable("timeout") from None`).
- [ ] Run the tests with logging on and search the captured output for a fake key you passed in (`caplog` in
      pytest): it must not appear.

## 6. Accounts, sessions and payments (only if present)

- [ ] Every data endpoint has a permission check and a test (`add-accounts`, [authn-authz.md](../add-accounts/authn-authz.md)).
- [ ] Cookies `HttpOnly`, `SameSite=Lax`, `Secure` in production; CSRF origin check on state-changing requests.
- [ ] Rate limit on sign-in and on expensive endpoints (AI calls, exports).
- [ ] Payments: test mode, webhook signature verified, duplicates ignored (`add-payments`).

## 7. Dependencies

Run from the repository root and read the output (do not blindly apply fixes):

```bash
(cd <frontend> && npm audit --omit=dev)          # runtime dependencies of the web app
(cd <backend> && .venv/bin/python -m pip install pip-audit && .venv/bin/python -m pip_audit -r requirements.lock)
```

Status: not run from this guide (no app is configured in the template); check each tool's `--help` first.

- [ ] High or critical findings in runtime dependencies are fixed by upgrading the pinned version (then
      `npm run setup` and `npm run verify`), or listed as known problems with the reason.
- [ ] `npm audit fix --force` is never run without review: it can jump major versions and break the app.
- [ ] `pip-audit` is a development tool: installing it in `<backend>/.venv` is fine; add it to the lockfile only
      if the team wants it in CI.
- [ ] No unused dependencies left from experiments.

## 8. Secrets and data

- [ ] [env-and-secrets.md](env-and-secrets.md): `.env` not tracked, search for leaked secrets done, rotation plan
      known.
- [ ] No database, cache, uploads or screenshots with real personal data committed.
- [ ] Data sources' terms allow showing (and storing) the data as the app does.

## Report

List every `missing` line with a severity (`blocker`, `major`, `minor`) in the readiness report and in "Known
problems" of `<docs>/plan.md`. Accepting a blocker or major as a risk is the owner's decision, never a delegated
one (`docs/TOOLKIT.md` §4).
