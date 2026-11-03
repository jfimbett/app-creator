"""FastAPI backend of SEC Analytics.

Every backend route lives under /api so the frontend can call it on the same origin: in development
Next.js forwards /api/* to this server (see frontend/next.config.ts). At M1 the app serves only
recorded fixtures and makes no network request.
"""

from fastapi import FastAPI

from app.api import companies, meta
from app.data.fixtures import FixtureError, FixtureStore
from app.errors import install_error_handlers
from app.settings import Settings, SettingsError, load_settings

APP_NAME = "SEC Analytics"


def create_app(settings: Settings | None = None) -> FastAPI:
    """Build the app: validate settings, load the fixtures, register routes and error handlers.

    Raises `SettingsError` (naming the setting) when DATA_MODE or FIXTURES_DIR is unusable.
    """
    settings = settings or load_settings()
    try:
        store = FixtureStore(settings.fixtures_dir)
    except FixtureError as exc:
        raise SettingsError(f"FIXTURES_DIR: {exc} See .env.example.") from exc

    application = FastAPI(title=APP_NAME)
    application.state.settings = settings
    application.state.store = store
    install_error_handlers(application)

    @application.get("/api/health")
    def health() -> dict[str, str]:
        """Tells the frontend (and the launch scripts) that the backend is up."""
        return {"status": "ok", "app": APP_NAME}

    application.include_router(meta.router)
    application.include_router(companies.router)
    return application


app = create_app()
