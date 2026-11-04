"""Response shapes of the filing endpoints (milestones/architecture.md "API")."""

from __future__ import annotations

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel

from app.models.common import SourceInfo


class FilingMeta(BaseModel):
    """One row of a company's 10-K/10-Q list. Addresses are None without a primary document."""

    accession: str
    form: str
    is_amendment: bool
    filing_date: date
    report_date: date | None
    primary_document: str | None
    document_url: str | None
    index_url: str
    document_in_snapshot: bool | None = None


class LatestFilings(BaseModel):
    """The most recent ORIGINAL annual and quarterly reports; an amendment never replaces them."""

    annual: FilingMeta | None
    quarterly: FilingMeta | None
    annual_amended_by: FilingMeta | None
    quarterly_amended_by: FilingMeta | None
    label: str


class Coverage(BaseModel):
    """The range of filings shown, and whether it reaches the whole requested window."""

    from_date: date | None
    to_date: date | None
    complete: bool
    note: str | None


class FilingsResponse(BaseModel):
    cik: str
    latest: LatestFilings
    history: list[FilingMeta]
    coverage: Coverage
    source: SourceInfo


class FilingSection(BaseModel):
    id: str
    item: str
    title: str
    block_start: int


class FilingBlock(BaseModel):
    """Plain text only: the browser renders `text` as text, never as HTML."""

    id: int
    section_id: str | None
    kind: Literal["text", "heading", "table_row"]
    text: str


class FilingDocumentResponse(BaseModel):
    meta: FilingMeta
    section_status: Literal["detected", "not_detected"]
    note: str
    sections: list[FilingSection]
    blocks: list[FilingBlock]
    source_link: str
    scope: str
    truncated: bool
    document_retrieved_at: datetime
    amends: FilingMeta | None
    amended_by: FilingMeta | None
    source: SourceInfo
