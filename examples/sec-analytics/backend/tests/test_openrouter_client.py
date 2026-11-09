"""OpenRouter client (M5-AC7): parsing, error mapping and no retries. OpenRouter mocked with respx.

Responses use the documented shapes (docs/research/openrouter.md) and are SYNTHETIC. The key is the
clearly fake `test-key-not-real-0000`. No test reaches the network.
"""

import json
from pathlib import Path

import httpx
import pytest
import respx

from app.clients.openrouter import (
    BASE_URL,
    AiError,
    OpenRouterClient,
)

KEY = "test-key-not-real-0000"
DATA = Path(__file__).parent / "synthetic" / "openrouter"
MODELS = json.loads((DATA / "models.json").read_text("utf-8"))
KEY_INFO = json.loads((DATA / "key.json").read_text("utf-8"))
CHAT_OK = json.loads((DATA / "chat_ok.json").read_text("utf-8"))
MESSAGES = [{"role": "system", "content": "s"}, {"role": "user", "content": "u"}]
pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
def router():
    with respx.mock(assert_all_called=False, assert_all_mocked=True) as mock:
        yield mock


@pytest.fixture
def client() -> OpenRouterClient:
    return OpenRouterClient()


async def test_models_are_parsed_sorted_and_priced_per_million(router, client) -> None:
    route = router.get(f"{BASE_URL}/models").mock(return_value=httpx.Response(200, json=MODELS))
    models = await client.list_models(KEY)
    assert [m.id for m in models] == [
        "example/alpha-free:free",
        "example/no-pricing",
        "example/zeta-model",
    ]
    zeta = models[2]
    assert (zeta.prompt_usd_per_million, zeta.completion_usd_per_million) == ("2.5", "10")
    assert zeta.context_length == 128000 and zeta.expiration_date is None
    free = models[0]
    assert (free.prompt_usd_per_million, free.completion_usd_per_million) == ("0", "0")
    assert free.expiration_date.isoformat() == "2026-12-31"
    assert models[1].prompt_usd_per_million is None and models[1].context_length is None
    assert route.calls.last.request.headers["Authorization"] == f"Bearer {KEY}"


async def test_key_info_gives_label_and_remaining_limit(router, client) -> None:
    router.get(f"{BASE_URL}/key").mock(return_value=httpx.Response(200, json=KEY_INFO))
    info = await client.key_info(KEY)
    assert (info.label, info.limit_remaining_usd) == ("group-7 (invented)", 4.25)


async def test_chat_sends_the_users_model_and_the_output_limit(router, client) -> None:
    route = router.post(f"{BASE_URL}/chat/completions").mock(
        return_value=httpx.Response(200, json=CHAT_OK)
    )
    reply = await client.chat(KEY, "example/zeta-model", MESSAGES, 800)
    sent = json.loads(route.calls.last.request.content)
    assert sent["model"] == "example/zeta-model"
    assert sent["max_completion_tokens"] == 800 and "max_tokens" not in sent
    assert sent["messages"] == MESSAGES
    assert sent["stream"] is False and sent["temperature"] == 0.2
    assert "tools" not in sent and "response_format" not in sent
    headers = route.calls.last.request.headers
    assert headers["Authorization"] == f"Bearer {KEY}"
    assert headers["X-OpenRouter-Title"] == "SEC Analytics (local teaching app)"
    assert KEY not in str(route.calls.last.request.url) and KEY not in sent.__repr__()
    assert reply.content.startswith("Net margin rose")
    assert reply.finish_reason == "stop"
    assert reply.usage == {"prompt_tokens": 5120, "completion_tokens": 42, "cost": 0.0131}


def error_body(code: int, message: str, metadata: dict | None = None) -> dict:
    return {"error": {"code": code, "message": message, "metadata": metadata or {}}}


@pytest.mark.parametrize(
    ("status", "body", "headers", "code", "http", "message"),
    [
        (
            401,
            error_body(401, "No auth credentials found"),
            {},
            "ai_key_invalid",
            401,
            "Key rejected",
        ),
        (
            402,
            error_body(402, "Insufficient credits", {"limit_source": "openrouter_credits"}),
            {},
            "ai_insufficient_credits",
            402,
            "Out of credits",
        ),
        (
            403,
            error_body(403, "Key limit exceeded", {"limit_source": "openrouter_key_limit"}),
            {},
            "ai_insufficient_credits",
            402,
            "Out of credits",
        ),
        (
            404,
            error_body(404, "Model not found"),
            {},
            "ai_model_not_found",
            404,
            "Model not available; choose another",
        ),
        (
            429,
            error_body(429, "Rate limited"),
            {"Retry-After": "12"},
            "ai_rate_limited",
            429,
            "Rate limited; try again later",
        ),
        (
            408,
            error_body(408, "Timeout"),
            {},
            "ai_timeout",
            504,
            "The AI did not answer within 60 s",
        ),
        (
            502,
            error_body(502, "Provider down"),
            {},
            "ai_unavailable",
            502,
            "The AI provider is unavailable; try again later",
        ),
        (
            503,
            error_body(503, "No provider"),
            {},
            "ai_unavailable",
            502,
            "The AI provider is unavailable; try again later",
        ),
    ],
)
async def test_m5_ac7_errors_map_to_plain_messages_with_exactly_one_call(
    router, client, status, body, headers, code, http, message
) -> None:
    route = router.post(f"{BASE_URL}/chat/completions").mock(
        return_value=httpx.Response(status, json=body, headers=headers)
    )
    with pytest.raises(AiError) as caught:
        await client.chat(KEY, "example/zeta-model", MESSAGES, 800)
    assert (caught.value.code, caught.value.status, caught.value.message) == (code, http, message)
    assert route.call_count == 1  # never retried
    if status == 429:
        assert caught.value.details == {"retry_after": 12}


async def test_other_403_is_forbidden_with_the_providers_reason(router, client) -> None:
    body = error_body(403, "Flagged", {"reasons": ["self-harm"], "provider_name": "X"})
    router.post(f"{BASE_URL}/chat/completions").mock(return_value=httpx.Response(403, json=body))
    with pytest.raises(AiError) as caught:
        await client.chat(KEY, "m/x", MESSAGES, 800)
    assert caught.value.code == "ai_forbidden" and caught.value.status == 403
    assert caught.value.message == "The AI provider refused the request (self-harm)"


async def test_timeout_is_mapped_and_not_retried(router, client) -> None:
    route = router.post(f"{BASE_URL}/chat/completions").mock(side_effect=httpx.ReadTimeout("slow"))
    with pytest.raises(AiError) as caught:
        await client.chat(KEY, "m/x", MESSAGES, 800)
    assert (caught.value.code, caught.value.status) == ("ai_timeout", 504)
    assert route.call_count == 1


async def test_200_with_error_and_no_choices_is_unavailable_or_mapped(router, client) -> None:
    route = router.post(f"{BASE_URL}/chat/completions").mock(
        return_value=httpx.Response(200, json=error_body(502, "Upstream error"))
    )
    with pytest.raises(AiError) as caught:
        await client.chat(KEY, "m/x", MESSAGES, 800)
    assert caught.value.code == "ai_unavailable"
    route.mock(return_value=httpx.Response(200, json=error_body(429, "Rate limited")))
    with pytest.raises(AiError) as caught:
        await client.chat(KEY, "m/x", MESSAGES, 800)
    assert caught.value.code == "ai_rate_limited"


async def test_empty_content_is_unavailable(router, client) -> None:
    empty = {**CHAT_OK, "choices": [{"finish_reason": "stop", "message": {"content": ""}}]}
    router.post(f"{BASE_URL}/chat/completions").mock(return_value=httpx.Response(200, json=empty))
    with pytest.raises(AiError) as caught:
        await client.chat(KEY, "m/x", MESSAGES, 800)
    assert caught.value.code == "ai_unavailable"


async def test_length_finish_keeps_the_partial_answer(router, client) -> None:
    cut = {
        **CHAT_OK,
        "choices": [{"finish_reason": "length", "message": {"content": "Net margin rose because"}}],
    }
    router.post(f"{BASE_URL}/chat/completions").mock(return_value=httpx.Response(200, json=cut))
    reply = await client.chat(KEY, "m/x", MESSAGES, 800)
    assert (reply.content, reply.finish_reason) == ("Net margin rose because", "length")


async def test_a_key_error_never_contains_the_key(router, client) -> None:
    router.get(f"{BASE_URL}/key").mock(
        return_value=httpx.Response(401, json=error_body(401, f"Bad key {KEY}"))
    )
    with pytest.raises(AiError) as caught:
        await client.key_info(KEY)
    assert KEY not in str(caught.value) and KEY not in repr(caught.value.details)


# ------------------------------------------------------------------ security review 2026-11-09


@pytest.mark.parametrize(
    ("status", "body"),
    [
        (403, {"error": {"metadata": "x"}}),
        (200, {"error": "boom"}),
        (200, {"choices": ["x"]}),
        (200, {"choices": [{"message": "hi"}]}),
        (200, {"choices": [{"message": {"content": 42}}]}),
        (200, ["not", "an", "object"]),
    ],
)
async def test_malformed_replies_are_unavailable_not_a_crash(router, client, status, body) -> None:
    router.post(f"{BASE_URL}/chat/completions").mock(return_value=httpx.Response(status, json=body))
    with pytest.raises(AiError) as caught:
        await client.chat(KEY, "m/x", MESSAGES, 800)
    assert caught.value.code in {"ai_unavailable", "ai_forbidden"}


async def test_retry_after_is_kept_only_as_a_small_number(router, client) -> None:
    for header, expected in (("12", {"retry_after": 12}), ("x" * 5000, None), ("99999", None)):
        router.post(f"{BASE_URL}/chat/completions").mock(
            return_value=httpx.Response(429, json={}, headers={"Retry-After": header})
        )
        with pytest.raises(AiError) as caught:
            await client.chat(KEY, "m/x", MESSAGES, 800)
        assert caught.value.details == expected
