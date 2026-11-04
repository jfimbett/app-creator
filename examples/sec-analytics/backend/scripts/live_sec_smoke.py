#!/usr/bin/env python3
"""Manual live SEC smoke check. Never run by `npm run verify`.

Fetches the ticker map, Apple's submissions and Apple's Company Facts through the app's client (3
requests, 1 per second), checks the structure the app relies on, and prints PASS or FAIL per check.

SEC_USER_AGENT comes from the process environment or the root .env. Its value is never printed.
Run from the backend folder:  .venv/bin/python scripts/live_sec_smoke.py
Exit code: 0 all passed, 1 a check failed, 2 not configured.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.clients.sec import (  # noqa: E402
    COMPANY_TICKERS_URL,
    SecClient,
    SecContactNotConfigured,
    SecError,
    companyfacts_url,
    submissions_url,
    validate_user_agent,
)
from app.logic.search import search, universe_from_tickers  # noqa: E402
from app.logic.statements import build_financials  # noqa: E402

APPLE = "0000320193"
REPO_ROOT = Path(__file__).resolve().parents[4]


def contact() -> str | None:
    """SEC_USER_AGENT from the environment, else from the root .env (only that one line is used)."""
    value = os.environ.get("SEC_USER_AGENT")
    if value:
        return value
    env_file = REPO_ROOT / ".env"
    if not env_file.is_file():
        return None
    for line in env_file.read_text(encoding="utf-8").splitlines():
        name, _, raw = line.partition("=")
        if name.strip() == "SEC_USER_AGENT":
            return raw.strip().strip("'\"")
    return None


class Report:
    def __init__(self) -> None:
        self.failed = 0

    def check(self, name: str, passed: bool) -> None:
        print(f"{'PASS' if passed else 'FAIL'}  {name}")
        self.failed += 0 if passed else 1


def main() -> int:
    agent = contact()
    try:
        validate_user_agent(agent)
    except SecContactNotConfigured:
        print("NOT RUN  SEC_USER_AGENT is not configured (see .env.example and docs/SETUP.md)")
        return 2

    report = Report()
    with SecClient(agent) as client:
        try:
            tickers = client.get_json(COMPANY_TICKERS_URL)
            report.check("ticker map: fetched", True)
            universe = universe_from_tickers(tickers)
            report.check("ticker map: lists many filers", len(universe) > 1000)
            found = search("NVDA", universe, 3)
            report.check(
                "ticker map: NVDA found by ticker", bool(found) and found[0].ticker == "NVDA"
            )
            found = search("apple", universe, 10)
            report.check("ticker map: Apple found by name", any(m.cik == APPLE for m in found))

            submissions = client.get_json(submissions_url(APPLE))
            report.check("submissions: name present", bool(submissions.get("name")))
            report.check("submissions: fiscal year end", bool(submissions.get("fiscalYearEnd")))
            report.check("submissions: recent filings", "recent" in submissions.get("filings", {}))

            facts = client.get_json(companyfacts_url(APPLE))
            report.check("company facts: us-gaap present", "us-gaap" in facts.get("facts", {}))
            result = build_financials(facts, companyfacts_url(APPLE))
            report.check("statements: reporting currency USD", result.currency == "USD")
            report.check("statements: at least 5 annual periods", len(result.periods) >= 5)
            latest = {key: values[-1] for key, values in result.series.items()}
            report.check("statements: latest revenue reported", latest["revenue"].status == "ok")
            report.check("statements: latest net income", latest["net_income"].status == "ok")
            report.check("statements: latest total assets", latest["assets"].status == "ok")
            report.check("ratios: latest net margin computed", latest["net_margin"].status == "ok")
            period = result.periods[-1]
            print(f"INFO  latest annual period: {period.label} (ends {period.end})")
        except SecError as exc:
            report.check(f"SEC request ({exc.code})", False)
    print("live SEC: passed" if not report.failed else f"live SEC: failed ({report.failed} checks)")
    return 0 if not report.failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
