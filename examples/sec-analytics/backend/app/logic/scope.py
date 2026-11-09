"""Deterministic pre-check of a question before any AI call (M5, Q43). Pure function.

Refuses, without calling the model:
- price forecasts, valuations and investment advice (small, documented term lists below);
- a company the app knows (a ticker or name in the demo universe or SEC's ticker file) that is
  not loaded in the current scope;
- a scope with no data at all.

Keep the lists small and test them for false positives: "buyback", "sales price of products",
"EPS" and "AI spending" must pass. Anything subtler is left to the model, whose refusals are
shown as they are.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

ADVICE_REFUSAL = (
    "This analyst only explains the loaded SEC data; "
    "it does not forecast prices or give investment advice"
)
NOT_LOADED = "That company is not loaded; open it first"
MISSING_CONTEXT = "Not enough loaded data to answer this question"

# Price forecasts and valuation: these phrases name market prices, which the app never has.
_PRICE = re.compile(
    r"\b(share|stock) price\b|\bprice target\b|\bmarket cap(italization|italisation)?\b|"
    r"\bp\s*/\s*e\b|\bvaluations?\b|\bvalue the (company|stock)\b|\bwill\b.{0,40}\btrade\b",
    re.IGNORECASE,
)
# Investment advice: what to do with one's money.
_ADVICE = re.compile(
    r"\bshould (i|we|you) (buy|sell|hold|short|invest)\b|\binvest in\b|\bbuy or sell\b|"
    r"\b(a|good) (buy|sell)\b|\bworth (buying|investing)\b",
    re.IGNORECASE,
)
# Upper-case words that are finance or everyday abbreviations, never read as tickers.
_NOT_TICKERS = frozenset(
    {
        "AI",
        "IT",
        "US",
        "USA",
        "USD",
        "EUR",
        "FY",
        "EPS",
        "CEO",
        "CFO",
        "COO",
        "ROE",
        "ROA",
        "FCF",
        "GAAP",
        "SEC",
        "EBIT",
        "EBITDA",
        "MD",
        "Q1",
        "Q2",
        "Q3",
        "Q4",
        "PDF",
        "ESG",
        "R",
        "D",
        "OK",
    }
)
_COMPANY_WORDS = frozenset(
    {
        "inc",
        "corp",
        "corporation",
        "co",
        "company",
        "ltd",
        "plc",
        "the",
        "group",
        "holdings",
        "class",
        "a",
        "b",
        "c",
    }
)


@dataclass(frozen=True)
class KnownCompany:
    ticker: str
    name: str


@dataclass(frozen=True)
class Refusal:
    code: str
    message: str


def _name_word(name: str) -> str | None:
    """The distinctive first word of an entity name ("Apple Inc." → "apple"), if it is one."""
    for word in re.findall(r"[A-Za-z][A-Za-z0-9&-]*", name):
        lowered = word.lower()
        if lowered not in _COMPANY_WORDS and len(lowered) >= 4:
            return lowered
    return None


def _mentions(question: str, company: KnownCompany) -> bool:
    ticker = company.ticker
    if (
        len(ticker) >= 2
        and ticker not in _NOT_TICKERS
        and re.search(rf"(?<![A-Za-z0-9-]){re.escape(ticker)}(?![A-Za-z0-9-])", question)
    ):
        return True
    word = _name_word(company.name)
    return bool(word) and re.search(rf"\b{re.escape(word)}\b", question, re.IGNORECASE) is not None


def precheck(
    question: str,
    *,
    loaded: list[KnownCompany],
    known: list[KnownCompany],
    has_context: bool,
) -> Refusal | None:
    """A refusal when the question is clearly out of scope, else None (ask the model)."""
    if _PRICE.search(question) or _ADVICE.search(question):
        return Refusal("out_of_scope", ADVICE_REFUSAL)
    loaded_tickers = {c.ticker for c in loaded}
    loaded_words = {_name_word(c.name) for c in loaded}
    for company in known:
        if company.ticker in loaded_tickers or (
            _name_word(company.name) and _name_word(company.name) in loaded_words
        ):
            continue
        if _mentions(question, company):
            return Refusal("company_not_loaded", NOT_LOADED)
    if not has_context:
        return Refusal("missing_context", MISSING_CONTEXT)
    return None
