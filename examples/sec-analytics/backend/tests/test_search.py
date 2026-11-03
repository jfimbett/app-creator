"""Search over the demo universe built from the recorded fixtures (M1-AC3).

The universe comes from fixtures/company_tickers.json plus the submissions files; no network.
"""

import pytest

from app.data.fixtures import FixtureStore, default_fixtures_dir
from app.logic.search import search

APPLE, MICROSOFT, ALPHABET = "0000320193", "0000789019", "0001652044"


@pytest.fixture(scope="module")
def universe():
    return FixtureStore(default_fixtures_dir()).universe()


def test_universe_has_one_entry_per_company(universe) -> None:
    assert [company.cik for company in universe] == [APPLE, MICROSOFT, ALPHABET]
    alphabet = universe[2]
    assert set(alphabet.tickers) == {"GOOGL", "GOOG", "GOOGM", "GOOGN"}


def test_lowercase_ticker_finds_apple_first_by_ticker(universe) -> None:
    results = search("aapl", universe, limit=10)
    assert results[0].cik == APPLE
    assert results[0].match == "ticker"
    assert results[0].ticker == "AAPL"


@pytest.mark.parametrize("query", ["320193", "0000320193", "CIK320193", " 320193 "])
def test_cik_in_any_padding_finds_apple_only(universe, query) -> None:
    results = search(query, universe, limit=10)
    assert [(r.cik, r.match) for r in results] == [(APPLE, "cik")]


def test_name_substring_is_case_insensitive(universe) -> None:
    results = search("Microsoft", universe, limit=10)
    assert [(r.cik, r.match) for r in results] == [(MICROSOFT, "name")]
    assert [r.cik for r in search("soft", universe, limit=10)] == [MICROSOFT]


@pytest.mark.parametrize("query", ["GOOGL", "goog", "GOO", "alphabet"])
def test_alphabet_appears_exactly_once(universe, query) -> None:
    results = search(query, universe, limit=10)
    assert [r.cik for r in results] == [ALPHABET]


def test_exact_ticker_reports_the_matched_ticker(universe) -> None:
    assert search("goog", universe, limit=10)[0].ticker == "GOOG"
    assert search("GOOGL", universe, limit=10)[0].ticker == "GOOGL"


def test_prefix_match_is_ranked_ticker(universe) -> None:
    result = search("GOO", universe, limit=10)[0]
    assert result.match == "ticker"
    assert result.ticker == "GOOGL"  # the company's primary ticker among those that match


def test_unknown_company_gives_no_results(universe) -> None:
    assert search("tesla", universe, limit=10) == []


def test_eleven_digits_is_not_a_cik_and_matches_nothing(universe) -> None:
    assert search("12345678901", universe, limit=10) == []


def test_ranking_exact_ticker_before_name(universe) -> None:
    # "a" is a ticker prefix of AAPL and a name substring of "Apple Inc." and "Alphabet Inc."
    # ("MICROSOFT CORP" has no "a").
    results = search("a", universe, limit=10)
    assert [(r.cik, r.match) for r in results] == [(APPLE, "ticker"), (ALPHABET, "name")]


def test_limit_caps_the_results(universe) -> None:
    assert len(search("a", universe, limit=1)) == 1
