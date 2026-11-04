"""GET /api/meta: what data the app serves (mode, snapshot date, demo universe)."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import get_settings, get_store
from app.data.fixtures import FixtureStore
from app.models.companies import DemoCompany, MetaResponse
from app.settings import Settings

router = APIRouter(prefix="/api", tags=["meta"])


@router.get("/meta", response_model=MetaResponse)
def meta(
    store: Annotated[FixtureStore, Depends(get_store)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> MetaResponse:
    """Data mode, whether live is offered and configured, and the demo universe."""
    universe = [
        DemoCompany(cik=c.cik, ticker=c.primary_ticker, name=c.name) for c in store.universe()
    ]
    return MetaResponse(
        data_mode=settings.data_mode,
        live_available=settings.live_available,
        live_configured=settings.live_configured,
        snapshot_date=store.snapshot_date,
        demo_universe=universe,
    )
