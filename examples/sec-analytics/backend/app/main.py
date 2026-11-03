"""FastAPI backend of the walking skeleton.

Every backend route lives under /api so the frontend can call it on the same origin: in development
Next.js forwards /api/* to this server (see frontend/next.config.ts).
"""

from fastapi import FastAPI

APP_NAME = "SEC Analytics"

app = FastAPI(title=APP_NAME)


@app.get("/api/health")
def health() -> dict[str, str]:
    """Tells the frontend (and the launch scripts) that the backend is up."""
    return {"status": "ok", "app": APP_NAME}
