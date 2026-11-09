"""Deterministic scope pre-check (M5-E3, M5-E4): refusals happen before any model call. Offline."""

import pytest

from app.logic.scope import (
    ADVICE_REFUSAL,
    MISSING_CONTEXT,
    NOT_LOADED,
    KnownCompany,
    precheck,
)

APPLE = KnownCompany(ticker="AAPL", name="Apple Inc.")
MICROSOFT = KnownCompany(ticker="MSFT", name="MICROSOFT CORP")
ALPHABET = KnownCompany(ticker="GOOGL", name="Alphabet Inc.")
KNOWN = [APPLE, MICROSOFT, ALPHABET]


def check(question, loaded=(APPLE,), has_context=True):
    return precheck(question, loaded=list(loaded), known=KNOWN, has_context=has_context)


@pytest.mark.parametrize(
    "question",
    [
        "What will Apple's share price be next year?",
        "Should I buy MSFT?",
        "should i sell my apple shares",
        "Is Apple a buy or sell right now?",
        "What is Apple's stock price target?",
        "What is Apple's market cap?",
        "What P/E does Apple trade at?",
        "Give me a valuation of Apple",
        "Where will Apple trade in 2027?",
        "Should I invest in Apple?",
    ],
)
def test_m4_e3_prices_valuations_and_advice_are_refused(question) -> None:
    refusal = check(question)
    assert refusal is not None
    assert (refusal.code, refusal.message) == ("out_of_scope", ADVICE_REFUSAL)
    assert ADVICE_REFUSAL == (
        "This analyst only explains the loaded SEC data; it does not forecast prices or give "
        "investment advice"
    )


@pytest.mark.parametrize(
    "question",
    [
        "How did Apple's share buybacks affect equity?",
        "What is the net margin trend?",
        "What does the 10-K say about the sales price of products?",
        "Why did net margin change?",
        "Which risk factors mention supply?",
        "How much did revenue grow in FY2026?",
        "What was FCF and EPS in the latest year? Compare to the CEO letter in the 10-K.",
        "Does the filing mention AI or IT spending?",
    ],
)
def test_allowed_questions_pass(question) -> None:
    assert check(question) is None


def test_m5_e4_a_known_company_that_is_not_loaded_is_refused() -> None:
    for question in (
        "How does Apple compare with Microsoft?",
        "Is MSFT's margin higher?",
        "What about Alphabet's revenue?",
    ):
        refusal = check(question, loaded=(APPLE,))
        assert refusal is not None, question
        assert (refusal.code, refusal.message) == ("company_not_loaded", NOT_LOADED)
    assert NOT_LOADED == "That company is not loaded; open it first"
    assert check("How does Apple compare with Microsoft?", loaded=(APPLE, MICROSOFT)) is None


def test_tickers_count_only_as_whole_upper_case_words() -> None:
    # "msft" in lower case or inside a word is not a ticker mention; names match case-insensitively.
    assert check("is the msft-like growth sustainable?") is None
    assert check("what about microsoft?") is not None


def test_empty_context_is_refused() -> None:
    refusal = check("What is the net margin trend?", has_context=False)
    assert (refusal.code, refusal.message) == ("missing_context", MISSING_CONTEXT)
    assert MISSING_CONTEXT == "Not enough loaded data to answer this question"
