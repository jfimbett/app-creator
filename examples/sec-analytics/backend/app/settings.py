"""Backend settings, read from the environment and validated once at startup.

Settings (names documented in the root .env.example; tests need none of them):

- DATA_MODE: "fixtures" (recorded SEC data only, offline) or "live" (the Demo/Live selector is
  offered; live data is still fetched only when a request asks for it).
- FIXTURES_DIR: folder with the recorded fixtures. Empty or unset means
  examples/sec-analytics/fixtures. A relative path is taken from the repository root.
- SEC_USER_AGENT: a descriptive name plus the person's own contact email. Needed for live mode.
  The value is held as a secret: it is never logged, echoed or sent to the browser.
- SEC_CACHE_DIR: disk cache for SEC responses. Empty or unset means backend/.cache/sec.
- SEC_MAX_REQUESTS_PER_SECOND: default 1; values above 5 are refused.
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, SecretStr, ValidationError

from app.clients.sec import SecContactNotConfigured, validate_user_agent

REPO_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_FIXTURES_DIR = Path(__file__).resolve().parents[2] / "fixtures"
DEFAULT_CACHE_DIR = Path(__file__).resolve().parents[1] / ".cache" / "sec"
ALLOWED_DATA_MODES = ("fixtures", "live")
MAX_REQUESTS_PER_SECOND_LIMIT = 5.0


class SettingsError(RuntimeError):
    """A setting is invalid; the message names the setting and what to do."""


class Settings(BaseModel):
    """Validated settings. Construct directly in tests; use `load_settings` in the app."""

    model_config = ConfigDict(frozen=True)

    data_mode: Literal["fixtures", "live"] = "fixtures"
    fixtures_dir: Path = DEFAULT_FIXTURES_DIR
    sec_user_agent: SecretStr | None = None
    sec_cache_dir: Path = DEFAULT_CACHE_DIR
    sec_max_requests_per_second: float = 1.0

    @property
    def live_available(self) -> bool:
        """True when this run of the app offers live mode at all."""
        return self.data_mode == "live"

    @property
    def live_configured(self) -> bool:
        """True when a well-formed SEC_USER_AGENT is present (the value is never exposed)."""
        raw = self.sec_user_agent.get_secret_value() if self.sec_user_agent else None
        try:
            validate_user_agent(raw)
        except SecContactNotConfigured:
            return False
        return True


def _resolve_dir(raw: str | None, default: Path) -> Path:
    """Empty means the default folder; a relative path is taken from the repository root."""
    if raw is None or not raw.strip():
        return default
    path = Path(raw.strip())
    return path if path.is_absolute() else (REPO_ROOT / path).resolve()


def _max_rate(raw: str | None) -> float:
    """Parse SEC_MAX_REQUESTS_PER_SECOND; the fair-access limit is deliberately conservative."""
    if raw is None or not raw.strip():
        return 1.0
    try:
        rate = float(raw)
    except ValueError:
        rate = -1.0
    if not 0 < rate <= MAX_REQUESTS_PER_SECOND_LIMIT:
        raise SettingsError(
            "SEC_MAX_REQUESTS_PER_SECOND must be above 0 and at most 5. SEC's limit of 10 per "
            "second is shared by everyone on one public address (see .env.example)."
        )
    return rate


def load_settings(env: Mapping[str, str] | None = None) -> Settings:
    """Read and validate settings from `env` (default: the process environment)."""
    env = os.environ if env is None else env
    mode = env.get("DATA_MODE", "fixtures")
    agent = env.get("SEC_USER_AGENT")
    try:
        return Settings(
            data_mode=mode,
            fixtures_dir=_resolve_dir(env.get("FIXTURES_DIR"), DEFAULT_FIXTURES_DIR),
            sec_user_agent=SecretStr(agent) if agent else None,
            sec_cache_dir=_resolve_dir(env.get("SEC_CACHE_DIR"), DEFAULT_CACHE_DIR),
            sec_max_requests_per_second=_max_rate(env.get("SEC_MAX_REQUESTS_PER_SECOND")),
        )
    except ValidationError:
        allowed = ", ".join(ALLOWED_DATA_MODES)
        raise SettingsError(
            f"DATA_MODE must be one of: {allowed}. "
            "Fix DATA_MODE in your environment or root .env (see .env.example)."
        ) from None
