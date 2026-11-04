"""Capture the recorded SEC fixtures for the demo universe (milestone brief §6).

Run from the backend folder with its own Python:
    .venv/bin/python scripts/capture_fixtures.py        (macOS/Linux)
    .venv\\Scripts\\python.exe scripts\\capture_fixtures.py  (Windows)

It makes exactly 7 requests through `app.clients.sec` (allowlist, 1 request per second, 20 s
timeout, Retry-After, no retry on 403): the ticker list, then submissions and company facts for each
company. Everything is fetched into memory first; files are written only when every request
succeeded, so a blocked run leaves no partial fixtures. The existing `fixtures/` folder is replaced
as a whole.

`SEC_USER_AGENT` comes from the process environment, or else from the repository-root `.env` (only
that key is parsed). Its value is never printed, logged or written anywhere.

`--filings` adds to the fixtures instead of replacing them (milestone brief M3 §6). It reads the
recorded submissions files without refetching them, downloads the latest original 10-K and 10-Q of
each company (6 requests) and stores each one gzip-compressed and otherwise unmodified. When a
company's recorded list does not reach back 10 years it also downloads the older submissions
page(s) SEC lists for that window. Existing data files stay untouched; manifest.json gains entries.

Exit codes: 0 done, 2 `SEC_USER_AGENT` missing or malformed, 3 SEC request failed, 4 the data did
not match what was expected (for example a ticker resolved to an unexpected CIK).
"""

from __future__ import annotations

import gzip
import hashlib
import json
import os
import shutil
import sys
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import httpx

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from app.clients.sec import (  # noqa: E402
    COMPANY_TICKERS_URL,
    SecClient,
    SecContactNotConfigured,
    SecError,
    companyfacts_url,
    submissions_url,
    validate_user_agent,
)
from app.logic import filings as filing_logic  # noqa: E402
from app.logic.archive import document_url  # noqa: E402
from app.logic.concepts import (  # noqa: E402
    CAPTURE_CONCEPTS,
    NET_INCOME_CONCEPT,
    REVENUE_CONCEPTS,
    TAXONOMY,
)

REPO_ROOT = BACKEND_DIR.parents[2]
FIXTURES_DIR = BACKEND_DIR.parent / "fixtures"
SETTING = "SEC_USER_AGENT"
# Tickers resolved from company_tickers.json; the run stops if SEC maps them to other CIKs.
EXPECTED = {"AAPL": "0000320193", "MSFT": "0000789019", "GOOGL": "0001652044"}
KEPT_FORMS = ("10-K", "10-K/A", "10-Q", "10-Q/A")
ANNUAL_FORMS = ("10-K", "10-K/A")
ANNUAL_DAYS = (350, 380)


class CaptureStopped(Exception):
    """The capture cannot continue; `exit_code` says why."""

    def __init__(self, message: str, exit_code: int) -> None:
        super().__init__(message)
        self.exit_code = exit_code


@dataclass
class Fetched:
    """One downloaded document, kept in memory until every request has succeeded."""

    kind: str
    url: str
    retrieved_at: str
    body: Any
    cik: str | None = None


@dataclass
class CountingTransport(httpx.BaseTransport):
    """Wraps the real transport and counts every HTTP request (retries and redirects included)."""

    inner: httpx.BaseTransport = field(default_factory=httpx.HTTPTransport)
    count: int = 0

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        self.count += 1
        return self.inner.handle_request(request)

    def close(self) -> None:
        self.inner.close()


# ---------------------------------------------------------------- settings


def read_user_agent() -> str:
    """`SEC_USER_AGENT` from the environment or the root `.env`; validated, never echoed."""
    value = os.environ.get(SETTING) or _from_root_env()
    try:
        return validate_user_agent(value)
    except SecContactNotConfigured as exc:
        raise CaptureStopped(str(exc), exit_code=2) from exc


def _from_root_env() -> str | None:
    """Parse only the `SEC_USER_AGENT=` line of the root `.env`, like the root launchers."""
    path = REPO_ROOT / ".env"
    if not path.is_file():
        return None
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("export "):
            line = line[len("export ") :].lstrip()
        key, sep, value = line.partition("=")
        if sep and key.strip() == SETTING:
            value = value.strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                value = value[1:-1]
            return value or None
    return None


# ---------------------------------------------------------------- fetching


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _get(client: SecClient, kind: str, url: str, cik: str | None = None) -> Fetched:
    """Fetch one allowlisted JSON document and timestamp it."""
    body = client.get_json(url)
    return Fetched(kind=kind, url=url, retrieved_at=_utc_stamp(), body=body, cik=cik)


def resolve_ciks(tickers: dict[str, Any]) -> dict[str, str]:
    """Map the expected tickers to 10-digit CIKs; stop if any is absent or different."""
    found = {
        entry.get("ticker"): str(entry.get("cik_str")).zfill(10)
        for entry in tickers.values()
        if isinstance(entry, dict)
    }
    for ticker, expected in EXPECTED.items():
        if found.get(ticker) != expected:
            raise CaptureStopped(
                f"{ticker} resolves to CIK {found.get(ticker)}, expected {expected}; "
                "check the demo universe before recapturing",
                exit_code=4,
            )
    return {ticker: found[ticker] for ticker in EXPECTED}


def fetch_all(client: SecClient) -> list[Fetched]:
    """The 7 requests, in order: ticker list, then submissions and company facts per company."""
    tickers = _get(client, "company_tickers", COMPANY_TICKERS_URL)
    if not isinstance(tickers.body, dict):
        raise CaptureStopped("company_tickers.json is not a JSON object", exit_code=4)
    fetched = [tickers]
    for cik in resolve_ciks(tickers.body).values():
        fetched.append(_get(client, "submissions", submissions_url(cik), cik))
        fetched.append(_get(client, "companyfacts", companyfacts_url(cik), cik))
    return fetched


# ---------------------------------------------------------------- trimming


def trim_tickers(body: dict[str, Any]) -> dict[str, Any]:
    """Entries of the original object whose `cik_str` is a demo CIK; keys and fields unchanged."""
    wanted = set(EXPECTED.values())
    return {
        key: entry
        for key, entry in body.items()
        if isinstance(entry, dict) and str(entry.get("cik_str")).zfill(10) in wanted
    }


def trim_submissions(body: dict[str, Any]) -> dict[str, Any]:
    """All top-level fields; `filings.recent` keeps 10-K/10-Q rows (all columns, row-aligned)."""
    filings = body.get("filings")
    if not isinstance(filings, dict) or not isinstance(filings.get("recent"), dict):
        raise CaptureStopped("submissions JSON has no filings.recent table", exit_code=4)
    recent = filings["recent"]
    forms = recent.get("form")
    if not isinstance(forms, list) or {len(col) for col in recent.values()} != {len(forms)}:
        raise CaptureStopped("submissions filings.recent columns are not aligned", exit_code=4)
    rows = [i for i, form in enumerate(forms) if form in KEPT_FORMS]
    kept_recent = {name: [column[i] for i in rows] for name, column in recent.items()}
    return {**body, "filings": {**filings, "recent": kept_recent}}


def trim_companyfacts(body: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    """Keep `cik`, `entityName` and us-gaap `CAPTURE_CONCEPTS` unmodified; list absent ones."""
    gaap = body.get("facts", {}).get(TAXONOMY)
    if not isinstance(gaap, dict):
        raise CaptureStopped("companyfacts JSON has no us-gaap facts", exit_code=4)
    wanted = set(CAPTURE_CONCEPTS)
    kept = {
        name: {key: concept.get(key) for key in ("label", "description", "units")}
        for name, concept in gaap.items()
        if name in wanted
    }
    absent = [name for name in CAPTURE_CONCEPTS if name not in kept]
    trimmed = {"cik": body.get("cik"), "entityName": body.get("entityName"),
               "facts": {TAXONOMY: kept}}
    return trimmed, absent


# ---------------------------------------------------------------- manifest details


def _iter_facts(trimmed: dict[str, Any], concepts: tuple[str, ...] | None = None):
    for name, concept in trimmed["facts"][TAXONOMY].items():
        if concepts is not None and name not in concepts:
            continue
        for facts in concept["units"].values():
            yield from facts


def _is_annual_10k(fact: dict[str, Any]) -> bool:
    if fact.get("form") not in ANNUAL_FORMS or not fact.get("start") or not fact.get("end"):
        return False
    days = (date.fromisoformat(fact["end"]) - date.fromisoformat(fact["start"])).days
    return ANNUAL_DAYS[0] <= days <= ANNUAL_DAYS[1]


def companyfacts_details(trimmed: dict[str, Any]) -> tuple[list[str], dict[str, Any]]:
    """Distinct accessions, and earliest/latest annual 10-K end dates for revenue and net income."""
    accessions = sorted({fact["accn"] for fact in _iter_facts(trimmed) if fact.get("accn")})
    periods: dict[str, Any] = {}
    for label, concepts in (("revenue", REVENUE_CONCEPTS), ("net_income", (NET_INCOME_CONCEPT,))):
        ends = sorted({f["end"] for f in _iter_facts(trimmed, concepts) if _is_annual_10k(f)})
        periods[label] = {
            "annual_10k_end_earliest": ends[0] if ends else None,
            "annual_10k_end_latest": ends[-1] if ends else None,
            "annual_10k_period_count": len(ends),
        }
    return accessions, periods


def submissions_details(trimmed: dict[str, Any]) -> tuple[list[str], dict[str, Any]]:
    """Distinct accessions and earliest/latest filingDate among the kept rows."""
    recent = trimmed["filings"]["recent"]
    dates = sorted(recent.get("filingDate", []))
    periods = {"filing_date_earliest": dates[0] if dates else None,
               "filing_date_latest": dates[-1] if dates else None,
               "rows_kept": len(dates)}
    return sorted(set(recent.get("accessionNumber", []))), periods


# ---------------------------------------------------------------- writing


def _dump(path: Path, data: Any) -> bytes:
    path.parent.mkdir(parents=True, exist_ok=True)
    content = (json.dumps(data, indent=1, ensure_ascii=False) + "\n").encode("utf-8")
    path.write_bytes(content)
    return content


def build_entry(item: Fetched, out_dir: Path) -> dict[str, Any]:
    """Trim one document, write it, and return its manifest entry."""
    entry: dict[str, Any] = {"kind": item.kind}
    if item.kind == "company_tickers":
        rel, data = "company_tickers.json", trim_tickers(item.body)
        accessions, periods = [], {}
        scope = "Entries of SEC's ticker list whose cik_str is Apple, Microsoft or Alphabet."
        trimmed = "All other companies' entries removed; kept entries unchanged."
    elif item.kind == "submissions":
        rel, data = f"submissions/CIK{item.cik}.json", trim_submissions(item.body)
        accessions, periods = submissions_details(data)
        scope = ("All top-level fields unchanged; filings.recent rows with form 10-K, 10-K/A, "
                 "10-Q or 10-Q/A, all columns, row-aligned; filings.files unchanged.")
        trimmed = ("Other forms' rows removed from filings.recent; the older pages listed in "
                   "filings.files were not downloaded.")
    else:
        data, absent = trim_companyfacts(item.body)
        rel = f"companyfacts/CIK{item.cik}.json"
        accessions, periods = companyfacts_details(data)
        entry["concepts_absent"] = absent
        scope = ("cik, entityName and the us-gaap concepts in CAPTURE_CONCEPTS, each with label, "
                 "description and every fact in every unit and form, unmodified.")
        trimmed = ("Other us-gaap concepts and other taxonomies (dei, ...) removed to keep the "
                   "snapshot small; concepts_absent lists capture concepts SEC had none of.")
    content = _dump(out_dir / rel, data)
    if item.cik:
        entry["cik"] = item.cik
    entry.update(
        path=rel, source_url=item.url, retrieved_at=item.retrieved_at,
        sha256=hashlib.sha256(content).hexdigest(), bytes=len(content),
        accessions=accessions, periods=periods, scope=scope, trimmed=trimmed,
    )
    return {"path": entry.pop("path"), **entry}


README = """# Recorded SEC fixtures (RECORDED SEC DEMO)

Authentic data from SEC EDGAR, recorded on **{snapshot}** (UTC) for the demo universe: Apple
(CIK 0000320193), Microsoft (0000789019) and Alphabet (0001652044). The app serves these files
offline in fixture mode and labels them `RECORDED SEC DEMO · snapshot {snapshot}`.

- `company_tickers.json`: the three companies' entries from
  https://www.sec.gov/files/company_tickers.json.
- `submissions/CIK##########.json`: https://data.sec.gov/submissions/, with `filings.recent` cut
  down to 10-K, 10-K/A, 10-Q and 10-Q/A rows.
- `companyfacts/CIK##########.json`: https://data.sec.gov/api/xbrl/companyfacts/, only the us-gaap
  concepts in `backend/app/logic/concepts.py` `CAPTURE_CONCEPTS`.
- `manifest.json`: for every file the source URL, retrieval time, sha256, size, accession numbers,
  periods, what was kept and what was trimmed. No value was edited, rounded or reordered.

The User-Agent used for the capture was configured locally by the person who ran it and is not
recorded.

## Recapture

These files change only by running the capture script; never edit them by hand. With your own
`SEC_USER_AGENT` set (see the root `.env.example`), from `examples/sec-analytics/backend/`:

    .venv/bin/python scripts/capture_fixtures.py

(Windows: `.venv\\Scripts\\python.exe scripts\\capture_fixtures.py`). It makes 7 requests, at
most one per second, and replaces this whole folder.

**Warning:** a recapture changes every number. The hand-worked known answers (`FX…` rows in
`milestones/acceptance.md`) must be worked out again from the new files before the tests that use
them are updated.
"""


def write_fixtures(fetched: list[Fetched], snapshot: str) -> list[dict[str, Any]]:
    """Write into a temporary sibling folder, then swap it in place of `fixtures/`."""
    staging = FIXTURES_DIR.with_name("fixtures.capture-tmp")
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir()
    entries = [build_entry(item, staging) for item in fetched]
    manifest = {
        "schema_version": 1, "label": "RECORDED SEC DEMO", "synthetic": False,
        "snapshot_date": snapshot, "captured_with": "be/scripts/capture_fixtures.py",
        "user_agent": "configured locally; not recorded", "files": entries,
    }
    _dump(staging / "manifest.json", manifest)
    (staging / "README.md").write_text(README.format(snapshot=snapshot), encoding="utf-8")
    (staging / ".gitattributes").write_text("* -text\n", encoding="utf-8")
    old = FIXTURES_DIR.with_name("fixtures.previous")
    if FIXTURES_DIR.exists():
        FIXTURES_DIR.rename(old)
    staging.rename(FIXTURES_DIR)
    if old.exists():
        shutil.rmtree(old)
    return entries


# ---------------------------------------------------------------- --filings

MAX_DOCUMENT_BYTES = 20 * 1024 * 1024
DOCUMENT_SCOPE = (
    "The complete primary document of this filing as SEC serves it. Exhibits and other documents "
    "in the same filing are separate files and were not captured."
)
DOCUMENT_TRIMMED = "none; stored gzip-compressed"
PAGE_SCOPE = (
    "An older page of SEC's submissions list, rows with form 10-K, 10-K/A, 10-Q or 10-Q/A, all "
    "columns, row-aligned."
)
PAGE_TRIMMED = "Other forms' rows removed."


def _trim_page(body: dict[str, Any]) -> dict[str, Any]:
    forms = body.get("form")
    if not isinstance(forms, list) or {len(col) for col in body.values()} != {len(forms)}:
        raise CaptureStopped("submissions page columns are not aligned", exit_code=4)
    rows = [i for i, form in enumerate(forms) if form in KEPT_FORMS]
    return {name: [column[i] for i in rows] for name, column in body.items()}


def _filing_entry(row: filing_logic.FilingMeta, cik: str, content: bytes, stored: str) -> dict:
    return {
        "path": stored, "kind": "filing_document", "cik": cik, "source_url": row.document_url,
        "retrieved_at": _utc_stamp(), "sha256": hashlib.sha256(content).hexdigest(),
        "bytes": len(content), "accessions": [row.accession],
        "periods": {"report_date": row.report_date.isoformat() if row.report_date else None},
        "form": row.form, "scope": DOCUMENT_SCOPE, "trimmed": DOCUMENT_TRIMMED,
    }


def capture_filings(client: SecClient, manifest: dict[str, Any]) -> dict[str, bytes]:
    """Fetch every new file into memory, and add its manifest entry. Returns path -> content."""
    new: dict[str, bytes] = {}
    entries: list[dict[str, Any]] = []
    amendments: dict[str, dict[str, int]] = {}
    snapshot = date.fromisoformat(manifest["snapshot_date"])
    start = filing_logic.window_start(snapshot, filing_logic.MAX_YEARS)
    for cik in EXPECTED.values():
        recorded = json.loads(
            (FIXTURES_DIR / "submissions" / f"CIK{cik}.json").read_text(encoding="utf-8")
        )
        recent = recorded["filings"]["recent"]
        rows = filing_logic.parse_rows(recent, cik)
        tables = [rows]
        for name in filing_logic.older_pages_needed(recent, recorded["filings"]["files"], start):
            url = f"https://data.sec.gov/submissions/{name}"
            page = _trim_page(client.get_json(url))
            content = (json.dumps(page, indent=1, ensure_ascii=False) + "\n").encode("utf-8")
            stored = f"submissions/{name}"
            new[stored] = content
            page_rows = filing_logic.parse_rows(page, cik)
            tables.append(page_rows)
            dates = sorted(row.filing_date.isoformat() for row in page_rows)
            entries.append({
                "path": stored, "kind": "submissions_page", "cik": cik, "source_url": url,
                "retrieved_at": _utc_stamp(), "sha256": hashlib.sha256(content).hexdigest(),
                "bytes": len(content), "accessions": sorted(r.accession for r in page_rows),
                "periods": {"filing_date_earliest": dates[0] if dates else None,
                            "filing_date_latest": dates[-1] if dates else None,
                            "rows_kept": len(dates)},
                "scope": PAGE_SCOPE, "trimmed": PAGE_TRIMMED,
            })
        every_row = filing_logic.merge_rows(*tables)
        amendments[cik] = {
            form: sum(1 for row in filing_logic.in_window(every_row, start) if row.form == form)
            for form in ("10-K/A", "10-Q/A")
        }
        latest = filing_logic.select_latest(every_row, "capture")
        for row in (latest.annual, latest.quarterly):
            if row is None or row.document_url is None:
                raise CaptureStopped(f"CIK {cik} has no usable 10-K or 10-Q", exit_code=4)
            url = document_url(cik, row.accession, row.primary_document)
            body = client.fetch(url, max_bytes=MAX_DOCUMENT_BYTES).content
            content = gzip.compress(body, compresslevel=9, mtime=0)
            stored = f"filings/{cik}/{row.accession}/{row.primary_document}.gz"
            new[stored] = content
            entries.append(_filing_entry(row, cik, content, stored))
    new_paths = {entry["path"] for entry in entries}
    manifest["files"] = [e for e in manifest["files"] if e["path"] not in new_paths] + entries
    manifest["amendment_rows"] = amendments
    return new


def main_filings() -> int:
    """Add filing documents to the fixtures. Writes nothing unless every request succeeded."""
    transport = CountingTransport()
    manifest = json.loads((FIXTURES_DIR / "manifest.json").read_text(encoding="utf-8"))
    try:
        user_agent = read_user_agent()
        print(f"{SETTING}: set (value hidden)")
        with SecClient(user_agent, transport=transport) as client:
            new = capture_filings(client, manifest)
    except CaptureStopped as exc:
        print(f"Capture stopped: {exc}", file=sys.stderr)
        return exc.exit_code
    except SecError as exc:
        print(f"Capture stopped after {transport.count} request(s): {exc}. "
              "No fixtures were written.", file=sys.stderr)
        return 3
    for relative, content in new.items():
        path = FIXTURES_DIR / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    _dump(FIXTURES_DIR / "manifest.json", manifest)
    print(f"Added {len(new)} files in {transport.count} requests.")
    print(f"Amendment rows in the snapshot, per CIK: {manifest['amendment_rows']}")
    for relative, content in sorted(new.items()):
        print(f"  {relative}  {len(content)} bytes")
    return 0


def main() -> int:
    """Run the capture; print progress without the User-Agent value."""
    if "--filings" in sys.argv[1:]:
        return main_filings()
    transport = CountingTransport()
    try:
        user_agent = read_user_agent()
        print(f"{SETTING}: set (value hidden)")
        with SecClient(user_agent, transport=transport) as client:
            fetched = fetch_all(client)
    except CaptureStopped as exc:
        print(f"Capture stopped: {exc}", file=sys.stderr)
        return exc.exit_code
    except SecError as exc:
        print(f"Capture stopped after {transport.count} request(s): {exc}. "
              "No fixtures were written.", file=sys.stderr)
        return 3
    snapshot = datetime.now(timezone.utc).date().isoformat()
    try:
        entries = write_fixtures(fetched, snapshot)
    except CaptureStopped as exc:
        print(f"Capture stopped: {exc}. No fixtures were written.", file=sys.stderr)
        return exc.exit_code
    print(f"Captured {len(entries)} files in {transport.count} requests; snapshot {snapshot}.")
    print(f"Written to {FIXTURES_DIR.as_posix()}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
