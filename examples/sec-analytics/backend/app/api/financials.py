"""Metric catalog, normalized statement summaries and metric series. Validates and maps only."""

from typing import Annotated, Any, Literal

from fastapi import APIRouter, Depends, Query

from app.api.companies import _not_found, parse_cik
from app.api.deps import get_data
from app.clients.sec import companyfacts_url
from app.data.source import DataSource, combine_sources
from app.errors import AppError
from app.logic.concepts import CATALOG_BY_ID, LABELS, catalog
from app.logic.metrics import PERCENT, RATIO
from app.logic.statements import (
    BALANCE_LINES,
    CASH_FLOW_LINES,
    INCOME_LINES,
    RATIO_LINES,
    Financials,
    build_financials,
)
from app.models.financials import (
    FinancialsResponse,
    Line,
    MetricInfo,
    MetricsCatalog,
    MetricSeries,
    MetricSeriesResponse,
    PeriodInfo,
    Statements,
)

router = APIRouter(prefix="/api", tags=["financials"])

SourceParam = Annotated[Literal["demo", "live"], Query(description="demo (default) or live")]
YearsParam = Annotated[int, Query(ge=5, le=10, description="Latest 5 to 10 annual periods")]
MAX_METRICS = 6


def _text(value: Any) -> str | None:
    return value if isinstance(value, str) and value.strip() else None


def _kind_and_unit(metric_id: str, financials: Financials) -> tuple[str, str]:
    """A line's kind and unit, also when the company has no periods."""
    values = financials.series.get(metric_id) or []
    kind = values[0].kind if values else CATALOG_BY_ID[metric_id]["kind"]
    if metric_id in {"debt_to_equity"}:
        return kind, RATIO
    if CATALOG_BY_ID.get(metric_id, {}).get("unit_kind") == "percent":
        return kind, PERCENT
    return kind, financials.currency or ""


def _line(metric_id: str, financials: Financials) -> Line:
    kind, unit = _kind_and_unit(metric_id, financials)
    return Line(
        metric_id=metric_id,
        label=LABELS[metric_id],
        kind=kind,
        unit=unit,
        values=financials.series.get(metric_id, []),
    )


def _load(cik10: str, data: DataSource, source: str) -> tuple[Financials, Any]:
    """Company Facts for a CIK as all-period financials, plus its SourceInfo."""
    fetched = data.companyfacts(cik10, source)
    if fetched.data is None:
        raise _not_found(cik10)
    return build_financials(fetched.data, companyfacts_url(cik10)), fetched


@router.get("/metrics", response_model=MetricsCatalog)
def metric_catalog() -> MetricsCatalog:
    """Every metric the explorer can show, with its formula or SEC concepts."""
    return MetricsCatalog(metrics=[MetricInfo(**item) for item in catalog()])


@router.get("/companies/{cik}/financials", response_model=FinancialsResponse)
def company_financials(
    cik: str,
    data: Annotated[DataSource, Depends(get_data)],
    years: YearsParam = 10,
    source: SourceParam = "demo",
) -> FinancialsResponse:
    """Normalized annual statement summaries and ratios (not the complete filed statements)."""
    cik10 = parse_cik(cik)
    all_years, facts = _load(cik10, data, source)
    profile = data.submissions(cik10, source)
    shown = all_years.latest(years)
    return FinancialsResponse(
        cik=cik10,
        currency=shown.currency,
        fiscal_year_end=_text((profile.data or {}).get("fiscalYearEnd")),
        periods=[
            PeriodInfo(fiscal_year_label=p.label, start=p.start, end=p.end) for p in shown.periods
        ],
        statements=Statements(
            income=[_line(m, shown) for m in INCOME_LINES],
            balance=[_line(m, shown) for m in BALANCE_LINES],
            cash_flow=[_line(m, shown) for m in CASH_FLOW_LINES],
        ),
        ratios=[_line(m, shown) for m in RATIO_LINES],
        notes=shown.notes,
        source=combine_sources([facts.source, profile.source]),
    )


def _parse_ids(ids: str) -> list[str]:
    """1 to 6 known metric ids, in the order asked, without repeats; otherwise a 422."""
    wanted = list(dict.fromkeys(part.strip() for part in ids.split(",") if part.strip()))
    if not 1 <= len(wanted) <= MAX_METRICS:
        raise AppError(
            "invalid_request", "Choose from 1 to 6 metrics.", 422, {"count": len(wanted)}
        )
    unknown = [metric_id for metric_id in wanted if metric_id not in CATALOG_BY_ID]
    if unknown:
        raise AppError(
            "unknown_metric",
            "Unknown metric. The list is at /api/metrics.",
            422,
            {"unknown": unknown},
        )
    return wanted


@router.get("/companies/{cik}/metrics", response_model=MetricSeriesResponse)
def company_metrics(
    cik: str,
    data: Annotated[DataSource, Depends(get_data)],
    ids: Annotated[str, Query(description="Comma list of 1-6 ids from /api/metrics")],
    years: YearsParam = 10,
    source: SourceParam = "demo",
) -> MetricSeriesResponse:
    """The selected metrics by fiscal year, each with provenance or formula and inputs."""
    wanted = _parse_ids(ids)
    cik10 = parse_cik(cik)
    all_years, facts = _load(cik10, data, source)
    shown = all_years.latest(years)
    series = []
    for metric_id in wanted:
        kind, unit = _kind_and_unit(metric_id, shown)
        series.append(
            MetricSeries(
                metric_id=metric_id,
                label=LABELS[metric_id],
                unit=unit,
                kind=kind,
                formula=CATALOG_BY_ID[metric_id]["formula"],
                points=shown.series.get(metric_id, []),
            )
        )
    return MetricSeriesResponse(cik=cik10, series=series, source=facts.source)
