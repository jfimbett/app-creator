"""M2 API: catalog, statements, explorer series, live mode and its failures (offline, respx)."""

import json
from pathlib import Path

import httpx
import pytest
import respx
from fastapi.testclient import TestClient
from pydantic import SecretStr

from app.clients.sec import COMPANY_TICKERS_URL, SecClient, companyfacts_url, submissions_url
from app.main import create_app
from app.settings import Settings, SettingsError, load_settings

APPLE = "0000320193"
NVDA_CIK = "0001045810"
FAKE_UA = "SEC Analytics tests " + "tests" + "@" + "sec-analytics.invalid"
NOT_CONFIGURED = (
    "Live SEC data is not configured: set SEC_USER_AGENT (see .env.example and docs/SETUP.md)"
)
RESTATEMENT = "Values may reflect later restatements; not point-in-time."
EXAMPLE = json.loads(
    (Path(__file__).parent / "synthetic" / "example_co.json").read_text(encoding="utf-8")
)


class NoWait:
    def __init__(self) -> None:
        self.now = 0.0

    def clock(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        self.now += seconds


@pytest.fixture(scope="module")
def demo() -> TestClient:
    return TestClient(create_app(), raise_server_exceptions=False)


@pytest.fixture
def live(tmp_path: Path) -> TestClient:
    wait = NoWait()
    settings = Settings(data_mode="live", sec_user_agent=SecretStr(FAKE_UA), sec_cache_dir=tmp_path)
    client = SecClient(FAKE_UA, clock=wait.clock, sleep=wait.sleep)
    return TestClient(create_app(settings, client), raise_server_exceptions=False)


def _error(response, status: int, code: str) -> dict:
    assert response.status_code == status
    body = response.json()["error"]
    assert body["code"] == code
    return body


def test_catalog_lists_every_metric_with_formula_or_concepts(demo: TestClient) -> None:
    metrics = {m["id"]: m for m in demo.get("/api/metrics").json()["metrics"]}
    assert set(metrics) >= {
        "revenue", "revenue_growth", "operating_income", "operating_margin", "net_income",
        "net_margin", "income_tax", "interest_expense", "ebit", "ebitda", "d_and_a",
        "operating_cash_flow", "capex", "fcf", "fcf_margin", "assets", "assets_current",
        "liabilities", "liabilities_current", "equity", "debt", "working_capital",
        "debt_to_equity", "roe", "roa",
    }  # fmt: skip
    assert metrics["net_margin"]["formula"] == "net income ÷ revenue"
    assert metrics["net_margin"]["unit_kind"] == "percent"
    assert metrics["debt_to_equity"]["unit_kind"] == "ratio"
    assert metrics["fcf"]["unit_kind"] == "currency"
    assert metrics["revenue"]["kind"] == "reported"
    assert metrics["revenue"]["concepts"][0] == "Revenues"
    assert not {"pe_ratio", "market_cap", "ev_ebitda"} & set(metrics)


def test_m2_ac4_financials_for_apple_in_demo(demo: TestClient) -> None:
    response = demo.get(f"/api/companies/{APPLE}/financials")
    assert response.status_code == 200
    body = response.json()
    assert len(body["periods"]) == 10
    assert body["currency"] == "USD"
    assert body["fiscal_year_end"] == "0926"
    assert RESTATEMENT in body["notes"]
    assert body["periods"][-1] == {
        "fiscal_year_label": "FY2026", "start": "2025-09-28", "end": "2026-09-26",
    }  # fmt: skip
    assert body["source"]["label"].startswith("RECORDED SEC DEMO · snapshot ")
    lines = [*body["statements"]["income"], *body["statements"]["balance"],
             *body["statements"]["cash_flow"], *body["ratios"]]  # fmt: skip
    for line in lines:
        assert len(line["values"]) == 10
        for value in line["values"]:
            assert (value["value"] is None) == (value["status"] != "ok")
            if value["status"] == "ok" and value["kind"] == "reported":
                assert value["provenance"]["source_url"] == companyfacts_url(APPLE)
            if value["kind"] == "derived":
                assert value["formula"] and value["inputs"]
            if value["status"] != "ok":
                assert value["reason"]


def test_m2_ac6_reported_value_has_full_provenance(demo: TestClient) -> None:
    income = demo.get(f"/api/companies/{APPLE}/financials").json()["statements"]["income"]
    revenue = next(line for line in income if line["metric_id"] == "revenue")
    provenance = revenue["values"][-1]["provenance"]
    # FX1 in milestones/acceptance.md.
    assert provenance == {
        "concept": "RevenueFromContractWithCustomerExcludingAssessedTax",
        "taxonomy": "us-gaap",
        "unit": "USD",
        "start": "2025-09-28",
        "end": "2026-09-26",
        "form": "10-K",
        "accession": "0000320193-26-000026",
        "filed": "2026-11-03",
        "fy": 2026,
        "fp": "FY",
        "source_url": companyfacts_url(APPLE),
    }


def test_years_selects_the_latest_periods(demo: TestClient) -> None:
    body = demo.get(f"/api/companies/{APPLE}/financials", params={"years": 5}).json()
    assert [p["fiscal_year_label"] for p in body["periods"]] == [
        "FY2022", "FY2023", "FY2024", "FY2025", "FY2026",
    ]  # fmt: skip
    growth = next(line for line in body["ratios"] if line["metric_id"] == "revenue_growth")
    # The first shown year still compares with its prior year, outside the shown range.
    assert growth["values"][0]["status"] == "ok"


@pytest.mark.parametrize("years", [4, 11, "ten"])
def test_invalid_years(demo: TestClient, years) -> None:
    response = demo.get(f"/api/companies/{APPLE}/financials", params={"years": years})
    _error(response, 422, "invalid_years")
    response = demo.get(
        f"/api/companies/{APPLE}/metrics", params={"ids": "revenue", "years": years}
    )
    _error(response, 422, "invalid_years")


def test_metric_series_for_the_explorer(demo: TestClient) -> None:
    response = demo.get(f"/api/companies/{APPLE}/metrics", params={"ids": "net_margin,fcf"})
    assert response.status_code == 200
    series = {s["metric_id"]: s for s in response.json()["series"]}
    assert series["net_margin"]["unit"] == "percent"
    assert series["fcf"]["unit"] == "USD"
    assert series["net_margin"]["formula"] == "net income ÷ revenue"
    assert len(series["fcf"]["points"]) == 10
    # FX6 in milestones/acceptance.md.
    assert series["fcf"]["points"][-1]["value"] == 136_056_000_000


def test_metric_series_rejects_unknown_and_too_many(demo: TestClient) -> None:
    url = f"/api/companies/{APPLE}/metrics"
    _error(demo.get(url, params={"ids": "revenue,pe_ratio"}), 422, "unknown_metric")
    too_many = "revenue,fcf,roe,roa,debt,ebit,ebitda"
    _error(demo.get(url, params={"ids": too_many}), 422, "invalid_request")


def test_overview_key_figures_grow_with_badges_data(demo: TestClient) -> None:
    body = demo.get(f"/api/companies/{APPLE}/overview").json()
    figures = {m["metric_id"]: m for m in body["key_figures"]}
    assert set(figures) == {
        "revenue", "revenue_growth", "net_income", "net_margin", "operating_cash_flow", "fcf",
        "debt_to_equity",
    }  # fmt: skip
    assert figures["net_income"]["kind"] == "reported"
    assert figures["fcf"]["kind"] == "derived"


def test_demo_outside_the_snapshot_is_not_found(demo: TestClient) -> None:
    _error(demo.get("/api/companies/1045810/financials"), 404, "company_not_found")


def test_live_is_refused_under_fixture_mode(demo: TestClient) -> None:
    _error(demo.get("/api/companies/search", params={"q": "aapl", "source": "live"}), 409,
           "live_disabled")  # fmt: skip
    _error(demo.get(f"/api/companies/{APPLE}/financials", params={"source": "live"}), 409,
           "live_disabled")  # fmt: skip


def test_invalid_source_is_rejected(demo: TestClient) -> None:
    _error(demo.get(f"/api/companies/{APPLE}", params={"source": "x"}), 422, "invalid_request")


def test_meta_reports_live_state(demo: TestClient, live: TestClient, tmp_path: Path) -> None:
    assert demo.get("/api/meta").json()["live_available"] is False
    meta = live.get("/api/meta").json()
    assert (meta["data_mode"], meta["live_available"], meta["live_configured"]) == (
        "live", True, True,
    )  # fmt: skip
    assert FAKE_UA not in json.dumps(meta)
    unconfigured = TestClient(
        create_app(Settings(data_mode="live", sec_cache_dir=tmp_path)),
        raise_server_exceptions=False,
    )
    assert unconfigured.get("/api/meta").json()["live_configured"] is False


TICKERS = {
    "0": {"cik_str": 1045810, "ticker": "NVDA", "title": "NVIDIA CORP"},
    "1": {"cik_str": 1652044, "ticker": "GOOGL", "title": "Alphabet Inc."},
    "2": {"cik_str": 1652044, "ticker": "GOOG", "title": "Alphabet Inc."},
}


@respx.mock
def test_m2_ac1_live_search_uses_the_ticker_file_and_is_labelled_live(live: TestClient) -> None:
    respx.get(COMPANY_TICKERS_URL).mock(return_value=httpx.Response(200, json=TICKERS))
    response = live.get("/api/companies/search", params={"q": "NVDA", "source": "live"})
    assert response.status_code == 200
    body = response.json()
    assert body["results"] == [
        {"cik": NVDA_CIK, "ticker": "NVDA", "name": "NVIDIA CORP", "match": "ticker"}
    ]
    assert body["source"]["mode"] == "live"
    assert body["source"]["label"].startswith("LIVE · retrieved ")
    assert body["universe_note"] == (
        "Live search covers SEC filers listed in the SEC ticker file; "
        "other filers can be opened by CIK."
    )
    assert body["source"]["source_urls"] == [COMPANY_TICKERS_URL]


@respx.mock
def test_live_search_by_name_and_cik_one_result_per_company(live: TestClient) -> None:
    respx.get(COMPANY_TICKERS_URL).mock(return_value=httpx.Response(200, json=TICKERS))
    by_name = live.get("/api/companies/search", params={"q": "alphabet", "source": "live"}).json()
    assert [r["cik"] for r in by_name["results"]] == ["0001652044"]
    by_cik = live.get("/api/companies/search", params={"q": "1045810", "source": "live"}).json()
    assert by_cik["results"][0]["match"] == "cik"
    assert by_cik["source"]["mode"] == "cached"


@respx.mock
def test_a_cik_outside_the_ticker_file_can_still_be_opened(live: TestClient) -> None:
    respx.get(COMPANY_TICKERS_URL).mock(return_value=httpx.Response(200, json=TICKERS))
    body = live.get("/api/companies/search", params={"q": "42", "source": "live"}).json()
    assert body["results"][0]["cik"] == "0000000042"
    assert body["results"][0]["ticker"] == ""
    assert "open by CIK" in body["results"][0]["name"]
    none = live.get("/api/companies/search", params={"q": "zzzz", "source": "live"}).json()
    assert none["results"] == []


def test_m2_ac2_live_without_the_setting_names_it(tmp_path: Path) -> None:
    client = TestClient(
        create_app(Settings(data_mode="live", sec_cache_dir=tmp_path)),
        raise_server_exceptions=False,
    )
    body = _error(
        client.get("/api/companies/search", params={"q": "a", "source": "live"}),
        503,
        "sec_contact_not_configured",
    )
    assert body["message"] == NOT_CONFIGURED
    assert client.get("/api/companies/search", params={"q": "aapl"}).status_code == 200


@respx.mock
@pytest.mark.parametrize(
    "failure",
    [httpx.Response(503), httpx.ReadTimeout("slow")],
    ids=["503", "timeout"],
)
def test_m2_ac3_sec_failure_is_reported_and_never_replaced_by_demo_data(
    live: TestClient, failure
) -> None:
    route = respx.get(companyfacts_url(APPLE))
    if isinstance(failure, Exception):
        route.mock(side_effect=failure)
    else:
        route.mock(return_value=failure)
    body = _error(
        live.get(f"/api/companies/{APPLE}/overview", params={"source": "live"}),
        502,
        "sec_unavailable",
    )
    assert body["message"] == "SEC is unavailable right now"


@respx.mock
def test_rate_limit_and_refusal_messages(live: TestClient) -> None:
    respx.get(submissions_url(APPLE)).mock(
        return_value=httpx.Response(429, headers={"Retry-After": "7"})
    )
    body = _error(live.get(f"/api/companies/{APPLE}", params={"source": "live"}), 503,
                  "sec_rate_limited")  # fmt: skip
    assert body["details"]["retry_after"] == 7
    assert body["message"] == "SEC is limiting requests; try again in 7 s"
    respx.get(submissions_url("1")).mock(return_value=httpx.Response(403))
    body = _error(live.get("/api/companies/1", params={"source": "live"}), 502, "sec_refused")
    assert body["message"] == (
        "SEC refused the request (403). The app does not retry refused requests."
    )


@respx.mock
def test_m2_e13_redirect_out_of_the_allowlist_maps_to_502(live: TestClient) -> None:
    respx.get(submissions_url(APPLE)).mock(
        return_value=httpx.Response(302, headers={"Location": "https://example.com/"})
    )
    _error(live.get(f"/api/companies/{APPLE}", params={"source": "live"}), 502,
           "upstream_not_allowed")  # fmt: skip


@respx.mock
def test_live_unknown_filer_and_no_company_facts(live: TestClient) -> None:
    respx.get(submissions_url("2")).mock(return_value=httpx.Response(404))
    _error(live.get("/api/companies/2", params={"source": "live"}), 404, "company_not_found")
    respx.get(companyfacts_url("3")).mock(return_value=httpx.Response(404))
    body = _error(live.get("/api/companies/3/overview", params={"source": "live"}), 404,
                  "company_not_found")  # fmt: skip
    assert "Company Facts" in body["message"]


def _without_fy2024_revenue() -> dict:
    document = json.loads(json.dumps(EXAMPLE))
    gaap = document["facts"]["us-gaap"]
    gaap["NetIncomeLoss"]["units"]["USD"].insert(
        0,
        {"start": "2024-01-01", "end": "2024-12-31", "val": 90, "accn": "0000000001-25-000001",
         "fy": 2024, "fp": "FY", "form": "10-K", "filed": "2025-02-01"},
    )  # fmt: skip
    gaap["Revenues"]["units"]["USD"] = gaap["Revenues"]["units"]["USD"][1:]
    return document


@respx.mock
def test_m2_ac8_period_without_revenue_over_a_mocked_sec(live: TestClient) -> None:
    respx.get(companyfacts_url("1")).mock(
        return_value=httpx.Response(200, json=_without_fy2024_revenue())
    )
    respx.get(submissions_url("1")).mock(
        return_value=httpx.Response(200, json={"name": "SYNTHETIC", "fiscalYearEnd": "1231"})
    )
    body = live.get("/api/companies/1/financials", params={"source": "live"}).json()
    # Five years requested at most; this company has two.
    assert [p["fiscal_year_label"] for p in body["periods"]] == ["FY2024", "FY2025"]
    assert body["source"]["label"].startswith("LIVE · retrieved ")
    income = {line["metric_id"]: line for line in body["statements"]["income"]}
    missing = income["revenue"]["values"][0]
    assert (missing["status"], missing["value"]) == ("missing", None)
    assert missing["reason"] == "no mapped revenue concept"
    ratios = {line["metric_id"]: line for line in body["ratios"]}
    margin = ratios["net_margin"]["values"][0]
    assert (margin["status"], margin["value"]) == ("unavailable", None)


@respx.mock
def test_combined_source_shows_cached_when_any_part_is_cached(live: TestClient) -> None:
    respx.get(companyfacts_url("1")).mock(return_value=httpx.Response(200, json=EXAMPLE))
    respx.get(submissions_url("1")).mock(return_value=httpx.Response(200, json={"name": "S"}))
    live.get("/api/companies/1", params={"source": "live"})
    body = live.get("/api/companies/1/financials", params={"source": "live"}).json()
    assert body["source"]["mode"] == "cached"
    assert body["source"]["label"].startswith("CACHED · retrieved ")
    assert len(body["source"]["source_urls"]) == 2


def test_settings_accept_live_and_refuse_a_high_rate(tmp_path: Path) -> None:
    settings = load_settings({"DATA_MODE": "live", "SEC_CACHE_DIR": str(tmp_path)})
    assert settings.live_available and not settings.live_configured
    assert load_settings({"SEC_MAX_REQUESTS_PER_SECOND": "5"}).sec_max_requests_per_second == 5
    for bad in ("6", "0", "fast"):
        with pytest.raises(SettingsError, match="SEC_MAX_REQUESTS_PER_SECOND"):
            load_settings({"SEC_MAX_REQUESTS_PER_SECOND": bad})


def test_the_contact_never_appears_in_settings_output() -> None:
    settings = load_settings({"DATA_MODE": "live", "SEC_USER_AGENT": FAKE_UA})
    assert settings.live_configured
    assert FAKE_UA not in repr(settings)
    assert FAKE_UA not in settings.model_dump_json()


@respx.mock
def test_a_filer_with_no_annual_10k_revenue_gets_an_explanation_not_an_error(
    live: TestClient,
) -> None:
    """Found on live data: a foreign filer (20-F) caused a 500."""
    no_10k = {"facts": {"us-gaap": {"Revenues": {"units": {"USD": [
        {"start": "2024-01-01", "end": "2024-12-31", "val": 5, "accn": "0000000009-25-000001",
         "fy": 2024, "fp": "FY", "form": "20-F", "filed": "2025-03-01"},
    ]}}}}}  # fmt: skip
    respx.get(companyfacts_url("9")).mock(return_value=httpx.Response(200, json=no_10k))
    respx.get(submissions_url("9")).mock(
        return_value=httpx.Response(200, json={"name": "SYNTHETIC FOREIGN FILER"})
    )
    response = live.get("/api/companies/9/financials", params={"source": "live"})
    assert response.status_code == 200
    body = response.json()
    assert body["periods"] == []
    assert body["currency"] is None
    assert body["notes"] == ["No annual 10-K revenue in a currency unit was found."]
    assert body["statements"]["income"][0]["values"] == []
    series = live.get(
        "/api/companies/9/metrics", params={"ids": "revenue,net_margin", "source": "live"}
    )
    assert series.status_code == 200
    assert series.json()["series"][0]["points"] == []
