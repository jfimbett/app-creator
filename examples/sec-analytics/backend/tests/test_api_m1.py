"""M1 API: health, meta, search and profile over the recorded fixtures (M1-AC3, M1-AC4, M1-E2).

Expected profile values are read straight from the fixture submissions files, not from the app.
Overview expectations come from the hand-worked rows FX1-FX4 in milestones/acceptance.md.
"""

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.data.fixtures import FixtureStore
from app.main import create_app
from app.settings import Settings, SettingsError, load_settings

FIXTURES_DIR = Path(__file__).resolve().parents[2] / "fixtures"
APPLE, MICROSOFT, ALPHABET = "0000320193", "0000789019", "0001652044"
LABEL_PREFIX = "RECORDED SEC DEMO · snapshot "
UNIVERSE_NOTE = "Search covers the demo companies only: Apple, Microsoft, Alphabet"


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(create_app(), raise_server_exceptions=False)


def _manifest() -> dict:
    return json.loads((FIXTURES_DIR / "manifest.json").read_text(encoding="utf-8"))


def _submissions(cik: str) -> dict:
    path = FIXTURES_DIR / "submissions" / f"CIK{cik}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _assert_envelope(response, status: int, code: str) -> dict:
    assert response.status_code == status
    body = response.json()
    assert set(body) == {"error"}
    assert set(body["error"]) == {"code", "message", "details", "reference"}
    assert body["error"]["code"] == code
    assert body["error"]["message"]
    return body["error"]


# --- health and meta -------------------------------------------------------------------------


def test_health(client) -> None:
    assert client.get("/api/health").json() == {"status": "ok", "app": "SEC Analytics"}


def test_meta_reports_fixture_mode_and_snapshot(client) -> None:
    body = client.get("/api/meta").json()
    assert body["data_mode"] == "fixtures"
    assert body["live_available"] is False
    assert body["live_configured"] is False
    assert body["snapshot_date"] == _manifest()["snapshot_date"]
    assert body["demo_universe"] == [
        {"cik": APPLE, "ticker": "AAPL", "name": "Apple Inc."},
        {"cik": MICROSOFT, "ticker": "MSFT", "name": "MICROSOFT CORP"},
        {"cik": ALPHABET, "ticker": "GOOGL", "name": "Alphabet Inc."},
    ]


# --- search ----------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("query", "cik", "match"),
    [
        ("aapl", APPLE, "ticker"),
        ("320193", APPLE, "cik"),
        ("0000320193", APPLE, "cik"),
        ("Microsoft", MICROSOFT, "name"),
        ("GOOGL", ALPHABET, "ticker"),
    ],
)
def test_search_finds_exactly_the_company(client, query, cik, match) -> None:
    response = client.get("/api/companies/search", params={"q": query})
    assert response.status_code == 200
    body = response.json()
    assert body["query"] == query
    assert [(r["cik"], r["match"]) for r in body["results"]] == [(cik, match)]
    assert set(body["results"][0]) == {"cik", "ticker", "name", "match"}
    assert body["universe_note"] == UNIVERSE_NOTE


def test_search_miss_is_an_empty_list(client) -> None:
    body = client.get("/api/companies/search", params={"q": "tesla"}).json()
    assert body["results"] == []
    assert body["universe_note"] == UNIVERSE_NOTE


def test_search_query_is_trimmed(client) -> None:
    assert client.get("/api/companies/search", params={"q": "  aapl "}).json()["query"] == "aapl"


def test_search_source_lists_the_files_used(client) -> None:
    source = client.get("/api/companies/search", params={"q": "a"}).json()["source"]
    assert "https://www.sec.gov/files/company_tickers.json" in source["source_urls"]
    assert f"https://data.sec.gov/submissions/CIK{APPLE}.json" in source["source_urls"]


@pytest.mark.parametrize("query", ["", "   ", "x" * 101])
def test_search_rejects_empty_or_long_query(client, query) -> None:
    response = client.get("/api/companies/search", params={"q": query})
    _assert_envelope(response, 422, "invalid_query")


def test_search_accepts_100_characters(client) -> None:
    assert client.get("/api/companies/search", params={"q": "x" * 100}).status_code == 200


def test_search_without_q_is_invalid_query(client) -> None:
    _assert_envelope(client.get("/api/companies/search"), 422, "invalid_query")


@pytest.mark.parametrize("limit", ["0", "21", "ten"])
def test_search_rejects_bad_limit(client, limit) -> None:
    response = client.get("/api/companies/search", params={"q": "a", "limit": limit})
    _assert_envelope(response, 422, "invalid_query")


def test_search_limit_caps_results(client) -> None:
    body = client.get("/api/companies/search", params={"q": "a", "limit": 1}).json()
    assert len(body["results"]) == 1


# --- profile ---------------------------------------------------------------------------------


def _expected_profile(cik: str) -> dict:
    raw = _submissions(cik)

    def text(value):
        return value if value else None

    return {
        "cik": raw["cik"],
        "name": raw["name"],
        "tickers": raw["tickers"],
        "exchanges": raw["exchanges"],
        "sic": text(raw["sic"]),
        "sic_description": text(raw["sicDescription"]),
        "fiscal_year_end": text(raw["fiscalYearEnd"]),
        "state_of_incorporation": text(raw["stateOfIncorporation"]),
        "former_names": [
            {"name": f["name"], "from": f["from"], "to": f["to"]} for f in raw["formerNames"]
        ],
    }


@pytest.mark.parametrize("cik", [APPLE, MICROSOFT, ALPHABET])
def test_profile_equals_fixture_submissions(client, cik) -> None:
    body = client.get(f"/api/companies/{cik}").json()
    source = body.pop("source")
    assert body == _expected_profile(cik)
    assert source["source_urls"] == [f"https://data.sec.gov/submissions/CIK{cik}.json"]


def test_apple_profile_known_values(client) -> None:
    body = client.get("/api/companies/320193").json()
    assert body["cik"] == APPLE
    assert body["name"] == "Apple Inc."
    assert body["tickers"] == ["AAPL"]
    assert body["exchanges"] == ["Nasdaq"]
    assert (body["sic"], body["sic_description"]) == ("3571", "Electronic Computers")
    assert body["fiscal_year_end"] == "0926"
    assert body["state_of_incorporation"] == "CA"
    assert body["former_names"][0]["name"] == "APPLE INC"
    assert "description" not in body


@pytest.mark.parametrize("cik", ["320193", "CIK320193", "cik0000320193"])
def test_profile_accepts_any_padding_and_prefix(client, cik) -> None:
    assert client.get(f"/api/companies/{cik}").json()["cik"] == APPLE


@pytest.mark.parametrize("cik", ["abc", "12345678901", "-1", "12a"])
def test_profile_rejects_invalid_cik(client, cik) -> None:
    error = _assert_envelope(client.get(f"/api/companies/{cik}"), 422, "invalid_cik")
    assert error["message"] == "A CIK has up to 10 digits"


def test_profile_outside_demo_snapshot_is_404(client) -> None:
    error = _assert_envelope(client.get("/api/companies/1318605"), 404, "company_not_found")
    assert "not in the demo snapshot" in error["message"]
    assert error["details"] == {"cik": "0001318605"}


# --- overview (M1-AC5) -----------------------------------------------------------------------


def _companyfacts_url(cik: str) -> str:
    return f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"


def test_overview_shape_and_apple_known_answers(client) -> None:
    response = client.get(f"/api/companies/{APPLE}/overview")
    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"cik", "key_figures", "chart", "notes", "source"}
    assert body["cik"] == APPLE
    figures = {m["metric_id"]: m for m in body["key_figures"]}
    assert set(figures) == {"revenue", "net_income"}
    # FX1 and FX2 (acceptance.md): whole USD, not millions.
    assert figures["revenue"]["value"] == 478834000000
    assert figures["net_income"]["value"] == 132175000000
    for figure in figures.values():
        assert (figure["unit"], figure["kind"], figure["status"]) == ("USD", "reported", "ok")
        assert (figure["fiscal_year_label"], figure["period_end"]) == ("FY2026", "2026-09-26")
        assert figure["provenance"]["accession"] == "0000320193-26-000026"
        assert figure["provenance"]["source_url"] == _companyfacts_url(APPLE)
    assert "Values may reflect later restatements; not point-in-time." in body["notes"]
    assert body["source"]["source_urls"] == [_companyfacts_url(APPLE)]


def test_overview_microsoft_known_answers(client) -> None:
    body = client.get("/api/companies/789019/overview").json()
    figures = {m["metric_id"]: m for m in body["key_figures"]}
    assert figures["revenue"]["value"] == 331839000000  # FX3
    assert figures["net_income"]["value"] == 133749000000  # FX4
    assert figures["net_income"]["provenance"]["accession"] == "0001193125-26-323660"


@pytest.mark.parametrize("cik", [APPLE, MICROSOFT, ALPHABET])
def test_overview_has_at_least_five_annual_periods(client, cik) -> None:
    chart = client.get(f"/api/companies/{cik}/overview").json()["chart"]
    assert len(chart) >= 5
    for row in chart:
        assert set(row) == {"fiscal_year_label", "period_end", "revenue", "net_income"}
        assert row["fiscal_year_label"] == f"FY{row['period_end'][:4]}"


def test_overview_years_limits_the_chart(client) -> None:
    body = client.get(f"/api/companies/{APPLE}/overview", params={"years": 5}).json()
    assert [r["period_end"] for r in body["chart"]][-1] == "2026-09-26"
    assert len(body["chart"]) == 5


@pytest.mark.parametrize("years", ["0", "21", "five"])
def test_overview_rejects_bad_years(client, years) -> None:
    response = client.get(f"/api/companies/{APPLE}/overview", params={"years": years})
    error = _assert_envelope(response, 422, "invalid_request")
    assert error["details"] == {"parameters": ["years"]}


def test_overview_invalid_cik(client) -> None:
    error = _assert_envelope(client.get("/api/companies/abc/overview"), 422, "invalid_cik")
    assert error["message"] == "A CIK has up to 10 digits"


def test_overview_outside_demo_snapshot_is_404(client) -> None:
    error = _assert_envelope(
        client.get("/api/companies/1318605/overview"), 404, "company_not_found"
    )
    assert "not in the demo snapshot" in error["message"]


# --- errors and labels -----------------------------------------------------------------------


def test_unknown_route_uses_envelope(client) -> None:
    _assert_envelope(client.get("/api/does-not-exist"), 404, "not_found")


def test_wrong_method_uses_envelope(client) -> None:
    _assert_envelope(client.post("/api/meta"), 405, "method_not_allowed")


def test_unexpected_exception_is_generic_500() -> None:
    app = create_app()

    @app.get("/api/boom")
    def boom() -> None:
        raise RuntimeError("secret detail /Users/someone/private/path")

    response = TestClient(app, raise_server_exceptions=False).get("/api/boom")
    error = _assert_envelope(response, 500, "internal_error")
    assert error["reference"]
    assert "secret detail" not in response.text
    assert "Traceback" not in response.text
    assert "/Users/" not in response.text


@pytest.mark.parametrize(
    ("path", "params"),
    [
        ("/api/companies/search", {"q": "aapl"}),
        ("/api/companies/search", {"q": "tesla"}),
        (f"/api/companies/{APPLE}", None),
        (f"/api/companies/{ALPHABET}", None),
        (f"/api/companies/{APPLE}/overview", None),
        (f"/api/companies/{ALPHABET}/overview", {"years": 3}),
    ],
)
def test_every_source_label_is_recorded_sec_demo(client, path, params) -> None:
    source = client.get(path, params=params).json()["source"]
    snapshot = _manifest()["snapshot_date"]
    assert source["label"].startswith(LABEL_PREFIX)
    assert source["label"] == LABEL_PREFIX + snapshot
    assert source["mode"] == "demo"
    assert source["retrieved_at"] is None
    assert source["snapshot_date"] == snapshot


# --- settings and synthetic labelling --------------------------------------------------------


def test_settings_default_to_fixtures() -> None:
    settings = load_settings({})
    assert settings.data_mode == "fixtures"
    assert settings.fixtures_dir == FIXTURES_DIR


@pytest.mark.parametrize("mode", ["live", "cached", "FIXTURES "])
def test_settings_refuse_other_modes_naming_the_setting(mode) -> None:
    with pytest.raises(SettingsError, match="DATA_MODE"):
        load_settings({"DATA_MODE": mode})


def test_create_app_fails_on_missing_fixtures(tmp_path) -> None:
    settings = Settings(data_mode="fixtures", fixtures_dir=tmp_path / "nowhere")
    with pytest.raises(SettingsError, match="FIXTURES_DIR"):
        create_app(settings)


def _write_synthetic_tree(root: Path) -> None:
    """A minimal SYNTHETIC fixtures tree (invented for this test, never SEC data)."""
    (root / "submissions").mkdir(parents=True)
    marker = "SYNTHETIC: invented for tests, not SEC data"
    manifest = {
        "_synthetic": marker,
        "schema_version": 1,
        "label": "RECORDED SEC DEMO",  # deliberately wrong: synthetic must still win
        "synthetic": True,
        "snapshot_date": "2000-01-01",
        "files": [
            {"path": "company_tickers.json", "kind": "company_tickers",
             "source_url": "https://www.sec.gov/files/company_tickers.json"},
            {"path": "submissions/CIK0000000001.json", "kind": "submissions",
             "cik": "0000000001",
             "source_url": "https://data.sec.gov/submissions/CIK0000000001.json"},
        ],
    }
    tickers = {"_synthetic": marker, "0": {"cik_str": 1, "ticker": "TEST", "title": "Test Co"}}
    submissions = {"_synthetic": marker, "cik": "0000000001", "name": "Test Co",
                   "tickers": ["TEST"], "exchanges": [], "sic": "", "sicDescription": "",
                   "fiscalYearEnd": "", "stateOfIncorporation": "", "formerNames": []}
    for name, content in [("manifest.json", manifest), ("company_tickers.json", tickers),
                          ("submissions/CIK0000000001.json", submissions)]:
        (root / name).write_text(json.dumps(content), encoding="utf-8")


def test_synthetic_manifest_is_never_labelled_sec_data(tmp_path) -> None:
    _write_synthetic_tree(tmp_path)
    store = FixtureStore(tmp_path)
    assert store.synthetic is True
    assert store.source_info([]).label == "SYNTHETIC TEST DATA · snapshot 2000-01-01"

    client = TestClient(create_app(Settings(data_mode="fixtures", fixtures_dir=tmp_path)))
    body = client.get("/api/companies/1").json()
    assert body["source"]["label"].startswith("SYNTHETIC TEST DATA")
    assert body["sic"] is None  # empty SEC text is "not reported", never invented
    assert body["fiscal_year_end"] is None
