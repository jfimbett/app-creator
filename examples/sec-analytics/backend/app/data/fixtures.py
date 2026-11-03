"""Read the recorded SEC fixtures and their manifest (examples/sec-analytics/fixtures/).

The manifest says where every file came from. `SourceInfo` labels are built here:
`RECORDED SEC DEMO · snapshot <date>` for authentic data, and `SYNTHETIC TEST DATA · snapshot
<date>` whenever the manifest (or a loaded file) is marked synthetic, whatever label the
manifest claims. Files are read once and kept in memory; nothing here touches the network.
"""

from __future__ import annotations

import json
from datetime import date
from functools import cached_property
from pathlib import Path
from typing import Any

from app.logic.search import UniverseCompany
from app.models.common import SourceInfo
from app.settings import DEFAULT_FIXTURES_DIR

RECORDED_LABEL = "RECORDED SEC DEMO"
SYNTHETIC_LABEL = "SYNTHETIC TEST DATA"
SYNTHETIC_KEY = "_synthetic"


class FixtureError(RuntimeError):
    """The fixtures folder is missing or inconsistent (a startup problem, not a user error)."""


def default_fixtures_dir() -> Path:
    """The folder used when FIXTURES_DIR is not set."""
    return DEFAULT_FIXTURES_DIR


def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise FixtureError(f"Fixture file missing: {path.name}") from None
    except json.JSONDecodeError as exc:
        raise FixtureError(f"Fixture file is not valid JSON: {path.name}") from exc


class FixtureStore:
    """Read-only access to one fixtures folder: manifest, tickers and submissions."""

    def __init__(self, root: Path) -> None:
        self.root = Path(root)
        if not (self.root / "manifest.json").is_file():
            raise FixtureError("No manifest.json in the fixtures folder (check FIXTURES_DIR).")
        self.manifest: dict[str, Any] = _read_json(self.root / "manifest.json")
        self._entries = {entry["path"]: entry for entry in self.manifest.get("files", [])}
        self._tickers = self._load("company_tickers.json")
        self._submissions = {
            entry["cik"]: self._load(entry["path"])
            for entry in self._entries.values()
            if entry.get("kind") == "submissions"
        }

    def _load(self, relative: str) -> Any:
        """Load a file listed in the manifest; refuse files the manifest does not list."""
        if relative not in self._entries:
            raise FixtureError(f"Fixture file not listed in manifest.json: {relative}")
        return _read_json(self.root / relative)

    @cached_property
    def synthetic(self) -> bool:
        """True unless the manifest says `synthetic: false` and no loaded file is marked."""
        files = [self.manifest, self._tickers, *self._submissions.values()]
        marked = any(isinstance(f, dict) and SYNTHETIC_KEY in f for f in files)
        return self.manifest.get("synthetic") is not False or marked

    @property
    def snapshot_date(self) -> date:
        """The capture date recorded in the manifest."""
        return date.fromisoformat(self.manifest["snapshot_date"])

    def source_url(self, relative: str) -> str:
        """The original SEC URL of a fixture file."""
        return self._entries[relative]["source_url"]

    def source_info(self, files: list[str]) -> SourceInfo:
        """SourceInfo for a response built from the given fixture files."""
        label = SYNTHETIC_LABEL if self.synthetic else RECORDED_LABEL
        snapshot = self.snapshot_date
        return SourceInfo(
            mode="demo",
            label=f"{label} · snapshot {snapshot.isoformat()}",
            retrieved_at=None,
            snapshot_date=snapshot,
            source_urls=[self.source_url(path) for path in files],
        )

    def submissions_path(self, cik: str) -> str:
        """Relative path of a company's submissions fixture."""
        return f"submissions/CIK{cik}.json"

    def submissions(self, cik: str) -> dict[str, Any] | None:
        """The recorded submissions JSON for a 10-digit CIK, or None if not in the snapshot."""
        return self._submissions.get(cik)

    def universe_files(self) -> list[str]:
        """The fixture files the search universe is built from."""
        return ["company_tickers.json", *(self.submissions_path(c) for c in self._submissions)]

    def universe(self) -> list[UniverseCompany]:
        """The demo companies in ticker-file order, one per CIK, tickers primary first."""
        tickers_by_cik: dict[str, list[str]] = {}
        for key, row in self._tickers.items():
            if key == SYNTHETIC_KEY:
                continue
            cik = str(row["cik_str"]).zfill(10)
            tickers_by_cik.setdefault(cik, []).append(row["ticker"])
        companies = []
        for cik, tickers in tickers_by_cik.items():
            sub = self._submissions.get(cik)
            if sub is None:
                continue
            extra = [t for t in sub.get("tickers", []) if t not in tickers]
            companies.append(UniverseCompany(cik, sub["name"], tuple(tickers + extra)))
        return companies
