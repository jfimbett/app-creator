"""Comparison of 2–4 companies and its CSV export (M4). Validates, loads and maps only.

Both endpoints build the result with the same function, so the CSV holds exactly the rows the
table shows. In live mode each company costs up to two SEC requests (Company Facts, submissions),
made one after another through the throttled client and cached for 24 hours.
"""

import re
from datetime import date, datetime, timezone
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response

from app.api.companies import _not_found, parse_cik
from app.api.deps import get_data
from app.clients.sec import companyfacts_url
from app.data.source import DataSource, combine_sources
from app.errors import AppError
from app.logic import compare as logic
from app.logic.csv_export import to_csv
from app.logic.statements import build_financials
from app.models.compare import CompareResponse

router = APIRouter(prefix="/api", tags=["compare"])

SourceParam = Annotated[Literal["demo", "live"], Query(description="demo (default) or live")]
YearsParam = Annotated[int, Query(ge=5, le=10, description="Latest 5 to 10 annual periods")]
IndexParam = Annotated[
    Literal["none", "first_common_year"],
    Query(description="none, or Index = 100 at first common fiscal year"),
]
CiksParam = Annotated[str, Query(description="Comma list of 2-4 CIKs")]
MetricsParam = Annotated[str, Query(description="Comma list of 1-6 comparison metrics")]
COUNT_MESSAGE = "Compare 2–4 companies"
DEFAULT_METRICS = ",".join(logic.DEFAULT_METRICS)


def _today() -> date:
    return datetime.now(timezone.utc).date()


def _parse_ciks(raw: str) -> list[str]:
    """2-4 distinct normalized CIKs in the order given; otherwise a 422 with its own code."""
    ciks: list[str] = []
    for part in (p.strip() for p in raw.split(",")):
        if not part:
            continue
        cik = parse_cik(part)
        if cik in ciks:
            raise AppError(
                "duplicate_company", "This company is already in the comparison.", 422,
                {"cik": cik},
            )
        ciks.append(cik)
    if len(ciks) < logic.MIN_COMPANIES:
        raise AppError("too_few_companies", COUNT_MESSAGE, 422, {"count": len(ciks)})
    if len(ciks) > logic.MAX_COMPANIES:
        raise AppError("too_many_companies", COUNT_MESSAGE, 422, {"count": len(ciks)})
    return ciks


def _parse_metrics(raw: str) -> list[str]:
    """1-6 comparison metrics in the order given, without repeats; otherwise a 422."""
    wanted = list(dict.fromkeys(p.strip() for p in raw.split(",") if p.strip()))
    unknown = [m for m in wanted if m not in logic.COMPARE_METRICS]
    if unknown:
        raise AppError(
            "unknown_metric",
            f"Compare from these metrics: {', '.join(logic.COMPARE_METRICS)}.",
            422,
            {"unknown": unknown, "allowed": list(logic.COMPARE_METRICS)},
        )
    if not logic.MIN_METRICS <= len(wanted) <= logic.MAX_METRICS:
        raise AppError(
            "invalid_request", "Choose from 1 to 6 metrics.", 422, {"count": len(wanted)}
        )
    return wanted


def _build(
    data: DataSource, ciks: str, metrics: str, years: int, index: str, source: str
) -> tuple[logic.CompareResult, list]:
    """Validate, load every company in order, and compare. Also returns the sources used."""
    cik_list = _parse_ciks(ciks)
    metric_list = _parse_metrics(metrics)
    companies: list[logic.CompanyInput] = []
    sources = []
    for cik in cik_list:
        facts = data.companyfacts(cik, source)
        if facts.data is None:
            raise _not_found(cik)
        profile = data.submissions(cik, source)
        raw = profile.data or {}
        financials = build_financials(facts.data, companyfacts_url(cik))
        tickers = [t for t in raw.get("tickers") or [] if isinstance(t, str) and t]
        companies.append(logic.CompanyInput(
            cik=cik,
            ticker=tickers[0] if tickers else "",
            name=raw.get("name") or facts.data.get("entityName") or cik,
            currency=financials.currency,
            series=financials.series,
            data_source=facts.source.label,
        ))
        sources.extend([facts.source, profile.source])
    result = logic.compare(companies, metric_list, years, index == "first_common_year")
    return result, sources


@router.get("/compare", response_model=CompareResponse)
def compare(
    data: Annotated[DataSource, Depends(get_data)],
    ciks: CiksParam,
    metrics: MetricsParam = DEFAULT_METRICS,
    years: YearsParam = 10,
    index: IndexParam = "none",
    source: SourceParam = "demo",
) -> CompareResponse:
    """2-4 companies side by side by their own fiscal years, never aligned or converted."""
    result, sources = _build(data, ciks, metrics, years, index, source)
    return CompareResponse(
        companies=result.companies,
        metrics=result.metrics,
        rows=result.rows,
        index_base=result.index_base,
        warnings=result.warnings,
        index_available=result.index_available,
        source=combine_sources(sources),
    )


def _file_name(result: logic.CompareResult, today: date) -> str:
    parts = [re.sub(r"[^A-Za-z0-9.]", "", c.ticker) or c.cik for c in result.companies]
    return f"sec-analytics-compare-{'-'.join(parts)}-{today.isoformat()}.csv"


@router.get("/compare.csv", response_class=Response)
def compare_csv(
    data: Annotated[DataSource, Depends(get_data)],
    ciks: CiksParam,
    metrics: MetricsParam = DEFAULT_METRICS,
    years: YearsParam = 10,
    index: IndexParam = "none",
    source: SourceParam = "demo",
) -> Response:
    """The same comparison as CSV, one line per row in table order (header in logic/csv_export)."""
    result, _ = _build(data, ciks, metrics, years, index, source)
    return Response(
        content=to_csv(result),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{_file_name(result, _today())}"'},
    )
