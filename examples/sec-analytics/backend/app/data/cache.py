"""Disk caches for SEC responses.

`DiskCache`: JSON documents, one file per URL, kept for 24 hours.
`DocumentCache`: filing documents, kept until deleted, because an accession number never changes.

File: `<root>/<sha256 of the URL>.json` holding `{url, retrieved_at, status, body}`. Files are
written atomically (temporary file, then rename). A corrupt or foreign file is ignored and
refetched, and an expired entry is treated as absent. There is no background refresh.
"""

from __future__ import annotations

import gzip
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


@dataclass(frozen=True)
class CachedDocument:
    """One stored filing document."""

    url: str
    retrieved_at: datetime
    content: bytes


class DocumentCache:
    """Filing documents under `<root>/filings/<sha256 of the URL>.{gz,json}`, with no expiry.

    The file name comes from a hash, so nothing from a document or a request becomes a path. A
    corrupt pair is ignored and fetched again.
    """

    def __init__(self, root: Path, clock: Callable[[], datetime] = utc_now) -> None:
        self.root = Path(root) / "filings"
        self._clock = clock

    def _paths(self, url: str) -> tuple[Path, Path]:
        name = hashlib.sha256(url.encode("utf-8")).hexdigest()
        return self.root / f"{name}.gz", self.root / f"{name}.json"

    def get(self, url: str) -> CachedDocument | None:
        """The stored document for `url`, or None if absent or unreadable."""
        body_path, record_path = self._paths(url)
        try:
            record = json.loads(record_path.read_text(encoding="utf-8"))
            retrieved_at = datetime.fromisoformat(record["retrieved_at"])
            if record["url"] != url or retrieved_at.tzinfo is None:
                return None
            content = gzip.decompress(body_path.read_bytes())
        except (OSError, ValueError, KeyError, TypeError, EOFError):
            return None
        return CachedDocument(url, retrieved_at, content)

    def put(self, url: str, content: bytes) -> CachedDocument:
        """Store a document atomically: the record is written last, so it marks a complete pair."""
        retrieved_at = self._clock()
        body_path, record_path = self._paths(url)
        self.root.mkdir(parents=True, exist_ok=True)
        record = {"url": url, "retrieved_at": retrieved_at.isoformat()}
        _write_atomic(self.root, body_path, gzip.compress(content, mtime=0))
        _write_atomic(self.root, record_path, json.dumps(record).encode("utf-8"))
        return CachedDocument(url, retrieved_at, content)


def _write_atomic(folder: Path, target: Path, content: bytes) -> None:
    fd, temp_name = tempfile.mkstemp(dir=folder, suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as temp:
            temp.write(content)
        os.replace(temp_name, target)
    except BaseException:
        Path(temp_name).unlink(missing_ok=True)
        raise
