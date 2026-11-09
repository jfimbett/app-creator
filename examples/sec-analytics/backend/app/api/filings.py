"""A company's filing list and the reader's text. Validates and maps only (architecture.md "API").

The accession must be in that company's own 10-K/10-Q list before anything is fetched. The address
then comes from SEC's own data for that row, never from the request: this is not a URL proxy.
"""

from datetime import date, datetime, timezone
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Path, Query

from app.api.companies import _not_found, parse_cik
from app.api.deps import get_data
from app.data.source import DataSource, FilingList
from app.errors import AppError
from app.logic import filings as logic
from app.logic.archive import is_valid_accession
from app.logic.sanitize import MAX_BLOCKS
from app.models.common import SourceInfo
from app.models.filings import (
    Coverage,
    FilingBlock,
    FilingDocumentResponse,
    FilingSection,
    FilingsResponse,
)

router = APIRouter(prefix="/api/companies", tags=["filings"])
SourceParam = Annotated[Literal["demo", "live"], Query(description="demo (default) or live")]
DataDep = Annotated[DataSource, Depends(get_data)]


def _today() -> date:
    return datetime.now(timezone.utc).date()


def _parse_forms(raw: str) -> set[str]:
    forms = {part.strip() for part in raw.split(",") if part.strip()}
    if not forms or not forms <= set(logic.ALL_FORMS):
        raise AppError(
            "invalid_forms",
            f"Choose forms from {', '.join(logic.ALL_FORMS)}.",
            422,
            {"allowed": list(logic.ALL_FORMS)},
        )
    return forms


def _load(data: DataSource, cik: str, source: str) -> FilingList:
    found = data.filing_list(cik, source, _today())
    if found is None:
        raise _not_found(cik)
    return found


@router.get("/{cik}/filings", response_model=FilingsResponse)
def company_filings(
    cik: str,
    data: DataDep,
    forms: Annotated[str, Query(description="Comma-separated subset of the four forms")] = ",".join(
        logic.ALL_FORMS
    ),
    years: Annotated[int, Query(ge=1, le=logic.MAX_YEARS)] = logic.MAX_YEARS,
    source: SourceParam = "demo",
) -> FilingsResponse:
    """The latest original 10-K and 10-Q, and the filing history of the window, newest first."""
    normalized = parse_cik(cik)
    wanted = _parse_forms(forms)
    found = _load(data, normalized, source)
    reference = found.listed_at.date() if found.listed_at else _today()
    window = logic.in_window(found.rows, logic.window_start(reference, years))
    history = [row for row in window if row.form in wanted]
    label = logic.latest_label(found.source, found.listed_at)
    facts = logic.CoverageFacts(demo=source == "demo", pages_missing=found.pages_missing)
    coverage: Coverage = logic.coverage_of(history, facts)
    return FilingsResponse(
        cik=normalized,
        latest=logic.select_latest(found.rows, label),
        history=history,
        coverage=coverage,
        source=found.source,
    )


def _scope(source: SourceInfo, retrieved_at: datetime, truncated: bool) -> str:
    """Says exactly what the reader shows, and from when."""
    if truncated:
        what = (
            f"Part of the primary document: only its first {MAX_BLOCKS:,} text blocks are shown. "
            "Open the source on sec.gov for the rest"
        )
    else:
        what = "Full primary document, without exhibits"
    if source.mode == "demo":
        when = f"recorded {retrieved_at:%Y-%m-%d}. Not necessarily the latest report on EDGAR"
    elif source.mode == "cached":
        when = f"cached copy retrieved {retrieved_at:%Y-%m-%d %H:%M} UTC"
    else:
        when = f"retrieved live {retrieved_at:%Y-%m-%d %H:%M} UTC"
    return f"{what}; {when}."


@router.get("/{cik}/filings/{accession:path}", response_model=FilingDocumentResponse)
def filing_document(
    cik: str,
    accession: Annotated[str, Path(description="Accession number, 0000320193-26-000026")],
    data: DataDep,
    source: SourceParam = "demo",
) -> FilingDocumentResponse:
    """A filing's primary document as sanitized plain text blocks with detected sections."""
    normalized = parse_cik(cik)
    if not is_valid_accession(accession):
        raise AppError(
            "invalid_accession",
            "An accession number looks like 0000320193-26-000026: 10 digits, 2 digits, 6 digits.",
            422,
        )
    found = _load(data, normalized, source)
    filing = next((row for row in found.rows if row.accession == accession), None)
    if filing is None:
        raise AppError(
            "filing_not_found", "This company has no 10-K or 10-Q with that accession number.", 404
        )
    parsed = data.parsed_filing(normalized, filing, source)
    sections = parsed.sections
    return FilingDocumentResponse(
        meta=filing,
        section_status=sections.status,
        note=sections.note,
        sections=[
            FilingSection(id=s.id, item=s.item, title=s.title, block_start=s.block_start)
            for s in sections.sections
        ],
        blocks=[
            FilingBlock(
                id=index,
                section_id=sections.section_of_block[index],
                kind="heading" if index in sections.heading_blocks else block.kind,
                text=block.text,
            )
            for index, block in enumerate(parsed.document.blocks)
        ],
        source_link=filing.document_url,
        scope=_scope(parsed.source, parsed.retrieved_at, parsed.document.truncated),
        truncated=parsed.document.truncated,
        document_retrieved_at=parsed.retrieved_at,
        amends=logic.amends(filing, found.rows),
        amended_by=logic.amended_by(filing, found.rows),
        source=parsed.source,
    )
