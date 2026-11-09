"""Response shapes of the AI analyst (M5, milestones/architecture.md "API"). Never the key."""

from __future__ import annotations

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel

NOTICE = "Source links are checked; the claims themselves may still be wrong."


class ModelEntry(BaseModel):
    id: str
    name: str
    context_length: int | None
    prompt_usd_per_million: str | None
    completion_usd_per_million: str | None
    expiration_date: date | None


class ModelsResponse(BaseModel):
    models: list[ModelEntry]
    fetched_at: datetime


class ConnectionTestResponse(BaseModel):
    ok: bool
    label: str | None
    limit_remaining_usd: float | None
    message: str


class ContextInfo(BaseModel):
    line: str
    facts: int
    passages: int
    chars: int


class Citation(BaseModel):
    source_id: str
    valid: bool
    kind: Literal["fact", "passage"]
    label: str
    period: str
    date: date | None
    link: str


class Refusal(BaseModel):
    code: str
    message: str


class Usage(BaseModel):
    prompt_tokens: int | None
    completion_tokens: int | None
    cost: float | None


class ChatResponse(BaseModel):
    answer: str
    citations: list[Citation]
    invalid_references: list[str]
    citation_note: str | None
    refusal: Refusal | None
    context: ContextInfo
    model: str
    usage: Usage | None
    finish_reason: str | None
    notice: str = NOTICE
