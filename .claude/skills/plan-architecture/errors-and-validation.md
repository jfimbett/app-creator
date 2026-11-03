# Validation and error handling

Two rules: **the server validates everything**, and **users see plain messages while the log keeps the
details.**

## Validation

| Where | Purpose | Tool |
|---|---|---|
| Server (required) | security and correctness: anything reaching the API may be wrong or hostile | pydantic models, `Query`/`Path` constraints, checks in logic |
| Client (optional) | help the user type: instant hints, disabled submit | HTML attributes (`required`, `min`, `type="date"`) and small checks |

Client-side checks can be skipped by anyone with a browser's developer tools; they never replace the server's.

Server-side checklist:

- [ ] Every request body is a pydantic model; no `dict` parameters.
- [ ] Numbers have bounds (`Field(gt=0, le=300)`), strings a maximum length and, where known, a pattern.
- [ ] Ids from the path are checked to exist (`404`) and, with accounts, to belong to the user (`add-accounts`).
- [ ] Rules that need data (duplicate name, end date after start date) are checked in logic and return `409`
      or `422` with a clear code.
- [ ] Uploaded files: size limit, allowed types checked by content, never a path from the user.
- [ ] Text that will be shown again is rendered as text (React escapes it by default; avoid
      `dangerouslySetInnerHTML`).

```python
from datetime import date
from pydantic import BaseModel, Field, model_validator

class PeriodIn(BaseModel):
    start: date
    end: date
    label: str = Field(min_length=1, max_length=80)

    @model_validator(mode="after")
    def end_after_start(self):
        if self.end < self.start:
            raise ValueError("End date must be on or after the start date.")
        return self
```

## Turning failures into the error envelope

Two kinds of errors:

- **Expected** (bad input, not found, upstream down, not configured): a specific code and a plain message.
  Log at `info`/`warning`.
- **Unexpected** (a bug): log the full traceback at `error` with a reference id; the user gets a generic
  message and that id. Never the traceback.

```python
# <backend>/app/errors.py
import logging, uuid
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

log = logging.getLogger("app")

class AppError(Exception):
    def __init__(self, status: int, code: str, message: str, details: object | None = None):
        self.status, self.code, self.message, self.details = status, code, message, details

def envelope(status: int, code: str, message: str, details: object | None = None) -> JSONResponse:
    return JSONResponse(status_code=status, content={"error": {"code": code, "message": message, "details": details}})

def install_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def _app_error(_: Request, exc: AppError):
        log.info("app error %s: %s", exc.code, exc.message)
        return envelope(exc.status, exc.code, exc.message, exc.details)

    @app.exception_handler(RequestValidationError)
    async def _invalid(_: Request, exc: RequestValidationError):
        fields = [{"field": ".".join(str(p) for p in e["loc"][1:]), "message": e["msg"]} for e in exc.errors()]
        return envelope(422, "invalid_input", "Some fields need fixing.", {"fields": fields})

    @app.exception_handler(Exception)
    async def _unexpected(_: Request, exc: Exception):
        ref = uuid.uuid4().hex[:8]
        log.exception("unexpected error ref=%s", ref)
        return envelope(500, "internal_error", f"Something went wrong on our side (reference {ref}). Please try again.")
```

Use it from routes and logic:

```python
raise AppError(404, "member_not_found", "No member with that id.")
raise AppError(503, "source_unavailable", "The data source is not responding. Showing nothing rather than old data.")
raise AppError(503, "not_configured", "This feature needs a setting that is not configured. The rest of the app works.")
```

Note: FastAPI's own `HTTPException` returns `{"detail": ...}`. Either use `AppError` everywhere or add a handler
for `HTTPException` that converts it to the envelope, so the frontend sees one shape.

## What the user sees

| Situation | Message (example) | Next step offered |
|---|---|---|
| invalid field | "End date must be on or after the start date." next to the field | fix the field |
| not found | "We could not find that member. It may have been deleted." | back to the list |
| backend down (network) | "Could not reach the server. Is the backend running?" | Try again |
| upstream service down | "The data source is not responding." plus how old any cached data is | Try again / use cached data |
| not configured | "AI summaries are not set up. Everything else works." | how to configure (in the README) |
| unexpected | "Something went wrong on our side (reference 3fa2c1d9)." | Try again |

Never show: tracebacks, SQL, file paths, environment values, keys, internal ids that mean nothing to the user.

## Logging

- Use `logging`, not `print`. Log the reference id, the code, and the inputs that matter, **without** secrets or
  personal data (no full request bodies, no `Authorization` headers, no keys in URLs).
- Development: readable lines in the `npm run dev` terminal. Tests: assert on the response, not on the log text.

## Tests to write

- [ ] Invalid input returns `422` with `error.code == "invalid_input"` and the field name.
- [ ] A not-found id returns `404` with its code.
- [ ] An upstream failure (mocked with `respx`, which is in the backend's dependencies) returns `503` with its code,
      not `500`.
- [ ] An unexpected exception returns `500`, a reference, and no traceback text in the body.
- [ ] Frontend (Vitest): the API client turns each of these into the right UI state
      ([ui-states-and-forms.md](../design-interface/ui-states-and-forms.md)).
