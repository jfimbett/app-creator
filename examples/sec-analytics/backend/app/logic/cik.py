"""CIK normalization.

A CIK (Central Index Key) is the SEC's number for a filer. data.sec.gov needs it as exactly
10 digits with leading zeros, e.g. Apple's 320193 becomes "0000320193".
"""

import re

_DIGITS = re.compile(r"[0-9]{1,10}")  # ASCII digits only; \d would also accept other scripts
_PREFIX = "CIK"


class InvalidCik(ValueError):
    """The text is not 1-10 digits (optionally prefixed with "CIK")."""

    def __init__(self) -> None:
        super().__init__("A CIK has up to 10 digits")


def normalize_cik(text: str) -> str:
    """Return the 10-digit, zero-padded CIK for `text`, or raise `InvalidCik`.

    Accepts surrounding spaces and an optional case-insensitive "CIK" prefix.
    """
    if not isinstance(text, str):
        raise InvalidCik()
    value = text.strip()
    if value[: len(_PREFIX)].upper() == _PREFIX:
        value = value[len(_PREFIX) :].strip()
    if not _DIGITS.fullmatch(value):
        raise InvalidCik()
    return value.zfill(10)
