"""Backend settings, read from the environment and validated once at startup.

Settings (names documented in the root .env.example; tests need none of them):

- DATA_MODE: where data comes from. Only "fixtures" (recorded SEC data, offline) exists at M1;
  any other value stops the app at startup with a message naming the setting.
- FIXTURES_DIR: folder with the recorded fixtures. Empty or unset means
  examples/sec-analytics/fixtures. A relative path is taken from the repository root.
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, ValidationError

REPO_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_FIXTURES_DIR = Path(__file__).resolve().parents[2] / "fixtures"
ALLOWED_DATA_MODES = ("fixtures",)


class SettingsError(RuntimeError):
    """A setting is invalid; the message names the setting and what to do."""


class Settings(BaseModel):
    """Validated settings. Construct directly in tests; use `load_settings` in the app."""

    model_config = ConfigDict(frozen=True)

    data_mode: Literal["fixtures"] = "fixtures"
    fixtures_dir: Path = DEFAULT_FIXTURES_DIR


def _fixtures_dir(raw: str | None) -> Path:
    """Resolve FIXTURES_DIR: empty means the default folder; relative means from the repo root."""
    if raw is None or not raw.strip():
        return DEFAULT_FIXTURES_DIR
    path = Path(raw.strip())
    return path if path.is_absolute() else (REPO_ROOT / path).resolve()


def load_settings(env: Mapping[str, str] | None = None) -> Settings:
    """Read and validate settings from `env` (default: the process environment)."""
    env = os.environ if env is None else env
    mode = env.get("DATA_MODE", "fixtures")
    try:
        return Settings(data_mode=mode, fixtures_dir=_fixtures_dir(env.get("FIXTURES_DIR")))
    except ValidationError:
        allowed = ", ".join(ALLOWED_DATA_MODES)
        raise SettingsError(
            f"DATA_MODE must be one of: {allowed} (milestone M1 has no live mode). "
            "Fix DATA_MODE in your environment or root .env (see .env.example)."
        ) from None
