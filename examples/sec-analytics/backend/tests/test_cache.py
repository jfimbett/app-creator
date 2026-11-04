"""Disk cache for SEC responses: TTL, corrupt files, atomic writes, key by URL hash. Offline."""

import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from app.data.cache import DiskCache

URL = "https://data.sec.gov/submissions/CIK0000320193.json"
START = datetime(2026, 11, 3, 12, 0, tzinfo=timezone.utc)


class Clock:
    def __init__(self) -> None:
        self.now = START

    def __call__(self) -> datetime:
        return self.now


def test_key_is_the_url_hash(tmp_path: Path) -> None:
    expected = hashlib.sha256(URL.encode()).hexdigest() + ".json"
    assert DiskCache(tmp_path).path_for(URL).name == expected


def test_put_then_get_returns_body_and_retrieval_time(tmp_path: Path) -> None:
    cache = DiskCache(tmp_path, Clock())
    cache.put(URL, {"a": 1})
    entry = cache.get(URL)
    assert (entry.body, entry.retrieved_at) == ({"a": 1}, START)
    stored = json.loads(cache.path_for(URL).read_text(encoding="utf-8"))
    assert set(stored) == {"url", "retrieved_at", "status", "body"}


def test_entry_expires_after_24_hours(tmp_path: Path) -> None:
    clock = Clock()
    cache = DiskCache(tmp_path, clock)
    cache.put(URL, {"a": 1})
    clock.now = START + timedelta(hours=23, minutes=59)
    assert cache.get(URL) is not None
    clock.now = START + timedelta(hours=24)
    assert cache.get(URL) is None


def test_corrupt_file_is_ignored(tmp_path: Path) -> None:
    cache = DiskCache(tmp_path, Clock())
    cache.put(URL, {"a": 1})
    cache.path_for(URL).write_text("{not json", encoding="utf-8")
    assert cache.get(URL) is None


def test_file_for_another_url_is_ignored(tmp_path: Path) -> None:
    cache = DiskCache(tmp_path, Clock())
    cache.put(URL, {"a": 1})
    stored = json.loads(cache.path_for(URL).read_text(encoding="utf-8"))
    stored["url"] = "https://data.sec.gov/submissions/CIK0000000001.json"
    cache.path_for(URL).write_text(json.dumps(stored), encoding="utf-8")
    assert cache.get(URL) is None


def test_write_leaves_no_temporary_file_and_a_failed_write_keeps_the_old_entry(
    tmp_path: Path,
) -> None:
    cache = DiskCache(tmp_path, Clock())
    cache.put(URL, {"a": 1})
    assert [p.suffix for p in tmp_path.iterdir()] == [".json"]
    try:
        cache.put(URL, {"bad": object()})  # not JSON-serializable
    except TypeError:
        pass
    assert cache.get(URL).body == {"a": 1}
    assert [p.suffix for p in tmp_path.iterdir()] == [".json"]


def test_absent_entry_and_absent_folder(tmp_path: Path) -> None:
    assert DiskCache(tmp_path / "nowhere").get(URL) is None
