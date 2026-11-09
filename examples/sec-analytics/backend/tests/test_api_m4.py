"""M4 API: /api/compare and /api/compare.csv in demo (authentic fixtures) and live (SEC mocked).

The live tests serve the recorded fixture JSON through a fake SEC (respx), so they show this app's
throttling, caching and labelling, never SEC's real answers. No test here reaches the network.
"""

import csv
import io
import json
from pathlib import Path

import httpx
import pytest
import respx
from fastapi.testclient import TestClient
from pydantic import SecretStr

from app.api import compare as compare_api
from app.clients.sec import SecClient, companyfacts_url, submissions_url
from app.logic.csv_export import HEADER
from app.main import create_app
from app.settings import Settings

APPLE, MICROSOFT, ALPHABET = "0000320193", "0000789019", "0001652044"
DEMO = f"{APPLE},{MICROSOFT},{ALPHABET}"
FIXTURES = Path(__file__).resolve().parents[2] / "fixtures"
FAKE_UA = "SEC Analytics tests " + "tests" + "@" + "sec-analytics.invalid"


class NoWait:
    def __init__(self) -> None:
        self.now = 0.0
        self.slept = 0.0

    def clock(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        self.now += seconds
        self.slept += seconds


@pytest.fixture(scope="module")
def demo() -> TestClient:
    return TestClient(create_app(Settings(data_mode="fixtures")))


def error(response, status: int, code: str) -> dict:
    assert response.status_code == status, response.text
    body = response.json()["error"]
    assert body["code"] == code
    return body


# ------------------------------------------------------------------ demo: authentic fixtures


def test_m4_ac1_three_demo_companies_revenue_and_net_margin(demo) -> None:
    body = demo.get("/api/compare", params={"ciks": DEMO, "metrics": "revenue,net_margin"}).json()
    assert [c["ticker"] for c in body["companies"]] == ["AAPL", "MSFT", "GOOGL"]
    assert body["metrics"] == ["revenue", "net_margin"]
    assert body["source"]["mode"] == "demo"
    assert len(body["rows"]) == 3 * 2 * 10
    first = body["rows"][0]
    assert (first["cik"], first["metric_id"], first["fiscal_year_label"]) == (APPLE, "revenue",
                                                                              "FY2017")
    apple_2026 = next(r for r in body["rows"] if r["cik"] == APPLE and r["metric_id"] == "revenue"
                      and r["fiscal_year_label"] == "FY2026")
    # FX1 in milestones/acceptance.md.
    assert apple_2026["value"] == 478834000000
    assert apple_2026["unit"] == "USD" and apple_2026["period_end"] == "2026-09-26"
    assert apple_2026["data_source"].startswith("RECORDED SEC DEMO")
    margin = next(r for r in body["rows"] if r["cik"] == MICROSOFT
                  and r["metric_id"] == "net_margin" and r["fiscal_year_label"] == "FY2026")
    assert margin["value"] == pytest.approx(0.403054, abs=0.000001)  # FX10
    assert margin["unit"] == "ratio"


def test_m4_ac3_demo_year_ends_differ_and_are_named(demo) -> None:
    body = demo.get("/api/compare", params={"ciks": f"{APPLE},{MICROSOFT}"}).json()
    assert {c["ticker"]: c["fiscal_year_end"] for c in body["companies"]} == {
        "AAPL": "09-26", "MSFT": "06-30",
    }
    assert {"code": "fiscal_years_not_aligned", "message": "Fiscal years are not aligned"} in (
        body["warnings"]
    )
    assert body["index_base"] is None


def test_fx16_index_through_the_api(demo) -> None:
    body = demo.get("/api/compare", params={
        "ciks": f"{APPLE},{MICROSOFT}", "metrics": "revenue,net_margin",
        "index": "first_common_year",
    }).json()
    assert body["index_base"] == {
        "fiscal_year_by_cik": {APPLE: "FY2017", MICROSOFT: "FY2017"},
        "period_end_by_cik": {APPLE: "2017-09-30", MICROSOFT: "2017-06-30"},
    }
    value = {(r["cik"], r["metric_id"], r["fiscal_year_label"]): r for r in body["rows"]}
    assert value[(APPLE, "revenue", "FY2026")]["value"] == pytest.approx(208.88, abs=0.01)
    assert value[(MICROSOFT, "revenue", "FY2026")]["value"] == pytest.approx(343.62, abs=0.01)
    assert value[(APPLE, "revenue", "FY2026")]["indexed"] is True
    assert value[(APPLE, "net_margin", "FY2026")]["indexed"] is False


def test_years_limits_each_company(demo) -> None:
    body = demo.get("/api/compare", params={"ciks": f"{APPLE},{MICROSOFT}", "years": 5,
                                            "metrics": "revenue"}).json()
    assert len(body["rows"]) == 10
    assert {r["fiscal_year_label"] for r in body["rows"]} == {f"FY{y}" for y in range(2022, 2027)}


# ------------------------------------------------------------------ validation


def test_m4_ac2_too_few_and_too_many(demo) -> None:
    body = error(demo.get("/api/compare", params={"ciks": APPLE}), 422, "too_few_companies")
    assert body["message"] == "Compare 2–4 companies"
    five = ",".join(f"{n:010d}" for n in range(901, 906))
    body = error(demo.get("/api/compare", params={"ciks": five}), 422, "too_many_companies")
    assert body["message"] == "Compare 2–4 companies"


def test_m4_e3_duplicate_company_even_when_written_differently(demo) -> None:
    body = error(demo.get("/api/compare", params={"ciks": f"{APPLE},CIK320193"}), 422,
                 "duplicate_company")
    assert body["details"] == {"cik": APPLE}


def test_invalid_cik_metric_years_and_index(demo) -> None:
    error(demo.get("/api/compare", params={"ciks": f"{APPLE},abc"}), 422, "invalid_cik")
    body = error(demo.get("/api/compare", params={"ciks": DEMO, "metrics": "revenue,roe"}), 422,
                 "unknown_metric")
    assert body["details"]["unknown"] == ["roe"]
    seven = "revenue,revenue_growth,operating_margin,net_margin,operating_cash_flow,fcf,fcf_margin"
    error(demo.get("/api/compare", params={"ciks": DEMO, "metrics": seven}), 422,
          "invalid_request")
    for years in (4, 11):
        error(demo.get("/api/compare", params={"ciks": DEMO, "years": years}), 422,
              "invalid_years")
    response = demo.get("/api/compare", params={"ciks": DEMO, "index": "calendar"})
    assert response.status_code == 422


def test_company_outside_the_snapshot_is_404(demo) -> None:
    error(demo.get("/api/compare", params={"ciks": f"{APPLE},1045810"}), 404,
          "company_not_found")


def test_live_under_fixture_mode_is_refused(demo) -> None:
    error(demo.get("/api/compare", params={"ciks": DEMO, "source": "live"}), 409, "live_disabled")
    error(demo.get("/api/compare.csv", params={"ciks": DEMO, "source": "live"}), 409,
          "live_disabled")


# ------------------------------------------------------------------ CSV


def test_csv_is_an_attachment_with_exactly_the_json_rows(demo, monkeypatch) -> None:
    from datetime import date

    monkeypatch.setattr(compare_api, "_today", lambda: date(2026, 11, 9))
    params = {"ciks": f"{APPLE},{MICROSOFT}", "metrics": "revenue,net_margin",
              "index": "first_common_year"}
    shown = demo.get("/api/compare", params=params).json()
    response = demo.get("/api/compare.csv", params=params)
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"
    assert response.headers["content-disposition"] == (
        'attachment; filename="sec-analytics-compare-AAPL-MSFT-2026-11-09.csv"'
    )
    lines = list(csv.reader(io.StringIO(response.text, newline="")))
    assert lines[0] == list(HEADER)
    assert len(lines) - 1 == len(shown["rows"])
    for line, row in zip(lines[1:], shown["rows"], strict=True):
        cells = dict(zip(HEADER, line, strict=True))
        assert (cells["cik"], cells["metric"], cells["fiscal_year_label"]) == (
            row["cik"], row["metric_id"], row["fiscal_year_label"])
        if row["value"] is None:
            assert cells["value"] == ""
        else:
            assert float(cells["value"]) == pytest.approx(row["value"], rel=1e-12)


def test_csv_errors_use_the_json_envelope(demo) -> None:
    error(demo.get("/api/compare.csv", params={"ciks": APPLE}), 422, "too_few_companies")


# ------------------------------------------------------------------ live: SEC mocked


@pytest.fixture
def live(tmp_path):
    wait = NoWait()
    client = SecClient(FAKE_UA, clock=wait.clock, sleep=wait.sleep)
    settings = Settings(
        data_mode="live", sec_user_agent=SecretStr(FAKE_UA), sec_cache_dir=tmp_path / "cache"
    )
    with respx.mock(assert_all_called=False, assert_all_mocked=True) as router:
        for cik in (APPLE, MICROSOFT):
            facts = json.loads((FIXTURES / "companyfacts" / f"CIK{cik}.json").read_text("utf-8"))
            subs = json.loads((FIXTURES / "submissions" / f"CIK{cik}.json").read_text("utf-8"))
            router.get(companyfacts_url(cik)).mock(return_value=httpx.Response(200, json=facts))
            router.get(submissions_url(cik)).mock(return_value=httpx.Response(200, json=subs))
        yield TestClient(create_app(settings, sec_client=client)), router, wait


def test_live_compare_is_throttled_cached_and_labelled(live) -> None:
    client, router, wait = live
    params = {"ciks": f"{APPLE},{MICROSOFT}", "source": "live"}
    first = client.get("/api/compare", params=params).json()
    assert router.calls.call_count == 4  # submissions and Company Facts for each company
    assert wait.slept >= 3.0  # at most one request per second
    assert first["source"]["mode"] == "live"
    assert all(r["data_source"].startswith("LIVE") for r in first["rows"])
    second = client.get("/api/compare", params=params).json()
    assert router.calls.call_count == 4
    assert second["source"]["mode"] == "cached"
    assert [r["value"] for r in second["rows"]] == [r["value"] for r in first["rows"]]


def test_index_available_is_in_the_response(demo) -> None:
    body = demo.get("/api/compare", params={"ciks": f"{APPLE},{MICROSOFT}"}).json()
    assert body["index_available"] is True
    body = demo.get("/api/compare", params={"ciks": f"{APPLE},{MICROSOFT}",
                                            "metrics": "net_margin"}).json()
    assert body["index_available"] is False


def test_a_long_ciks_list_is_refused_without_parsing_it_all(demo) -> None:
    many = ",".join(f"{n:010d}" for n in range(1, 5000))
    error(demo.get("/api/compare", params={"ciks": many}), 422, "too_many_companies")
    error(demo.get("/api/compare", params={"ciks": "1," * 300}), 422, "too_many_companies")
