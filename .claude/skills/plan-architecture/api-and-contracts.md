# API design and typed contracts

The API is the contract between the frontend and the backend. Write it down (the API table in
`<docs>/architecture.md`), type it on both sides, and change it deliberately.

## Naming

| Rule | Good | Avoid |
|---|---|---|
| Everything under `/api` (the Next.js rewrite forwards only that) | `/api/members` | `/members` |
| Plural nouns for collections, ids in the path | `GET /api/members/42` | `GET /api/getMember?id=42` |
| Sub-resources for "belongs to" | `GET /api/members/42/runs` | `GET /api/runs-of-member` |
| Query parameters for filters, sort, pages | `?week=2026-W12&sort=-total_km` | `/api/members/sorted-by-total` |
| Lower-case kebab-case paths, snake_case JSON fields | `/api/weekly-totals`, `total_km` | `/api/WeeklyTotals`, mixed casing |
| HTTP methods carry the verb | `POST /api/runs`, `DELETE /api/runs/7` | `POST /api/deleteRun` |
| Actions that are not CRUD get a clear verb sub-path | `POST /api/imports/3/retry` | overloading `PUT` |

Status codes: `200` read/update, `201` created (with the new object), `204` deleted, `400` malformed request,
`404` not found, `409` conflict (duplicate), `422` invalid input, `429` rate-limited, `502`/`503` an upstream
service failed or is unavailable, `500` unexpected. Never `200` with an error inside.

## Typed contracts: pydantic on the server

```python
# <backend>/app/api/schemas.py
from datetime import date
from pydantic import BaseModel, Field

class RunIn(BaseModel):
    member_id: int = Field(gt=0)
    day: date
    distance_km: float = Field(gt=0, le=300)

class Run(RunIn):
    id: int

class WeeklyRow(BaseModel):
    member_id: int
    name: str
    total_km: float
    change_km: float | None          # None = not computable; change_note says why
    change_note: str | None = None
```

```python
# <backend>/app/main.py
from fastapi import FastAPI, Query
from .api.schemas import Run, RunIn, WeeklyRow

@app.post("/api/runs", response_model=Run, status_code=201)
def create_run(body: RunIn) -> Run: ...

@app.get("/api/weekly-totals", response_model=list[WeeklyRow])
def weekly_totals(week: str = Query(pattern=r"^\d{4}-W\d{2}$")) -> list[WeeklyRow]: ...
```

`response_model` filters out fields you did not declare (no accidental leaks) and documents the endpoint at
http://127.0.0.1:8000/docs while `npm run dev` runs.

## Typed contracts: TypeScript on the client

Mirror each response model as a type in `<frontend>/lib/api-types.ts`, and call the API through one small client
so error handling is the same everywhere:

```ts
// <frontend>/lib/api.ts
export type WeeklyRow = {
  member_id: number; name: string; total_km: number;
  change_km: number | null; change_note: string | null;
};

export type ApiError = { code: string; message: string; details?: unknown };
export type Result<T> = { ok: true; data: T } | { ok: false; error: ApiError };

export async function apiGet<T>(path: string): Promise<Result<T>> {
  try {
    const res = await fetch(path, { cache: "no-store" });
    const body: unknown = await res.json().catch(() => null);
    if (res.ok) return { ok: true, data: body as T };
    const err = (body as { error?: ApiError } | null)?.error;
    return { ok: false, error: err ?? { code: `http_${res.status}`, message: "The server returned an error." } };
  } catch {
    return { ok: false, error: { code: "network", message: "Could not reach the server. Is the backend running?" } };
  }
}
```

Keep a test that the types and the backend agree, at least for the main endpoint: a pytest test asserting the
JSON keys of a response, and a Vitest test that the client handles `ok`, an error envelope and a network
failure. If the API grows past a handful of endpoints, generating types from FastAPI's OpenAPI schema
(`/openapi.json`) is an option; record it as a decision first.

## Lists and pagination

Paginate any list that can grow beyond about 100 items. Start with limit/offset:

```
GET /api/runs?limit=50&offset=100
→ {"items": [...], "total": 1234, "limit": 50, "offset": 100}
```

- Cap `limit` on the server (`Query(50, ge=1, le=200)`); never trust the client's number.
- Return a stable order (`ORDER BY day DESC, id DESC`), or pages skip and repeat rows.
- Use cursor pagination (`?after=<last id>`) only when data changes while the user pages, or for very large lists.

Short, bounded lists (a handful of options) may be returned as a plain array.

## The error envelope

Every error response has the same shape, so the frontend handles errors in one place:

```json
{"error": {"code": "invalid_week", "message": "Week must look like 2026-W12.", "details": {"field": "week"}}}
```

- `code`: stable, snake_case, for code to branch on.
- `message`: plain words for the user, with a next step where possible.
- `details`: optional; field errors for forms; never stack traces, SQL, file paths or keys.

How to produce it in FastAPI: [errors-and-validation.md](errors-and-validation.md).

## Versioning (keep it light)

- Start with `/api/...` and no version. Frontend and backend live in one repository and change together.
- Adding a field is safe. Removing or renaming a field, or changing its meaning or unit, is a **breaking change**:
  change both sides in the same commit, update the API table, and note it in the decision log.
- Introduce `/api/v2/...` only when a client you do not control (another team, a mobile app) depends on the old
  shape.

## Checklist per endpoint

- [ ] Row in the API table (method, path, request, response model, errors).
- [ ] pydantic request and response models; constraints on every input.
- [ ] Matching TypeScript type; called through the shared client.
- [ ] Error codes listed and returned in the envelope.
- [ ] pytest: normal case, invalid input (422 + envelope), not found or empty case.
- [ ] Lists: limit capped, stable order.
