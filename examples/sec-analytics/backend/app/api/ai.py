"""The AI analyst endpoints (M5). Validates, builds the grounded context, calls the client, maps.

Boundary rules (milestones/architecture.md "OpenRouter boundary", brief §7):
- The person's key comes only in the `X-OpenRouter-Key` header, is passed to the client for one
  call and is never stored, logged or returned.
- `/api/ai/*` answers only this app's own pages: a foreign `Origin` or a cross-site
  `Sec-Fetch-Site` gets 403 `forbidden_origin`. This is a local teaching app, not an AI proxy.
- Body ≤ 64 KB; question 1–2,000 characters; at most 2 chats at once on the backend (a third gets
  409 `ai_busy`); no retries; a client that goes away cancels the upstream call, and the slot is
  freed in every case.
- A clearly out-of-scope question is refused before any model call (`logic/scope.py`).
"""

from __future__ import annotations

import asyncio
import json
import re
import threading
from collections.abc import Coroutine
from datetime import datetime, timezone
from typing import Annotated, Any, Literal

from fastapi import APIRouter, Depends, Request
from fastapi.responses import Response

from app.api.companies import _not_found, parse_cik
from app.api.deps import get_data, get_store
from app.clients.openrouter import AiError, OpenRouterClient
from app.clients.sec import companyfacts_url
from app.data.fixtures import FixtureStore
from app.data.source import DataSource
from app.errors import AppError
from app.logic import compare as compare_logic
from app.logic import retrieval
from app.logic.archive import is_valid_accession
from app.logic.citations import validate
from app.logic.filings import select_latest
from app.logic.prompting import build_messages
from app.logic.scope import KnownCompany, precheck
from app.logic.search import universe_from_tickers
from app.logic.statements import build_financials
from app.models.ai import (
    ChatResponse,
    Citation,
    ConnectionTestResponse,
    ContextInfo,
    ModelEntry,
    ModelsResponse,
    Refusal,
    Usage,
)

router = APIRouter(prefix="/api/ai", tags=["ai"])

MAX_BODY_BYTES = 64 * 1024
MAX_QUESTION = 2_000
MAX_COMPLETION_TOKENS = 800
MAX_CONCURRENT_CHATS = 2
POLL_SECONDS = 0.2
MODEL_ID = re.compile(r"^[A-Za-z0-9._:/-]{1,200}$")
_LOCAL_ORIGIN = re.compile(r"^http://(127\.0\.0\.1|localhost):\d{1,5}$")
LOCAL_HOSTS = frozenset({"127.0.0.1", "localhost"})
_KEY_TEXT = re.compile(r"^[\x21-\x7e]{1,300}$")
COMPARE_NAMES = {"fcf": "FCF", "fcf_margin": "FCF margin"}

DataDep = Annotated[DataSource, Depends(get_data)]
StoreDep = Annotated[FixtureStore, Depends(get_store)]


class ChatSlots:
    """At most `limit` chats at once. Thread-safe: test clients may run requests in threads."""

    def __init__(self, limit: int) -> None:
        self._limit = limit
        self._in_use = 0
        self._lock = threading.Lock()

    @property
    def in_use(self) -> int:
        return self._in_use

    def try_acquire(self) -> bool:
        with self._lock:
            if self._in_use >= self._limit:
                return False
            self._in_use += 1
            return True

    def release(self) -> None:
        with self._lock:
            self._in_use = max(0, self._in_use - 1)


class Cancelled(Exception):
    """The person's browser went away (Cancel or a closed tab) while the model was working."""


def check_origin(request: Request) -> None:
    """403 unless the request comes from this app's own page (or a tool with no Origin)."""
    origin = request.headers.get("origin")
    site = request.headers.get("sec-fetch-site")
    # The Host check stops DNS rebinding: a page on another name that resolves to 127.0.0.1.
    host = (request.headers.get("host") or "").rsplit(":", 1)[0].lower()
    if (
        host not in LOCAL_HOSTS
        or (origin is not None and not _LOCAL_ORIGIN.match(origin))
        or (site is not None and site not in {"same-origin", "none"})
    ):
        raise AppError(
            "forbidden_origin", "AI requests are accepted only from this app's own pages.", 403
        )


def _key(request: Request) -> str:
    key = (request.headers.get("x-openrouter-key") or "").strip()
    if not _KEY_TEXT.match(key):
        raise AppError(
            "ai_key_missing", "AI not configured: add your own OpenRouter key in AI settings.", 400
        )
    return key


def _client(request: Request) -> OpenRouterClient:
    return request.app.state.ai_client


def _as_app_error(error: AiError) -> AppError:
    return AppError(error.code, error.message, error.status, error.details)


async def run_upstream(request: Any, work: Coroutine[Any, Any, Any]) -> Any:
    """Run the upstream call as a task, cancelled if the client goes away."""
    task = asyncio.ensure_future(work)
    try:
        while True:
            done, _ = await asyncio.wait({task}, timeout=POLL_SECONDS)
            if done:
                return task.result()
            if await request.is_disconnected():
                task.cancel()
                raise Cancelled()
    finally:
        if not task.done():
            task.cancel()


# ------------------------------------------------------------------ request parsing


async def _json_body(request: Request) -> dict[str, Any]:
    too_large = AppError("request_too_large", "The request is larger than 64 KB.", 413)
    declared = request.headers.get("content-length")
    if declared is not None and (not declared.isdigit() or int(declared) > MAX_BODY_BYTES):
        raise too_large
    # Read in pieces and stop past the limit, also when no Content-Length was sent (chunked).
    parts: list[bytes] = []
    size = 0
    async for piece in request.stream():
        size += len(piece)
        if size > MAX_BODY_BYTES:
            raise too_large
        parts.append(piece)
    raw = b"".join(parts)
    try:
        body = json.loads(raw or b"{}")
    except ValueError:
        raise AppError("invalid_request", "The request body is not JSON.", 422) from None
    if not isinstance(body, dict):
        raise AppError("invalid_request", "The request body must be a JSON object.", 422)
    return body


def _scope_error(message: str) -> AppError:
    return AppError("invalid_scope", message, 422)


def _parse_scope(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, dict) or raw.get("kind") not in {"company", "filing", "comparison"}:
        raise _scope_error("The scope must be a company, a filing or a comparison.")
    kind = raw["kind"]
    if kind in {"company", "filing"}:
        if not isinstance(raw.get("cik"), str):
            raise _scope_error("The scope needs a company CIK.")
        scope = {"kind": kind, "cik": parse_cik(raw["cik"])}
        if kind == "filing":
            accession = raw.get("accession")
            if not isinstance(accession, str) or not is_valid_accession(accession):
                raise _scope_error("The filing scope needs a valid accession number.")
            scope["accession"] = accession
        return scope
    ciks, metrics = raw.get("ciks"), raw.get("metrics")
    if not isinstance(ciks, list) or not all(isinstance(c, str) for c in ciks):
        raise _scope_error("The comparison scope needs a list of CIKs.")
    normalized = list(dict.fromkeys(parse_cik(c) for c in ciks))
    if not compare_logic.MIN_COMPANIES <= len(normalized) <= compare_logic.MAX_COMPANIES:
        raise _scope_error("A comparison has 2–4 companies.")
    if (
        not isinstance(metrics, list)
        or not compare_logic.MIN_METRICS <= len(metrics) <= compare_logic.MAX_METRICS
        or any(m not in compare_logic.COMPARE_METRICS for m in metrics)
    ):
        raise _scope_error("Choose 1–6 comparison metrics.")
    return {"kind": "comparison", "ciks": normalized, "metrics": list(dict.fromkeys(metrics))}


def _parse_source(raw: Any) -> Literal["demo", "live"]:
    if raw in (None, "demo"):
        return "demo"
    if raw == "live":
        return "live"
    raise AppError("invalid_request", "source must be demo or live.", 422)


# ------------------------------------------------------------------ grounded context


class _Scoped:
    """The loaded data of a scope: fact sources, the document, the context line and companies."""

    def __init__(self) -> None:
        self.sources: list[retrieval.FactSource] = []
        self.document: retrieval.DocumentInput | None = None
        self.metric_ids: list[str] | None = None
        self.loaded: list[KnownCompany] = []
        self.kind = ""
        self.filing_label = ""
        self.has_document = False


def _company(data: DataSource, cik: str, source: str) -> tuple[retrieval.FactSource, KnownCompany]:
    facts = data.companyfacts(cik, source)
    if facts.data is None:
        raise _not_found(cik)
    profile = data.submissions(cik, source).data or {}
    tickers = [t for t in profile.get("tickers") or [] if isinstance(t, str) and t]
    ticker = tickers[0] if tickers else cik
    financials = build_financials(facts.data, companyfacts_url(cik))
    name = profile.get("name") or facts.data.get("entityName") or cik
    return retrieval.FactSource(cik, ticker, financials.series), KnownCompany(ticker, name)


def _document(data: DataSource, cik: str, ticker: str, filing: Any, source: str):
    parsed = data.parsed_filing(cik, filing, source)
    return retrieval.DocumentInput(
        cik=cik,
        ticker=ticker,
        form=filing.form,
        accession=filing.accession,
        filing_date=filing.filing_date,
        blocks=parsed.document.blocks,
        section_of_block=parsed.sections.section_of_block,
        section_labels={s.id: s.item for s in parsed.sections.sections},
    )


def _load_scope(
    data: DataSource, scope: dict[str, Any], source: str, *, with_document: bool = True
) -> _Scoped:
    """The scope's data. The preview passes `with_document=False`: it only says whether a 10-K
    exists, so opening the panel never downloads a filing document."""
    scoped = _Scoped()
    scoped.kind = scope["kind"]
    today = datetime.now(timezone.utc).date()
    if scope["kind"] == "comparison":
        for cik in scope["ciks"]:
            fact_source, company = _company(data, cik, source)
            scoped.sources.append(fact_source)
            scoped.loaded.append(company)
        scoped.metric_ids = scope["metrics"]
        return scoped
    fact_source, company = _company(data, scope["cik"], source)
    scoped.sources, scoped.loaded = [fact_source], [company]
    listed = data.filing_list(scope["cik"], source, today)
    rows = listed.rows if listed else []
    if scope["kind"] == "filing":
        filing = next((r for r in rows if r.accession == scope["accession"]), None)
        if filing is None:
            raise AppError(
                "filing_not_found",
                "This company has no 10-K or 10-Q with that accession number.",
                404,
            )
        if with_document:
            scoped.document = _document(data, scope["cik"], fact_source.ticker, filing, source)
        scoped.has_document = True
        scoped.filing_label = f"{filing.form} {filing.accession}"
        return scoped
    annual = select_latest(rows, "").annual if rows else None
    if annual is None:
        return scoped
    if not with_document:
        scoped.has_document = annual.document_url is not None and (
            source == "live" or bool(annual.document_in_snapshot)
        )
        return scoped
    try:
        scoped.document = _document(data, scope["cik"], fact_source.ticker, annual, source)
        scoped.has_document = True
    except AppError:
        scoped.document = None  # no readable 10-K: facts only, and the line says so
    return scoped


def _years(facts: tuple[retrieval.Fact, ...]) -> str:
    """The fiscal years actually sent, e.g. "FY2022–FY2026"."""
    labels = sorted(f.fiscal_year_label for f in facts)
    return f"{labels[0]}–{labels[-1]}" if labels else "no years"


def _line(scoped: _Scoped, facts: tuple[retrieval.Fact, ...]) -> str:
    tickers = [s.ticker for s in scoped.sources]
    if scoped.kind == "comparison":
        names = [COMPARE_NAMES.get(m, m.replace("_", " ")) for m in scoped.metric_ids or []]
        return f"Context: {', '.join(tickers)} facts for {', '.join(names)}"
    if scoped.kind == "filing":
        return f"Context: {tickers[0]} {scoped.filing_label} passages + {tickers[0]} facts"
    passages = " + 10-K passages" if scoped.has_document else " (no 10-K text available)"
    return f"Context: {tickers[0]} facts {_years(facts)}{passages}"


def _known(data: DataSource, store: FixtureStore, source: str) -> list[KnownCompany]:
    """Every company the app could name: the demo universe, or SEC's ticker file in live mode."""
    universe = (
        universe_from_tickers(data.ticker_map().data) if source == "live" else store.universe()
    )
    return [KnownCompany(c.primary_ticker, c.name) for c in universe]


# ------------------------------------------------------------------ endpoints


@router.get("/models", response_model=ModelsResponse, dependencies=[Depends(check_origin)])
async def list_models(request: Request) -> ModelsResponse:
    """The models the person's key can use, with prices per million tokens. None is preselected."""
    try:
        models = await _client(request).list_models(_key(request))
    except AiError as error:
        raise _as_app_error(error) from None
    return ModelsResponse(
        models=[ModelEntry(**m.__dict__) for m in models], fetched_at=datetime.now(timezone.utc)
    )


@router.post(
    "/test-connection", response_model=ConnectionTestResponse, dependencies=[Depends(check_origin)]
)
async def test_connection(request: Request) -> ConnectionTestResponse:
    """Checks the key with OpenRouter's key-info call (no model is called)."""
    try:
        info = await _client(request).key_info(_key(request))
    except AiError as error:
        raise _as_app_error(error) from None
    return ConnectionTestResponse(
        ok=True,
        label=info.label,
        limit_remaining_usd=info.limit_remaining_usd,
        message="Connected",
    )


@router.post("/context", response_model=ContextInfo, dependencies=[Depends(check_origin)])
async def context_preview(request: Request, data: DataDep) -> ContextInfo:
    """What a question in this scope would be grounded on. Needs no key and calls no model."""
    body = await _json_body(request)
    scope, source = _parse_scope(body.get("scope")), _parse_source(body.get("source"))
    scoped = await asyncio.to_thread(_load_scope, data, scope, source, with_document=False)
    context = retrieval.build_context(scoped.sources, scoped.metric_ids, None, "")
    return ContextInfo(
        line=_line(scoped, context.facts),
        facts=len(context.facts),
        passages=0,
        chars=context.chars,
    )


@router.post("/chat", response_model=ChatResponse, dependencies=[Depends(check_origin)])
async def chat(request: Request, data: DataDep, store: StoreDep) -> ChatResponse | Response:
    """One grounded question about the current scope, with checked source references."""
    key = _key(request)
    body = await _json_body(request)
    model = body.get("model")
    if not isinstance(model, str) or not MODEL_ID.match(model):
        raise AppError("invalid_model", "Choose a model in AI settings.", 422)
    question = body.get("question")
    if not isinstance(question, str) or not 1 <= len(question.strip()) <= MAX_QUESTION:
        raise AppError(
            "invalid_question",
            "Type a question of 1 to 2,000 characters.",
            422,
            {"max": MAX_QUESTION},
        )
    question = question.strip()
    scope, source = _parse_scope(body.get("scope")), _parse_source(body.get("source"))
    # Price, valuation and advice questions are refused before any SEC data is loaded.
    early = precheck(question, loaded=[], known=[], has_context=True)
    if early is not None:
        return ChatResponse(
            answer="",
            citations=[],
            invalid_references=[],
            citation_note=None,
            refusal=Refusal(code=early.code, message=early.message),
            context=ContextInfo(line="", facts=0, passages=0, chars=0),
            model=model,
            usage=None,
            finish_reason=None,
        )

    scoped = await asyncio.to_thread(_load_scope, data, scope, source)
    context = retrieval.build_context(scoped.sources, scoped.metric_ids, scoped.document, question)
    info = ContextInfo(
        line=_line(scoped, context.facts),
        facts=len(context.facts),
        passages=len(context.passages),
        chars=context.chars,
    )
    known = await asyncio.to_thread(_known, data, store, source)
    refusal = precheck(
        question,
        loaded=scoped.loaded,
        known=known,
        has_context=bool(context.facts or context.passages),
    )
    if refusal is not None:
        return ChatResponse(
            answer="",
            citations=[],
            invalid_references=[],
            citation_note=None,
            refusal=Refusal(code=refusal.code, message=refusal.message),
            context=info,
            model=model,
            usage=None,
            finish_reason=None,
        )

    messages = build_messages(question, context.facts, context.passages)
    slots: ChatSlots = request.app.state.ai_slots
    if not slots.try_acquire():
        raise AppError("ai_busy", "Another question is still running; try again shortly.", 409)
    try:
        reply = await run_upstream(
            request, _client(request).chat(key, model, messages, MAX_COMPLETION_TOKENS)
        )
    except Cancelled:
        return Response(status_code=499)
    except AiError as error:
        raise _as_app_error(error) from None
    finally:
        slots.release()  # every path frees the slot: success, error, cancel

    checked = validate(reply.content, context.facts, context.passages)
    return ChatResponse(
        answer=reply.content,
        citations=[Citation(**chip.__dict__) for chip in checked.citations],
        invalid_references=checked.invalid_references,
        citation_note=checked.note,
        refusal=None,
        context=info,
        model=reply.model or model,
        usage=Usage(**reply.usage) if reply.usage else None,
        finish_reason=reply.finish_reason,
    )
