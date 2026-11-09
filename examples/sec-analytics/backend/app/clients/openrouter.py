"""The only code that calls OpenRouter (M5, milestones/architecture.md "OpenRouter boundary").

- The base URL is a constant, not a setting, so this can never be pointed elsewhere (not a proxy).
- The key arrives per call from the person's browser and is used for that one request
  (`Authorization: Bearer`). It is never stored on this object, logged, or put in an error.
- No automatic retries: a retry could spend the person's credits twice.
- 60 s timeout. Errors are mapped by HTTP status and `error.metadata`, never by message text,
  and the body is checked for `error` even on a 200 (docs/research/openrouter.md §5, §8).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Any

import httpx

BASE_URL = "https://openrouter.ai/api/v1"
TIMEOUT_SECONDS = 60.0
TEMPERATURE = 0.2
ATTRIBUTION = {
    "HTTP-Referer": "http://127.0.0.1",
    "X-OpenRouter-Title": "SEC Analytics (local teaching app)",
}

KEY_REJECTED = "Key rejected"
OUT_OF_CREDITS = "Out of credits"
MODEL_NOT_AVAILABLE = "Model not available; choose another"
RATE_LIMITED = "Rate limited; try again later"
TIMED_OUT = "The AI did not answer within 60 s"
UNAVAILABLE = "The AI provider is unavailable; try again later"
EMPTY_ANSWER = "The AI returned an empty answer; try again or choose another model"
CREDIT_SOURCES = {"openrouter_key_limit", "openrouter_credits"}


class AiError(Exception):
    """A failed AI call, ready for the error envelope. Never carries the key."""

    def __init__(
        self, code: str, message: str, status: int, details: dict[str, Any] | None = None
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status = status
        self.details = details


@dataclass(frozen=True)
class ModelInfo:
    id: str
    name: str
    context_length: int | None
    prompt_usd_per_million: str | None
    completion_usd_per_million: str | None
    expiration_date: date | None


@dataclass(frozen=True)
class KeyInfo:
    label: str | None
    limit_remaining_usd: float | None


@dataclass(frozen=True)
class ChatReply:
    content: str
    finish_reason: str | None
    model: str | None
    usage: dict[str, Any] | None


def _per_million(value: Any) -> str | None:
    """OpenRouter's USD-per-token string as USD per million tokens ("0.0000025" → "2.5")."""
    if not isinstance(value, str | int | float):
        return None
    try:
        amount = Decimal(str(value)) * 1_000_000
    except InvalidOperation:
        return None
    text = format(amount.normalize(), "f")
    return text if text != "-0" else "0"


def _day(value: Any) -> date | None:
    try:
        return date.fromisoformat(str(value)[:10]) if value else None
    except ValueError:
        return None


def _map_error(status: int, body: Any, headers: httpx.Headers | None = None) -> AiError:
    """An OpenRouter failure as one of the app's error codes and plain messages."""
    error = body.get("error") if isinstance(body, dict) else None
    metadata = (error or {}).get("metadata") or {} if isinstance(error, dict) else {}
    if status == 401:
        return AiError("ai_key_invalid", KEY_REJECTED, 401)
    if status == 402 or (status == 403 and metadata.get("limit_source") in CREDIT_SOURCES):
        return AiError("ai_insufficient_credits", OUT_OF_CREDITS, 402)
    if status == 403:
        reasons = metadata.get("reasons")
        reason = ", ".join(str(r)[:60] for r in reasons[:3]) if isinstance(reasons, list) else ""
        message = "The AI provider refused the request" + (f" ({reason})" if reason else "")
        return AiError("ai_forbidden", message, 403)
    if status == 404:
        return AiError("ai_model_not_found", MODEL_NOT_AVAILABLE, 404)
    if status == 408:
        return AiError("ai_timeout", TIMED_OUT, 504)
    if status == 429:
        retry_after = headers.get("Retry-After") if headers is not None else None
        return AiError(
            "ai_rate_limited",
            RATE_LIMITED,
            429,
            {"retry_after": retry_after} if retry_after else None,
        )
    return AiError("ai_unavailable", UNAVAILABLE, 502)


class OpenRouterClient:
    """Calls OpenRouter with a key given per call. Holds no key and no connection between calls."""

    def __init__(
        self, transport: httpx.AsyncBaseTransport | None = None, timeout: float = TIMEOUT_SECONDS
    ) -> None:
        self._transport = transport
        self._timeout = timeout

    async def _request(
        self, method: str, path: str, key: str, payload: dict[str, Any] | None = None
    ) -> Any:
        headers = {"Authorization": f"Bearer {key}", "Accept": "application/json", **ATTRIBUTION}
        try:
            async with httpx.AsyncClient(
                base_url=BASE_URL,
                timeout=self._timeout,
                transport=self._transport,
                follow_redirects=False,
            ) as http:
                response = await http.request(method, path, headers=headers, json=payload)
        except httpx.TimeoutException:
            raise AiError("ai_timeout", TIMED_OUT, 504) from None
        except httpx.HTTPError:
            raise AiError("ai_unavailable", UNAVAILABLE, 502) from None
        try:
            body = response.json()
        except ValueError:
            body = None
        if response.status_code != 200:
            raise _map_error(response.status_code, body, response.headers)
        if not isinstance(body, dict):
            raise AiError("ai_unavailable", UNAVAILABLE, 502)
        return body

    async def list_models(self, key: str) -> list[ModelInfo]:
        body = await self._request("GET", "/models", key)
        models = []
        for item in body.get("data") or []:
            if not isinstance(item, dict) or not isinstance(item.get("id"), str):
                continue
            pricing = item.get("pricing") if isinstance(item.get("pricing"), dict) else {}
            context = item.get("context_length")
            models.append(
                ModelInfo(
                    id=item["id"],
                    name=str(item.get("name") or item["id"]),
                    context_length=context if isinstance(context, int) else None,
                    prompt_usd_per_million=_per_million(pricing.get("prompt")),
                    completion_usd_per_million=_per_million(pricing.get("completion")),
                    expiration_date=_day(item.get("expiration_date")),
                )
            )
        return sorted(models, key=lambda m: m.id)

    async def key_info(self, key: str) -> KeyInfo:
        data = (await self._request("GET", "/key", key)).get("data") or {}
        remaining = data.get("limit_remaining")
        label = data.get("label")
        return KeyInfo(
            label=label if isinstance(label, str) else None,
            limit_remaining_usd=float(remaining) if isinstance(remaining, int | float) else None,
        )

    async def chat(
        self, key: str, model: str, messages: list[dict[str, str]], max_completion_tokens: int
    ) -> ChatReply:
        payload = {
            "model": model,
            "messages": messages,
            "max_completion_tokens": max_completion_tokens,
            "temperature": TEMPERATURE,
            "stream": False,
        }
        body = await self._request("POST", "/chat/completions", key, payload)
        choices = body.get("choices")
        if body.get("error") and not choices:
            code = (body.get("error") or {}).get("code")
            raise _map_error(code if isinstance(code, int) else 502, body)
        choice = choices[0] if isinstance(choices, list) and choices else {}
        if isinstance(choice.get("error"), dict):
            code = choice["error"].get("code")
            raise _map_error(code if isinstance(code, int) else 502, {"error": choice["error"]})
        content = ((choice.get("message") or {}).get("content") or "").strip()
        if not content:
            raise AiError("ai_unavailable", EMPTY_ANSWER, 502)
        usage = body.get("usage") if isinstance(body.get("usage"), dict) else None
        return ChatReply(
            content=content,
            finish_reason=choice.get("finish_reason"),
            model=body.get("model") if isinstance(body.get("model"), str) else None,
            usage=(
                {
                    "prompt_tokens": usage.get("prompt_tokens"),
                    "completion_tokens": usage.get("completion_tokens"),
                    "cost": usage.get("cost"),
                }
                if usage
                else None
            ),
        )
