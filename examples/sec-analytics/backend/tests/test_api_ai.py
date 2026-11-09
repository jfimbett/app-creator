"""M5 API with a mocked OpenRouter (M5-AC3, AC4, AC5, AC6, AC7, E3, E4). Offline.

Answers are SYNTHETIC (tests/synthetic/openrouter); the SEC data is the recorded demo snapshot.
"""

import json
from pathlib import Path

import httpx
import pytest
import respx
from fastapi.testclient import TestClient

from app.clients.openrouter import BASE_URL
from app.logic.retrieval import MAX_CONTEXT_CHARS
from app.main import create_app
from app.settings import Settings

KEY = "test-key-not-real-0000"
HEADERS = {"X-OpenRouter-Key": KEY}
APPLE, MICROSOFT = "0000320193", "0000789019"
APPLE_10K = "0000320193-26-000026"
DATA = Path(__file__).parent / "synthetic" / "openrouter"
CHAT_OK = json.loads((DATA / "chat_ok.json").read_text("utf-8"))
MODELS = json.loads((DATA / "models.json").read_text("utf-8"))
KEY_INFO = json.loads((DATA / "key.json").read_text("utf-8"))
NOTICE = "Source links are checked; the claims themselves may still be wrong."


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(create_app(Settings(data_mode="fixtures")), base_url="http://127.0.0.1")


@pytest.fixture
def upstream():
    with respx.mock(assert_all_called=False, assert_all_mocked=True) as mock:
        yield mock


def ask(client, question="Why did net margin change?", scope=None, model="example/zeta-model"):
    body = {
        "model": model,
        "scope": scope or {"kind": "company", "cik": APPLE},
        "question": question,
        "source": "demo",
    }
    return client.post("/api/ai/chat", json=body, headers=HEADERS)


def reply(content: str, finish_reason: str = "stop") -> httpx.Response:
    choice = {"finish_reason": finish_reason, "message": {"role": "assistant", "content": content}}
    return httpx.Response(200, json={**CHAT_OK, "choices": [choice]})


def test_m5_ac3_models_and_connection_test(client, upstream) -> None:
    upstream.get(f"{BASE_URL}/models").mock(return_value=httpx.Response(200, json=MODELS))
    upstream.get(f"{BASE_URL}/key").mock(return_value=httpx.Response(200, json=KEY_INFO))
    models = client.get("/api/ai/models", headers=HEADERS).json()
    assert [m["id"] for m in models["models"]][2] == "example/zeta-model"
    assert models["models"][2]["prompt_usd_per_million"] == "2.5"
    assert models["fetched_at"]
    test = client.post("/api/ai/test-connection", json={}, headers=HEADERS).json()
    assert test == {
        "ok": True,
        "label": "group-7 (invented)",
        "limit_remaining_usd": 4.25,
        "message": "Connected",
    }


def test_m5_ac4_answer_with_two_valid_chips_and_the_notice(client, upstream) -> None:
    route = upstream.post(f"{BASE_URL}/chat/completions").mock(
        return_value=httpx.Response(200, json=CHAT_OK)
    )
    body = ask(client).json()
    assert body["answer"].startswith("Net margin rose to 27.60%")
    assert [c["source_id"] for c in body["citations"]] == ["F2", "P1"]
    fact, passage = body["citations"]
    assert fact["kind"] == "fact" and fact["valid"] is True
    # F2 is FY2025 revenue; its latest filing is the FY2026 10-K (as a comparative).
    assert "FY2025" in fact["label"] and APPLE_10K in fact["label"]
    assert fact["link"] == f"/companies/{APPLE}"
    assert passage["kind"] == "passage" and APPLE_10K in passage["label"]
    assert passage["link"].startswith(f"/companies/{APPLE}/filings/{APPLE_10K}#block-")
    assert passage["date"] == "2026-11-03"
    assert body["invalid_references"] == [] and body["citation_note"] is None
    assert body["notice"] == NOTICE
    assert body["refusal"] is None
    assert body["usage"] == {"prompt_tokens": 5120, "completion_tokens": 42, "cost": 0.0131}
    assert body["context"]["line"] == "Context: AAPL facts FY2022–FY2026 + 10-K passages"
    # M5-AC5 through the API: limits, model, output cap, the app's own numbers.
    sent = json.loads(route.calls.last.request.content)
    assert sent["model"] == "example/zeta-model" and sent["max_completion_tokens"] == 800
    assert body["context"]["facts"] <= 60 and body["context"]["passages"] <= 8
    assert body["context"]["chars"] <= MAX_CONTEXT_CHARS
    user = sent["messages"][1]["content"]
    assert "[F1] AAPL · Revenue · 478,834,000,000 USD · FY2026" in user  # FX1
    assert "27.60%" in user  # FX5, as computed by the app


def test_m5_e2_invalid_references_are_listed(client, upstream) -> None:
    upstream.post(f"{BASE_URL}/chat/completions").mock(
        return_value=reply("Margin [F2]. Other [F99] and [P42].")
    )
    body = ask(client).json()
    assert [c["source_id"] for c in body["citations"]] == ["F2"]
    assert body["invalid_references"] == ["F99", "P42"]


def test_an_answer_citing_nothing_says_so(client, upstream) -> None:
    upstream.post(f"{BASE_URL}/chat/completions").mock(return_value=reply("Margins went up."))
    body = ask(client).json()
    assert body["citations"] == [] and body["citation_note"] == "No valid sources cited"


def test_m5_ac6_context_lines_for_each_scope(client, upstream) -> None:
    upstream.post(f"{BASE_URL}/chat/completions").mock(
        return_value=httpx.Response(200, json=CHAT_OK)
    )
    filing = ask(client, scope={"kind": "filing", "cik": APPLE, "accession": APPLE_10K}).json()
    assert filing["context"]["line"] == f"Context: AAPL 10-K {APPLE_10K} passages + AAPL facts"
    comparison = ask(
        client,
        question="How do margins compare?",
        scope={
            "kind": "comparison",
            "ciks": [APPLE, MICROSOFT],
            "metrics": ["revenue", "net_margin"],
        },
    ).json()
    assert comparison["context"]["line"] == "Context: AAPL, MSFT facts for revenue, net margin"
    assert comparison["context"]["passages"] == 0
    preview = client.post(
        "/api/ai/context", json={"scope": {"kind": "company", "cik": APPLE}, "source": "demo"}
    ).json()
    assert preview["line"] == "Context: AAPL facts FY2022–FY2026 + 10-K passages"
    assert preview["facts"] > 0


def test_context_preview_needs_no_key_and_calls_no_model(client, upstream) -> None:
    response = client.post(
        "/api/ai/context",
        json={"scope": {"kind": "filing", "cik": APPLE, "accession": APPLE_10K}, "source": "demo"},
    )
    assert response.status_code == 200
    assert upstream.calls.call_count == 0


@pytest.mark.parametrize(
    "question", ["What will Apple's share price be next year?", "Should I buy MSFT?"]
)
def test_m5_e3_price_and_advice_questions_never_reach_the_model(client, upstream, question) -> None:
    body = ask(client, question=question).json()
    assert body["refusal"]["code"] == "out_of_scope"
    assert body["refusal"]["message"].startswith("This analyst only explains the loaded SEC data")
    assert body["answer"] == "" and body["citations"] == []
    assert upstream.calls.call_count == 0


def test_m5_e4_unloaded_company_never_reaches_the_model(client, upstream) -> None:
    body = ask(client, question="How does Apple compare with Microsoft?").json()
    assert body["refusal"] == {
        "code": "company_not_loaded",
        "message": "That company is not loaded; open it first",
    }
    assert upstream.calls.call_count == 0


@pytest.mark.parametrize(
    ("status", "code", "message"),
    [
        (401, "ai_key_invalid", "Key rejected"),
        (402, "ai_insufficient_credits", "Out of credits"),
        (404, "ai_model_not_found", "Model not available; choose another"),
        (429, "ai_rate_limited", "Rate limited; try again later"),
    ],
)
def test_m5_ac7_upstream_errors_reach_the_screen_as_plain_messages(
    client, upstream, status, code, message
) -> None:
    route = upstream.post(f"{BASE_URL}/chat/completions").mock(
        return_value=httpx.Response(status, json={"error": {"code": status, "message": "x"}})
    )
    response = ask(client)
    assert response.status_code == status
    assert response.json()["error"]["code"] == code
    assert response.json()["error"]["message"] == message
    assert route.call_count == 1


def test_m5_ac7_timeout_is_504(client, upstream) -> None:
    route = upstream.post(f"{BASE_URL}/chat/completions").mock(
        side_effect=httpx.ReadTimeout("slow")
    )
    response = ask(client)
    assert response.status_code == 504
    assert response.json()["error"]["message"] == "The AI did not answer within 60 s"
    assert route.call_count == 1


def test_length_finish_keeps_the_partial_answer(client, upstream) -> None:
    upstream.post(f"{BASE_URL}/chat/completions").mock(
        return_value=reply("Net margin rose because [F2]", "length")
    )
    body = ask(client).json()
    assert body["finish_reason"] == "length"
    assert body["answer"] == "Net margin rose because [F2]"


def test_scope_data_errors_keep_their_codes(client, upstream) -> None:
    response = ask(client, scope={"kind": "company", "cik": "1045810"})
    assert response.status_code == 404 and response.json()["error"]["code"] == "company_not_found"
    assert upstream.calls.call_count == 0


def test_missing_context_is_refused_without_calling_the_model(
    client, upstream, monkeypatch
) -> None:
    from app.api import ai as ai_api
    from app.logic.retrieval import Context

    monkeypatch.setattr(ai_api.retrieval, "build_context", lambda *a, **k: Context((), (), 0))
    body = ask(client).json()
    assert body["refusal"] == {
        "code": "missing_context",
        "message": "Not enough loaded data to answer this question",
    }
    assert upstream.calls.call_count == 0
