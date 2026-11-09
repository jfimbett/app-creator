"""M3 API: filing list and reader in demo (authentic fixtures) and live (SEC mocked with respx).

"Fixture" tests read recorded SEC data. "Mocked" tests use invented documents through a fake SEC, so
they show this app's handling, never SEC's real answers. No test here reaches the network.
"""

import gzip
import json
from datetime import date, datetime, timezone
from pathlib import Path

import httpx
import pytest
import respx
from fastapi.testclient import TestClient
from pydantic import SecretStr

from app.api import filings as filings_api
from app.clients.sec import SecClient, submissions_url
from app.data import source as source_module
from app.data.source import DataSource
from app.main import create_app
from app.settings import Settings

APPLE = "0000320193"
ALPHABET = "0001652044"
EXAMPLE = "0000000999"
APPLE_10K = "0000320193-26-000026"
APPLE_10Q = "0000320193-26-000020"
APPLE_OLD_10K = "0000320193-25-000079"
APPLE_10K_URL = (
    "https://www.sec.gov/Archives/edgar/data/320193/000032019326000026/aapl-20260926.htm"
)
FAKE_UA = "SEC Analytics tests " + "tests" + "@" + "sec-analytics.invalid"
DOCS = Path(__file__).parent / "synthetic" / "filings"
EXAMPLE_SUBMISSIONS = json.loads((DOCS / "amended_submissions.json").read_text())
DOC_URL = "https://www.sec.gov/Archives/edgar/data/999/000000099926000002/xmpl-k.htm"
SOURCE_LINK_PREFIX = "https://www.sec.gov/Archives/edgar/data/"


class NoWait:
    def __init__(self) -> None:
        self.now = 0.0

    def clock(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        self.now += seconds


@pytest.fixture(scope="module")
def demo() -> TestClient:
    return TestClient(create_app(Settings(data_mode="fixtures")))


# Live tests run on a fixed day, so the 10-year window and "older page needed" stay the same
# whatever the real date is (test review 2026-11-09: they would have failed from 2030).
TODAY = date(2026, 11, 9)


@pytest.fixture
def live(tmp_path, respx_mock, monkeypatch):
    wait = NoWait()
    monkeypatch.setattr(filings_api, "_today", lambda: TODAY)
    noon = datetime(2026, 11, 9, 12, 0, tzinfo=timezone.utc)
    client = SecClient(FAKE_UA, clock=wait.clock, sleep=wait.sleep, wall_clock=lambda: noon)
    settings = Settings(
        data_mode="live", sec_user_agent=SecretStr(FAKE_UA), sec_cache_dir=tmp_path / "cache"
    )
    app = create_app(settings, sec_client=client)
    # Retrieval times (and so the window's reference day) come from this clock, not the real one.
    app.state.data = DataSource(settings, app.state.store, client, clock=lambda: noon)
    return TestClient(app)


@pytest.fixture
def respx_mock():
    with respx.mock(assert_all_called=False, assert_all_mocked=True) as router:
        yield router


def mock_submissions(router, data=None):
    return router.get(submissions_url(EXAMPLE)).mock(
        return_value=httpx.Response(200, json=data or EXAMPLE_SUBMISSIONS)
    )


# ------------------------------------------------- demo: authentic fixtures


def test_ac1_apple_latest_in_snapshot(demo) -> None:
    body = demo.get(f"/api/companies/{APPLE}/filings").json()
    latest = body["latest"]
    assert latest["label"] == "Latest in snapshot (as of 2026-11-03)"
    assert latest["annual"]["form"] == "10-K"
    assert latest["annual"]["accession"] == APPLE_10K
    assert latest["annual"]["filing_date"] == "2026-11-03"
    assert latest["annual"]["report_date"] == "2026-09-26"
    assert latest["annual"]["document_in_snapshot"] is True
    assert latest["quarterly"]["form"] == "10-Q"
    assert latest["quarterly"]["accession"] == APPLE_10Q
    assert latest["annual_amended_by"] is None
    assert body["source"]["label"].startswith("RECORDED SEC DEMO")


def test_ac2_history_only_four_forms_ten_years_newest_first(demo) -> None:
    body = demo.get(f"/api/companies/{APPLE}/filings").json()
    rows = body["history"]
    assert {row["form"] for row in rows} <= {"10-K", "10-K/A", "10-Q", "10-Q/A"}
    dates = [row["filing_date"] for row in rows]
    assert dates == sorted(dates, reverse=True)
    assert min(dates) >= "2016-11-03"
    assert body["coverage"]["note"] == "History limited to the recorded snapshot"
    assert body["coverage"]["complete"] is False


@pytest.mark.parametrize("cik", [APPLE, "0000789019", ALPHABET])
def test_every_demo_company_has_a_readable_latest_report(demo, cik) -> None:
    latest = demo.get(f"/api/companies/{cik}/filings").json()["latest"]
    for filing in (latest["annual"], latest["quarterly"]):
        assert filing["is_amendment"] is False
        response = demo.get(f"/api/companies/{cik}/filings/{filing['accession']}")
        assert response.status_code == 200
        body = response.json()
        assert body["section_status"] == "detected"
        assert body["note"] == "Sections detected automatically; may be imperfect"
        assert "Full primary document" in body["scope"]
        assert "Not necessarily the latest report on EDGAR" in body["scope"]
        assert body["source"]["mode"] == "demo"
        assert body["source_link"] == filing["document_url"]


def test_authentic_alphabet_amendment_is_labelled_and_not_the_latest(demo) -> None:
    # The snapshot's only amendment row: a real Alphabet 10-K/A, listed but not recorded in full.
    body = demo.get(f"/api/companies/{ALPHABET}/filings").json()
    amendments = [row for row in body["history"] if row["form"] == "10-K/A"]
    assert len(amendments) == 1 and amendments[0]["is_amendment"] is True
    assert amendments[0]["document_in_snapshot"] is False
    assert body["latest"]["annual"]["form"] == "10-K"
    response = demo.get(f"/api/companies/{ALPHABET}/filings/{amendments[0]['accession']}")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "document_not_in_snapshot"


def test_reader_gives_clean_text_and_real_sections(demo) -> None:
    body = demo.get(f"/api/companies/{APPLE}/filings/{APPLE_10K}").json()
    assert body["meta"]["accession"] == APPLE_10K
    assert body["source_link"] == APPLE_10K_URL
    ids = [section["id"] for section in body["sections"]]
    assert {"item1", "item1a", "item7", "item8"} <= set(ids)
    text = "\n".join(block["text"] for block in body["blocks"])
    assert "Apple Inc." in text
    for banned in ("<div", "<span", "<script", "ix:nonNumeric", "style="):
        assert banned not in text
    assert [block["id"] for block in body["blocks"]] == list(range(len(body["blocks"])))
    item7 = next(section for section in body["sections"] if section["id"] == "item7")
    heading = body["blocks"][item7["block_start"]]
    assert heading["kind"] == "heading" and heading["section_id"] == "item7"
    assert heading["text"].startswith("Item 7")


def test_document_not_in_snapshot_keeps_the_source_link(demo) -> None:
    old = next(
        row for row in demo.get(f"/api/companies/{APPLE}/filings").json()["history"]
        if not row["document_in_snapshot"]
    )
    response = demo.get(f"/api/companies/{APPLE}/filings/{old['accession']}")
    assert response.status_code == 404
    error = response.json()["error"]
    assert error["code"] == "document_not_in_snapshot"
    assert error["message"] == "This filing's document is not in the recorded demo snapshot"
    assert error["details"]["source_link"] == old["document_url"]


@pytest.mark.parametrize(
    "bad", ["..%2F..%2Fetc", "0000320193-25-00007", "not-an-accession", "..%5C..%5Cetc"]
)
def test_e5_invalid_accession_is_422(demo, bad) -> None:
    response = demo.get(f"/api/companies/{APPLE}/filings/{bad}")
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_accession"


def test_e5_newline_in_the_path_is_refused_by_the_router(demo) -> None:
    response = demo.get(f"/api/companies/{APPLE}/filings/a%0Ab")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"


def test_e5_unknown_accession_is_404(demo) -> None:
    response = demo.get(f"/api/companies/{APPLE}/filings/0000320193-20-999999")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "filing_not_found"


def test_another_companys_accession_is_not_accepted(demo) -> None:
    response = demo.get(f"/api/companies/0000789019/filings/{APPLE_10K}")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "filing_not_found"


def test_invalid_forms_cik_years_and_company(demo) -> None:
    bad_forms = demo.get(f"/api/companies/{APPLE}/filings", params={"forms": "8-K"})
    assert bad_forms.status_code == 422 and bad_forms.json()["error"]["code"] == "invalid_forms"
    assert demo.get("/api/companies/abc/filings").json()["error"]["code"] == "invalid_cik"
    assert demo.get(f"/api/companies/{APPLE}/filings", params={"years": 11}).status_code == 422
    missing = demo.get("/api/companies/1045810/filings")
    assert missing.status_code == 404 and missing.json()["error"]["code"] == "company_not_found"


def test_forms_filter_keeps_latest_untouched(demo) -> None:
    body = demo.get(f"/api/companies/{APPLE}/filings", params={"forms": "10-Q"}).json()
    assert {row["form"] for row in body["history"]} == {"10-Q"}
    assert body["latest"]["annual"]["form"] == "10-K"


def test_live_under_fixture_mode_is_refused(demo) -> None:
    assert demo.get(f"/api/companies/{APPLE}/filings", params={"source": "live"}).status_code == 409
    response = demo.get(f"/api/companies/{APPLE}/filings/{APPLE_10K}", params={"source": "live"})
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "live_disabled"


def test_demo_filing_access_uses_no_network(no_external_network) -> None:
    with respx.mock(assert_all_called=False, assert_all_mocked=True) as router:
        client = TestClient(create_app(Settings(data_mode="fixtures")))
        assert client.get(f"/api/companies/{APPLE}/filings").status_code == 200
        assert client.get(f"/api/companies/{APPLE}/filings/{APPLE_10K}").status_code == 200
        assert router.calls.call_count == 0


# ------------------------------------------------- live: SEC mocked, invented documents


def test_mocked_live_list_labels_and_amendments(live, respx_mock) -> None:
    mock_submissions(respx_mock)
    first = live.get(f"/api/companies/{EXAMPLE}/filings", params={"source": "live"}).json()
    assert first["latest"]["label"].startswith("Latest on EDGAR (retrieved ")
    assert first["source"]["mode"] == "live"
    assert first["latest"]["annual"]["accession"] == "0000000999-26-000002"
    assert first["latest"]["quarterly_amended_by"]["form"] == "10-Q/A"
    assert all(row["document_in_snapshot"] is None for row in first["history"])
    second = live.get(f"/api/companies/{EXAMPLE}/filings", params={"source": "live"}).json()
    assert second["latest"]["label"].startswith("Latest on EDGAR (cached, retrieved ")
    assert second["source"]["mode"] == "cached"


def test_mocked_live_reader_fetches_once_then_caches_permanently(live, respx_mock) -> None:
    mock_submissions(respx_mock)
    document = respx_mock.get(DOC_URL).mock(
        return_value=httpx.Response(200, content=(DOCS / "toc_and_body.html").read_bytes())
    )
    path = f"/api/companies/{EXAMPLE}/filings/0000000999-26-000002"
    first = live.get(path, params={"source": "live"}).json()
    assert first["source"]["mode"] == "live"
    assert first["source"]["label"].startswith("LIVE")
    assert first["section_status"] == "detected"
    assert "retrieved live" in first["scope"]
    assert first["source_link"] == DOC_URL
    second = live.get(path, params={"source": "live"}).json()
    assert second["source"]["mode"] == "cached"
    assert "cached copy retrieved" in second["scope"]
    assert second["document_retrieved_at"] == first["document_retrieved_at"]
    assert second["blocks"] == first["blocks"]
    assert document.call_count == 1
    assert document.calls[0].request.headers["User-Agent"] == FAKE_UA


def test_e5_unknown_accession_makes_no_document_request(live, respx_mock) -> None:
    mock_submissions(respx_mock)
    path = f"/api/companies/{EXAMPLE}/filings/0000000999-26-000099"
    response = live.get(path, params={"source": "live"})
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "filing_not_found"
    assert respx_mock.calls.call_count == 1  # only the company's own list


def test_e5_invalid_accession_makes_no_request_at_all(live, respx_mock) -> None:
    response = live.get(
        f"/api/companies/{EXAMPLE}/filings/..%2F..%2Fetc", params={"source": "live"}
    )
    assert response.status_code == 422
    assert respx_mock.calls.call_count == 0


def test_unsafe_primary_document_from_sec_is_never_requested(live, respx_mock) -> None:
    bad = {"filings": {"files": [], "recent": {
        "accessionNumber": ["0000000999-26-000002"], "filingDate": ["2026-01-15"],
        "reportDate": ["2025-12-31"], "form": ["10-K"], "primaryDocument": ["../../../evil.htm"],
    }}}
    mock_submissions(respx_mock, bad)
    response = live.get(
        f"/api/companies/{EXAMPLE}/filings/0000000999-26-000002", params={"source": "live"}
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "document_unavailable"
    assert respx_mock.calls.call_count == 1


def test_mocked_redirect_outside_the_allowlist_is_not_followed(live, respx_mock) -> None:
    mock_submissions(respx_mock)
    respx_mock.get(DOC_URL).mock(
        return_value=httpx.Response(302, headers={"Location": "https://attacker.invalid/x"})
    )
    response = live.get(
        f"/api/companies/{EXAMPLE}/filings/0000000999-26-000002", params={"source": "live"}
    )
    assert response.status_code == 502
    assert response.json()["error"]["code"] == "upstream_not_allowed"
    assert respx_mock.calls.call_count == 2


def test_mocked_redirect_to_another_archive_path_is_followed(live, respx_mock) -> None:
    mock_submissions(respx_mock)
    target = "https://www.sec.gov/Archives/edgar/data/999/000000099926000002/moved.htm"
    respx_mock.get(DOC_URL).mock(return_value=httpx.Response(301, headers={"Location": target}))
    respx_mock.get(target).mock(return_value=httpx.Response(200, content=b"<p>Moved text.</p>"))
    response = live.get(
        f"/api/companies/{EXAMPLE}/filings/0000000999-26-000002", params={"source": "live"}
    )
    assert response.status_code == 200
    assert response.json()["blocks"][0]["text"] == "Moved text."


def test_mocked_hostile_document_reaches_the_client_as_text_only(live, respx_mock) -> None:
    mock_submissions(respx_mock)
    respx_mock.get(DOC_URL).mock(
        return_value=httpx.Response(200, content=(DOCS / "hostile.html").read_bytes())
    )
    response = live.get(
        f"/api/companies/{EXAMPLE}/filings/0000000999-26-000002", params={"source": "live"}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["section_status"] == "not_detected"
    assert body["note"] == "Section boundaries not detected; showing full text"
    text = json.dumps(body["blocks"])
    for banned in ("<script", "onclick", "<iframe", "javascript:", "HIDDEN-XBRL-FACT"):
        assert banned not in text


def test_mocked_document_over_the_limit_is_413_and_not_cached(
    live, respx_mock, monkeypatch
) -> None:
    monkeypatch.setattr(source_module, "MAX_DOCUMENT_BYTES", 1000)
    mock_submissions(respx_mock)
    respx_mock.get(DOC_URL).mock(return_value=httpx.Response(200, content=b"x" * 5000))
    path = f"/api/companies/{EXAMPLE}/filings/0000000999-26-000002"
    response = live.get(path, params={"source": "live"})
    assert response.status_code == 413
    error = response.json()["error"]
    assert error["code"] == "document_too_large"
    assert error["details"]["source_link"] == DOC_URL
    respx_mock.get(DOC_URL).mock(return_value=httpx.Response(200, content=b"<p>small</p>"))
    assert live.get(path, params={"source": "live"}).status_code == 200


def test_mocked_size_limit_counts_decoded_bytes(live, respx_mock, monkeypatch) -> None:
    monkeypatch.setattr(source_module, "MAX_DOCUMENT_BYTES", 1000)
    mock_submissions(respx_mock)
    respx_mock.get(DOC_URL).mock(return_value=httpx.Response(
        200, content=gzip.compress(b"x" * 50_000), headers={"Content-Encoding": "gzip"}
    ))
    response = live.get(
        f"/api/companies/{EXAMPLE}/filings/0000000999-26-000002", params={"source": "live"}
    )
    assert response.status_code == 413


def test_mocked_gzip_document_is_decoded_once(live, respx_mock) -> None:
    mock_submissions(respx_mock)
    respx_mock.get(DOC_URL).mock(return_value=httpx.Response(
        200, content=gzip.compress(b"<p>Zipped text.</p>"), headers={"Content-Encoding": "gzip"}
    ))
    response = live.get(
        f"/api/companies/{EXAMPLE}/filings/0000000999-26-000002", params={"source": "live"}
    )
    assert response.json()["blocks"][0]["text"] == "Zipped text."


def test_mocked_missing_empty_and_non_text_documents(live, respx_mock) -> None:
    table = {"filings": {"files": [], "recent": {
        "accessionNumber": ["0000000999-26-000002", "0000000999-26-000003", "0000000999-26-000004"],
        "filingDate": ["2026-01-15"] * 3, "reportDate": ["2025-12-31"] * 3,
        "form": ["10-K", "10-Q", "10-Q"], "primaryDocument": ["xmpl-k.htm", "e.htm", "r.pdf"],
    }}}
    mock_submissions(respx_mock, table)
    respx_mock.get(DOC_URL).mock(return_value=httpx.Response(404))
    empty = "https://www.sec.gov/Archives/edgar/data/999/000000099926000003/e.htm"
    respx_mock.get(empty).mock(return_value=httpx.Response(200, content=b"<script>x</script>"))
    for accession in ("0000000999-26-000002", "0000000999-26-000003", "0000000999-26-000004"):
        response = live.get(
            f"/api/companies/{EXAMPLE}/filings/{accession}", params={"source": "live"}
        )
        assert response.status_code == 404
        assert response.json()["error"]["code"] == "document_unavailable"
    assert respx_mock.calls.call_count == 3  # the PDF was never requested


@pytest.mark.parametrize(
    ("status", "code", "http"),
    [(403, "sec_refused", 502), (500, "sec_unavailable", 502)],
)
def test_mocked_sec_failures_keep_their_codes(live, respx_mock, status, code, http) -> None:
    mock_submissions(respx_mock)
    route = respx_mock.get(DOC_URL).mock(return_value=httpx.Response(status))
    response = live.get(
        f"/api/companies/{EXAMPLE}/filings/0000000999-26-000002", params={"source": "live"}
    )
    assert response.status_code == http
    assert response.json()["error"]["code"] == code
    assert route.call_count == 1


def test_mocked_timeout_is_reported_not_replaced_with_demo_data(live, respx_mock) -> None:
    mock_submissions(respx_mock)
    respx_mock.get(DOC_URL).mock(side_effect=httpx.ReadTimeout("slow"))
    response = live.get(
        f"/api/companies/{EXAMPLE}/filings/0000000999-26-000002", params={"source": "live"}
    )
    assert response.status_code == 502
    assert response.json()["error"]["code"] == "sec_unavailable"


def test_mocked_older_page_read_only_when_needed(live, respx_mock) -> None:
    near = {"filings": {
        "files": [{"name": f"CIK{EXAMPLE}-submissions-001.json", "filingFrom": "2015-01-01",
                   "filingTo": "2020-12-31"}],
        "recent": {"accessionNumber": ["0000000999-26-000002"], "filingDate": ["2026-01-15"],
                   "reportDate": ["2025-12-31"], "form": ["10-K"],
                   "primaryDocument": ["xmpl-k.htm"]},
    }}
    mock_submissions(respx_mock, near)
    page_url = f"https://data.sec.gov/submissions/CIK{EXAMPLE}-submissions-001.json"
    page = respx_mock.get(page_url).mock(return_value=httpx.Response(200, json={
        "accessionNumber": ["0000000999-20-000001"], "filingDate": ["2020-02-01"],
        "reportDate": ["2019-12-31"], "form": ["10-K/A"], "primaryDocument": ["o.htm"],
    }))
    body = live.get(f"/api/companies/{EXAMPLE}/filings", params={"source": "live"}).json()
    assert page.call_count == 1
    assert [row["form"] for row in body["history"]] == ["10-K", "10-K/A"]
    assert body["coverage"]["complete"] is True


def test_mocked_older_page_gone_is_stated_in_the_coverage(live, respx_mock) -> None:
    near = {"filings": {
        "files": [{"name": f"CIK{EXAMPLE}-submissions-001.json", "filingFrom": "2015-01-01",
                   "filingTo": "2020-12-31"}],
        "recent": {"accessionNumber": ["0000000999-26-000002"], "filingDate": ["2026-01-15"],
                   "reportDate": ["2025-12-31"], "form": ["10-K"],
                   "primaryDocument": ["xmpl-k.htm"]},
    }}
    mock_submissions(respx_mock, near)
    respx_mock.get(f"https://data.sec.gov/submissions/CIK{EXAMPLE}-submissions-001.json").mock(
        return_value=httpx.Response(404)
    )
    body = live.get(f"/api/companies/{EXAMPLE}/filings", params={"source": "live"}).json()
    assert body["coverage"]["complete"] is False
    assert "older filing pages" in body["coverage"]["note"]


def test_mocked_older_page_name_from_sec_cannot_escape_the_allowlist(live, respx_mock) -> None:
    bad = {"filings": {
        "files": [{"name": "../../evil.json", "filingFrom": "2015-01-01",
                   "filingTo": "2020-12-31"}],
        "recent": {"accessionNumber": ["0000000999-26-000002"], "filingDate": ["2026-01-15"],
                   "reportDate": ["2025-12-31"], "form": ["10-K"],
                   "primaryDocument": ["xmpl-k.htm"]},
    }}
    mock_submissions(respx_mock, bad)
    body = live.get(f"/api/companies/{EXAMPLE}/filings", params={"source": "live"}).json()
    assert respx_mock.calls.call_count == 1
    assert body["coverage"]["complete"] is False


def test_mocked_amended_original_links_both_ways(live, respx_mock) -> None:
    mock_submissions(respx_mock)
    url = "https://www.sec.gov/Archives/edgar/data/999/000000099926000005/xmpl-qa.htm"
    respx_mock.get(url).mock(return_value=httpx.Response(200, content=b"<p>Amended part.</p>"))
    body = live.get(
        f"/api/companies/{EXAMPLE}/filings/0000000999-26-000005", params={"source": "live"}
    ).json()
    assert body["meta"]["is_amendment"] is True
    assert body["amends"]["accession"] == "0000000999-26-000001"
    assert body["amended_by"] is None


def test_ac7_document_without_items_is_full_text_with_the_fallback_note(live, respx_mock) -> None:
    mock_submissions(respx_mock)
    respx_mock.get(DOC_URL).mock(
        return_value=httpx.Response(200, content=(DOCS / "no_items.html").read_bytes())
    )
    body = live.get(
        f"/api/companies/{EXAMPLE}/filings/0000000999-26-000002", params={"source": "live"}
    ).json()
    assert body["section_status"] == "not_detected"
    assert body["note"] == "Section boundaries not detected; showing full text"
    assert body["sections"] == []
    assert all(block["section_id"] is None for block in body["blocks"])
    assert len(body["blocks"]) >= 2


def test_api_years_parameter_narrows_the_window(demo) -> None:
    body = demo.get(f"/api/companies/{APPLE}/filings", params={"years": 3}).json()
    assert body["history"], "Apple has filings in the last three years of the snapshot"
    assert min(row["filing_date"] for row in body["history"]) >= "2023-11-03"
    full = demo.get(f"/api/companies/{APPLE}/filings").json()
    assert min(row["filing_date"] for row in full["history"]) < "2023-11-03"
