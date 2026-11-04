"""Disk cache for SEC responses (one JSON file per URL, kept for 24 hours).

File: `<root>/<sha256 of the URL>.json` holding `{url, retrieved_at, status, body}`. Files are
written atomically (temporary file, then rename). A corrupt or foreign file is ignored and
refetched, and an expired entry is treated as absent. There is no background refresh.
"""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

TTL = timedelta(hours=24)


def utc_now() -> datetime:
    """The current time in UTC."""
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class CacheEntry:
    """One cached SEC response."""

    url: str
    retrieved_at: datetime
    body: Any


class DiskCache:
    """Reads and writes SEC responses under `root`. `clock` is injectable for tests."""

    def __init__(self, root: Path, clock: Callable[[], datetime] = utc_now) -> None:
        self.root = Path(root)
        self._clock = clock

    def path_for(self, url: str) -> Path:
        """The cache file of a URL: its name is the URL's SHA-256."""
        return self.root / f"{hashlib.sha256(url.encode('utf-8')).hexdigest()}.json"

    def get(self, url: str) -> CacheEntry | None:
        """The entry for `url` if it exists, is readable, matches `url` and is under 24 h old."""
        try:
            raw = json.loads(self.path_for(url).read_text(encoding="utf-8"))
            retrieved_at = datetime.fromisoformat(raw["retrieved_at"])
            if raw["url"] != url or retrieved_at.tzinfo is None:
                return None
            body = raw["body"]
        except (OSError, ValueError, KeyError, TypeError):
            return None  # absent or corrupt: refetch rather than fail
        if self._clock() - retrieved_at >= TTL:
            return None
        return CacheEntry(url=url, retrieved_at=retrieved_at, body=body)

    def put(self, url: str, body: Any, status: int = 200) -> CacheEntry:
        """Store a response atomically and return the entry."""
        retrieved_at = self._clock()
        record = {
            "url": url,
            "retrieved_at": retrieved_at.isoformat(),
            "status": status,
            "body": body,
        }
        self.root.mkdir(parents=True, exist_ok=True)
        fd, temp_name = tempfile.mkstemp(dir=self.root, suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as temp:
                json.dump(record, temp)
            os.replace(temp_name, self.path_for(url))
        except BaseException:
            Path(temp_name).unlink(missing_ok=True)
            raise
        return CacheEntry(url=url, retrieved_at=retrieved_at, body=body)
