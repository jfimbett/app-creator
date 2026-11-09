"""AI boundary security (M5-E5, M5-E6, M5-AC8 backend part). OpenRouter mocked with respx.

The key is the clearly fake `test-key-not-real-0000`. No test reaches the network.
"""

import asyncio
import json
import logging
import threading
from pathlib import Path

import httpx
import pytest
import respx
from fastapi.testclient import TestClient

from app.api import ai as ai_api
from app.clients.openrouter import BASE_URL
from app.logging_setup import RedactingFilter
from app.main import create_app
from app.settings import Settings

KEY = "test-key-not-real-0000"
HEADERS = {"X-OpenRouter-Key": KEY}
APPLE = "0000320193"
DATA = Path(__file__).parent / "synthetic" / "openrouter"
CHAT_OK = json.loads((DATA / "chat_ok.json").read_text("utf-8"))
QUESTION = {
    "model": "example/zeta-model",
    "scope": {"kind": "company", "cik": APPLE},
    "question": "Why did net margin change?",
    "source": "demo",
}


@pytest.fixture
def app_client():
    return TestClient(create_app(Settings(data_mode="fixtures")), base_url="http://127.0.0.1")


@pytest.fixture
def upstream():
    with respx.mock(assert_all_called=False, assert_all_mocked=True) as mock:
        yield mock


def error(response, status: int, code: str) -> dict:
    assert response.status_code == status, response.text
    body = response.json()["error"]
    assert body["code"] == code
    return body


# ------------------------------------------------------------------ M5-E5 key never leaks


@pytest.mark.parametrize("status", [200, 401, 402, 404, 429, 502])
def test_m5_e5_the_key_is_in_no_log_line_error_or_response(
    app_client, upstream, caplog, status
) -> None:
    caplog.set_level(logging.DEBUG)
    body = CHAT_OK if status == 200 else {"error": {"code": status, "message": f"bad {KEY}"}}
    upstream.post(f"{BASE_URL}/chat/completions").mock(
        return_value=httpx.Response(status, json=body)
    )
    upstream.get(f"{BASE_URL}/key").mock(return_value=httpx.Response(status, json=body))
    upstream.get(f"{BASE_URL}/models").mock(return_value=httpx.Response(status, json=body))
    responses = [
        app_client.post("/api/ai/chat", json=QUESTION, headers=HEADERS),
        app_client.post("/api/ai/test-connection", json={}, headers=HEADERS),
        app_client.get("/api/ai/models", headers=HEADERS),
    ]
    for response in responses:
        assert KEY not in response.text
        assert KEY not in str(response.headers)
    assert KEY not in caplog.text
    sent = upstream.calls.last.request
    assert KEY not in str(sent.url)


def test_the_redacting_filter_hides_keys_and_auth_headers() -> None:
    record = logging.LogRecord(
        "x",
        logging.INFO,
        __file__,
        1,
        "headers %s and %s",
        ("Authorization: Bearer sk-or-v1-abcdef123456", "X-OpenRouter-Key: sk-or-v1-zzz"),
        None,
    )
    assert RedactingFilter().filter(record)
    text = record.getMessage()
    assert "sk-or-v1" not in text and "abcdef" not in text and "[REDACTED]" in text


# ------------------------------------------------------------------ M5-E6 limits and origin


def test_m5_e6_a_70_kb_body_is_413(app_client, upstream) -> None:
    big = {**QUESTION, "question": "x" * 70_000}
    error(app_client.post("/api/ai/chat", json=big, headers=HEADERS), 413, "request_too_large")
    assert upstream.calls.call_count == 0


def test_foreign_origins_are_refused_and_local_ones_accepted(app_client, upstream) -> None:
    upstream.get(f"{BASE_URL}/models").mock(return_value=httpx.Response(200, json={"data": []}))
    for headers in (
        {"Origin": "http://evil.example"},
        {"Origin": "http://127.0.0.1:3123", "Sec-Fetch-Site": "cross-site"},
        {"Origin": "https://127.0.0.1:3000"},
        {"Origin": "http://127.0.0.1.evil.example:3000"},
    ):
        response = app_client.get("/api/ai/models", headers={**HEADERS, **headers})
        error(response, 403, "forbidden_origin")
    assert upstream.calls.call_count == 0
    for headers in (
        {"Origin": "http://127.0.0.1:3123"},
        {"Origin": "http://localhost:3000"},
        {"Sec-Fetch-Site": "same-origin"},
        {"Sec-Fetch-Site": "none"},
        {},
    ):
        assert app_client.get("/api/ai/models", headers={**HEADERS, **headers}).status_code == 200


def test_no_key_and_bad_requests(app_client, upstream) -> None:
    error(app_client.get("/api/ai/models"), 400, "ai_key_missing")
    error(app_client.post("/api/ai/chat", json=QUESTION), 400, "ai_key_missing")
    error(
        app_client.post("/api/ai/chat", json={**QUESTION, "model": ""}, headers=HEADERS),
        422,
        "invalid_model",
    )
    no_model = {k: v for k, v in QUESTION.items() if k != "model"}
    error(app_client.post("/api/ai/chat", json=no_model, headers=HEADERS), 422, "invalid_model")
    error(
        app_client.post("/api/ai/chat", json={**QUESTION, "model": "bad model!"}, headers=HEADERS),
        422,
        "invalid_model",
    )
    for question in ("", "   ", "x" * 2001):
        error(
            app_client.post(
                "/api/ai/chat", json={**QUESTION, "question": question}, headers=HEADERS
            ),
            422,
            "invalid_question",
        )
    for scope in (
        {"kind": "planet"},
        {"kind": "company"},
        {"kind": "filing", "cik": APPLE},
        {"kind": "comparison", "ciks": [APPLE], "metrics": ["revenue"]},
        {"kind": "comparison", "ciks": [APPLE, "789019"], "metrics": ["roe"]},
    ):
        error(
            app_client.post("/api/ai/chat", json={**QUESTION, "scope": scope}, headers=HEADERS),
            422,
            "invalid_scope",
        )
    assert upstream.calls.call_count == 0


# ------------------------------------------------------------------ M5-AC8 slots


def test_m5_e6_a_third_concurrent_chat_is_busy_and_slots_are_freed(upstream) -> None:
    release = threading.Event()
    started = threading.Semaphore(0)

    async def slow(_request):
        started.release()
        while not release.is_set():
            await asyncio.sleep(0.02)
        return httpx.Response(200, json=CHAT_OK)

    upstream.post(f"{BASE_URL}/chat/completions").mock(side_effect=slow)
    app = create_app(Settings(data_mode="fixtures"))
    client = TestClient(app, base_url="http://127.0.0.1")
    results: list[int] = []

    def ask() -> None:
        results.append(client.post("/api/ai/chat", json=QUESTION, headers=HEADERS).status_code)

    threads = [threading.Thread(target=ask) for _ in range(2)]
    for thread in threads:
        thread.start()
    for _ in range(2):
        assert started.acquire(timeout=20)
    error(client.post("/api/ai/chat", json=QUESTION, headers=HEADERS), 409, "ai_busy")
    release.set()
    for thread in threads:
        thread.join(timeout=20)
    assert results == [200, 200]
    assert app.state.ai_slots.in_use == 0
    assert client.post("/api/ai/chat", json=QUESTION, headers=HEADERS).status_code == 200


def test_a_failed_upstream_call_frees_its_slot(app_client, upstream) -> None:
    upstream.post(f"{BASE_URL}/chat/completions").mock(side_effect=httpx.ReadTimeout("slow"))
    error(app_client.post("/api/ai/chat", json=QUESTION, headers=HEADERS), 504, "ai_timeout")
    assert app_client.app.state.ai_slots.in_use == 0


def test_a_disconnect_cancels_the_upstream_task() -> None:
    # Drives the endpoint's waiting loop directly: the client goes away while the model is slow.
    cancelled = asyncio.Event()

    async def slow_chat(*_args, **_kwargs):
        try:
            await asyncio.sleep(30)
        except asyncio.CancelledError:
            cancelled.set()
            raise

    class GoneRequest:
        async def is_disconnected(self) -> bool:
            return True

    async def run() -> None:
        with pytest.raises(ai_api.Cancelled):
            await ai_api.run_upstream(GoneRequest(), slow_chat())
        await asyncio.wait_for(cancelled.wait(), 2)

    asyncio.run(run())


def test_a_cancelled_chat_frees_its_slot(upstream, monkeypatch) -> None:
    async def gone(_request, work):
        work.close()
        raise ai_api.Cancelled()

    monkeypatch.setattr(ai_api, "run_upstream", gone)
    app = create_app(Settings(data_mode="fixtures"))
    client = TestClient(app, base_url="http://127.0.0.1")
    assert client.post("/api/ai/chat", json=QUESTION, headers=HEADERS).status_code == 499
    assert app.state.ai_slots.in_use == 0


# ------------------------------------------------------------------ security review 2026-11-09


def test_a_chunked_body_over_64_kb_is_refused_without_content_length(app_client, upstream) -> None:
    def chunks():
        for _ in range(80):
            yield b"x" * 1024

    response = app_client.post(
        "/api/ai/chat", content=chunks(), headers={**HEADERS, "Content-Type": "application/json"}
    )
    error(response, 413, "request_too_large")


def test_a_foreign_host_is_refused(upstream) -> None:
    # DNS rebinding: a page on another name that resolves to 127.0.0.1 sends its own Host.
    client = TestClient(
        create_app(Settings(data_mode="fixtures")), base_url="http://evil.test:8000"
    )
    error(client.get("/api/ai/models", headers=HEADERS), 403, "forbidden_origin")


def test_tracebacks_are_redacted_too() -> None:
    try:
        raise RuntimeError("upstream said Authorization: Bearer sk-or-v1-secretsecret")
    except RuntimeError:
        import sys

        record = logging.LogRecord("x", logging.ERROR, __file__, 1, "failed", (), sys.exc_info())
    RedactingFilter().filter(record)
    rendered = logging.Formatter().format(record)
    assert "secretsecret" not in rendered and "[REDACTED]" in rendered


def test_out_of_scope_questions_load_no_sec_data(upstream, monkeypatch) -> None:
    app = create_app(Settings(data_mode="fixtures"))
    calls: list[str] = []
    original = app.state.data.companyfacts

    def counting(cik, source):
        calls.append(cik)
        return original(cik, source)

    monkeypatch.setattr(app.state.data, "companyfacts", counting)
    client = TestClient(app, base_url="http://127.0.0.1")
    body = client.post(
        "/api/ai/chat", json={**QUESTION, "question": "Should I buy MSFT?"}, headers=HEADERS
    ).json()
    assert body["refusal"]["code"] == "out_of_scope"
    assert calls == [] and upstream.calls.call_count == 0


def test_context_preview_reads_no_filing_document(monkeypatch) -> None:
    app = create_app(Settings(data_mode="fixtures"))

    def refuse(*_args, **_kwargs):
        raise AssertionError("the preview must not read a filing document")

    monkeypatch.setattr(app.state.data, "parsed_filing", refuse)
    client = TestClient(app, base_url="http://127.0.0.1")
    response = client.post(
        "/api/ai/context", json={"scope": {"kind": "company", "cik": APPLE}, "source": "demo"}
    )
    assert response.status_code == 200
    assert response.json()["line"] == "Context: AAPL facts FY2022–FY2026 + 10-K passages"
