"""Deterministic pre-check of a question before any AI call (M5, Q43). Pure function.

Refuses, without calling the model:
- price forecasts, valuations and investment advice (small, documented patterns below);
- a company the app knows (a ticker or name in the demo universe or SEC's ticker file) that is
  not loaded in the current scope;
- a scope with no data at all.

In live mode the known list is SEC's whole ticker file, full of common words ("General Motors",
"Target", tickers ON, ALL, NOW). So a company counts as mentioned only when:
- its ticker appears as an upper-case word that is not a common abbreviation or English word,
  and the question is not written all in capitals;
- a name of two or more distinctive words appears as that phrase ("first solar"; a third word is
  used when the first two are both common, as in "united states steel");
- a one-word name appears capitalised, not as the first word of a sentence ("Target's revenue",
  never "revenue target").
These rules are tested for false positives ("first quarter", "general and administrative",
"SG&A", "ON track", "invest in R&D", "valuation allowance"). Anything subtler is left to the
model, whose refusals are shown as they are; a missed mention still only gets the loaded data.
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
    r"\b(share|stock) prices?\b|\bprice targets?\b|\bmarket cap(italization|italisation)?\b|"
    r"\bp\s*/\s*e\b|\bvalue the (company|stock|shares)\b|\bwhere will\b.{0,40}\btrade\b|"
    r"\bwill\b.{0,40}\btrade (at|above|below|higher|lower|for|near)\b|"
    r"\bvaluation of (the )?(company|stock|shares|it)\b|\bhow much is\b.{0,30}\bworth\b",
    re.IGNORECASE,
)
_VALUATION_OF_NAME = re.compile(r"\b[Vv]aluation (of|for) [A-Z]")
# Investment advice: what to do with one's money.
_ADVICE = re.compile(
    r"\bshould (i|we|you)\b.{0,20}\b(buy|sell|hold|short|invest)\b|\bbuy or sell\b|"
    r"\b(a|good) (buy|sell)\b|\bworth (buying|investing)\b|"
    r"\binvest(ing)? in (the |its |their )?(stock|shares)\b",
    re.IGNORECASE,
)
# Upper-case words that are finance abbreviations or English words, never read as tickers.
_NOT_TICKERS = frozenset(
    "AI IT US USA USD EUR FY EPS CEO CFO COO ROE ROA FCF GAAP SEC EBIT EBITDA MD PDF ESG OK "
    "Q1 Q2 Q3 Q4 SG GM NI OI CF IP NET ON ALL NOW ARE OR AN AT BE DO GO SO TO UP WE ME MY IN "
    "OF BY AS IS IF NO AM ANY CAN HAS HAD WAS FOR AND THE NOT BUT OUT NEW OLD BIG KEY TOP LOW "
    "HIGH CASH DEBT LOSS GAIN RISK SALE SALES COST TAX".split()
)
# Words that say nothing about which company is meant.
_SUFFIXES = frozenset(
    "inc inc. incorporated corp corp. corporation co co. company ltd limited plc llc lp l.p. "
    "holdings holding group the class a b c n.v. s.a. ag se de".split()
)
_COMMON = frozenset(
    "general first american united international national global target equity capital energy "
    "financial federal royal standard universal western eastern southern northern pacific "
    "atlantic digital advanced applied public service services industries resources solutions "
    "systems technologies partners realty properties bank bancorp trust union home health medical "
    "world new old great best prime core smart next open real simple main states north south east "
    "west america estate".split()
)
_WORD = re.compile(r"[A-Za-z][A-Za-z0-9&'.-]*")


@dataclass(frozen=True)
class KnownCompany:
    ticker: str
    name: str


@dataclass(frozen=True)
class Refusal:
    code: str
    message: str


def _core(name: str) -> list[str]:
    """The distinctive words of an entity name, lower case ("Apple Inc." → ["apple"])."""
    words = [w.lower().rstrip(".,") for w in _WORD.findall(name)]
    return [w for w in words if w and w not in _SUFFIXES]


def _name_pattern(name: str) -> re.Pattern[str] | None:
    core = _core(name)
    if not core:
        return None
    if len(core) == 1:
        word = core[0]
        if len(word) < 4:
            return None
        # Capitalised and not the first word of a sentence.
        title, upper = re.escape(word.capitalize()), re.escape(word.upper())
        return re.compile(rf"(?<![.!?]\s)(?<!^)\b(?:{title}|{upper})\b")
    size = 3 if core[0] in _COMMON and core[1] in _COMMON and len(core) >= 3 else 2
    phrase = r"\s+".join(re.escape(w) for w in core[:size])
    return re.compile(rf"\b{phrase}\b", re.IGNORECASE)


def _mentions(question: str, company: KnownCompany) -> bool:
    ticker = company.ticker
    shouting = not re.search(r"[a-z]", question)
    if (
        not shouting
        and len(ticker) >= 2
        and ticker not in _NOT_TICKERS
        and re.search(rf"(?<![A-Za-z0-9&-]){re.escape(ticker)}(?![A-Za-z0-9&-])", question)
    ):
        return True
    pattern = _name_pattern(company.name)
    return bool(pattern and pattern.search(question.strip()))


def precheck(
    question: str,
    *,
    loaded: list[KnownCompany],
    known: list[KnownCompany],
    has_context: bool,
) -> Refusal | None:
    """A refusal when the question is clearly out of scope, else None (ask the model)."""
    if _PRICE.search(question) or _VALUATION_OF_NAME.search(question) or _ADVICE.search(question):
        return Refusal("out_of_scope", ADVICE_REFUSAL)
    loaded_tickers = {c.ticker for c in loaded}
    loaded_cores = {tuple(_core(c.name)) for c in loaded}
    for company in known:
        if company.ticker in loaded_tickers or tuple(_core(company.name)) in loaded_cores:
            continue
        if _mentions(question, company):
            return Refusal("company_not_loaded", NOT_LOADED)
    if not has_context:
        return Refusal("missing_context", MISSING_CONTEXT)
    return None
