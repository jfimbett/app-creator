"""The recorded fixtures are complete, traceable and kept apart from synthetic data (M1-AC7).

Reads only local files: `examples/sec-analytics/fixtures/` and `tests/synthetic/`. No network.
"""

import gzip
import hashlib
import json
import re
from pathlib import Path

import pytest

from app.logic.concepts import CAPTURE_CONCEPTS

BACKEND_DIR = Path(__file__).resolve().parents[1]
FIXTURES_DIR = BACKEND_DIR.parent / "fixtures"
SYNTHETIC_DIR = BACKEND_DIR / "tests" / "synthetic"
NOT_LISTED = {"README.md", ".gitattributes", "manifest.json"}
MARKER = "SYNTHETIC: invented for tests"
REQUIRED_KEYS = {"path", "kind", "source_url", "retrieved_at", "sha256", "bytes", "accessions",
                 "periods", "scope", "trimmed"}
EXPECTED_CIKS = {"0000320193", "0000789019", "0001652044"}
EMAIL_LIKE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")


def _manifest() -> dict:
    return json.loads((FIXTURES_DIR / "manifest.json").read_text(encoding="utf-8"))


def _data_files() -> set[str]:
    return {
        path.relative_to(FIXTURES_DIR).as_posix()
        for path in FIXTURES_DIR.rglob("*")
        if path.is_file() and path.name not in NOT_LISTED
    }


def test_manifest_is_recorded_sec_data() -> None:
    manifest = _manifest()
    assert manifest["schema_version"] == 1
    assert manifest["label"] == "RECORDED SEC DEMO"
    assert manifest["synthetic"] is False
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", manifest["snapshot_date"])
    assert manifest["user_agent"] == "configured locally; not recorded"


def test_every_data_file_is_listed_once() -> None:
    listed = [entry["path"] for entry in _manifest()["files"]]
    assert len(listed) == len(set(listed))
    assert set(listed) == _data_files()


def test_each_entry_has_provenance_and_matching_hash() -> None:
    for entry in _manifest()["files"]:
        assert REQUIRED_KEYS <= entry.keys(), entry["path"]
        assert entry["source_url"].startswith(("https://data.sec.gov/", "https://www.sec.gov/"))
        assert re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", entry["retrieved_at"])
        assert entry["scope"] and entry["trimmed"]
        content = (FIXTURES_DIR / entry["path"]).read_bytes()
        assert hashlib.sha256(content).hexdigest() == entry["sha256"], entry["path"]
        assert len(content) == entry["bytes"], entry["path"]


def test_three_demo_companies_with_submissions_and_facts() -> None:
    files = _manifest()["files"]
    for kind in ("submissions", "companyfacts"):
        assert {entry["cik"] for entry in files if entry["kind"] == kind} == EXPECTED_CIKS
    assert [entry["kind"] for entry in files].count("company_tickers") == 1


def test_companyfacts_keep_only_capture_concepts() -> None:
    for entry in _manifest()["files"]:
        if entry["kind"] != "companyfacts":
            continue
        data = json.loads((FIXTURES_DIR / entry["path"]).read_text(encoding="utf-8"))
        assert set(data) == {"cik", "entityName", "facts"}
        assert set(data["facts"]) == {"us-gaap"}
        kept = set(data["facts"]["us-gaap"])
        assert kept <= set(CAPTURE_CONCEPTS)
        assert kept | set(entry["concepts_absent"]) == set(CAPTURE_CONCEPTS)
        for concept in data["facts"]["us-gaap"].values():
            assert set(concept) == {"label", "description", "units"}


def test_submissions_keep_only_annual_and_quarterly_forms() -> None:
    allowed = {"10-K", "10-K/A", "10-Q", "10-Q/A"}
    for entry in _manifest()["files"]:
        if entry["kind"] != "submissions":
            continue
        recent = json.loads((FIXTURES_DIR / entry["path"]).read_text(encoding="utf-8"))
        recent = recent["filings"]["recent"]
        lengths = {len(column) for column in recent.values()}
        assert len(lengths) == 1  # columns stay row-aligned
        assert set(recent["form"]) <= allowed


def test_no_synthetic_marker_or_email_under_fixtures() -> None:
    for path in FIXTURES_DIR.rglob("*"):
        if path.is_file() and path.suffix != ".gz":
            text = path.read_text(encoding="utf-8")
            assert MARKER not in text, path.name
            assert '"_synthetic"' not in text, path.name
            assert not EMAIL_LIKE.search(text), path.name


def test_filing_documents_are_listed_authentic_and_unmodified_gzip() -> None:
    # Filing text may hold a company's own published addresses, so only the marker is checked here.
    entries = [e for e in _manifest()["files"] if e["kind"] == "filing_document"]
    assert {e["cik"] for e in entries} == EXPECTED_CIKS
    assert sorted(e["form"] for e in entries) == ["10-K"] * 3 + ["10-Q"] * 3
    for entry in entries:
        assert entry["path"].endswith(".gz")
        assert entry["trimmed"] == "none; stored gzip-compressed"
        assert entry["source_url"].startswith("https://www.sec.gov/Archives/edgar/data/")
        assert entry["source_url"].rsplit("/", 1)[1] == Path(entry["path"]).stem
        text = gzip.decompress((FIXTURES_DIR / entry["path"]).read_bytes())
        assert MARKER.encode() not in text
        assert b"<html" in text[:2000].lower()


def test_amendment_rows_are_recorded_per_company() -> None:
    manifest = _manifest()
    counts = manifest["amendment_rows"]
    assert set(counts) == EXPECTED_CIKS
    assert all(set(row) == {"10-K/A", "10-Q/A"} for row in counts.values())
    assert counts["0001652044"] == {"10-K/A": 1, "10-Q/A": 0}  # the only amendment recorded


def test_older_submissions_pages_keep_only_the_four_forms() -> None:
    pages = [e for e in _manifest()["files"] if e["kind"] == "submissions_page"]
    for entry in pages:
        page = json.loads((FIXTURES_DIR / entry["path"]).read_text(encoding="utf-8"))
        assert set(page["form"]) <= {"10-K", "10-K/A", "10-Q", "10-Q/A"}
        assert len({len(column) for column in page.values()}) == 1


@pytest.mark.parametrize(
    "path", sorted(p for p in SYNTHETIC_DIR.rglob("*") if p.is_file()), ids=lambda p: p.name
)
def test_every_synthetic_file_carries_the_marker(path: Path) -> None:
    assert MARKER in path.read_text(encoding="utf-8")
