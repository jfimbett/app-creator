"""Build SEC archive addresses from validated parts (brief §7, M3-AC6, M3-E5).

Nothing here takes a whole URL from a caller. An address is assembled from a normalized CIK, an
accession number and a primary document name that came from SEC's own submissions data, and each
part is checked first. The SEC client checks the finished URL against its allowlist again.
"""

from __future__ import annotations

import re

from app.logic.cik import normalize_cik

ARCHIVE_ROOT = "https://www.sec.gov/Archives/edgar/data"
_ACCESSION = re.compile(r"[0-9]{10}-[0-9]{2}-[0-9]{6}")
_PRIMARY_DOCUMENT = re.compile(r"[A-Za-z0-9._-]{1,200}")


class InvalidArchivePart(ValueError):
    """An accession number or document name that must not be used to build an address."""


def is_valid_accession(accession: object) -> bool:
    """True for `0000320193-26-000026` and nothing else (no paths, no extra characters)."""
    return isinstance(accession, str) and _ACCESSION.fullmatch(accession) is not None


def is_valid_primary_document(name: object) -> bool:
    """True for a plain file name: no slash, no spaces, not made only of dots."""
    return (
        isinstance(name, str)
        and _PRIMARY_DOCUMENT.fullmatch(name) is not None
        and name.strip(".") != ""
    )


def _archive_folder(cik: str, accession: str) -> str:
    if not is_valid_accession(accession):
        raise InvalidArchivePart("Not a valid accession number")
    digits = accession.replace("-", "")
    return f"{ARCHIVE_ROOT}/{int(normalize_cik(cik))}/{digits}"


def document_url(cik: str, accession: str, primary_document: str) -> str:
    """The exact archive address of a filing's primary document."""
    if not is_valid_primary_document(primary_document):
        raise InvalidArchivePart("Not a valid document name")
    return f"{_archive_folder(cik, accession)}/{primary_document}"


def index_url(cik: str, accession: str) -> str:
    """The filing's index page on sec.gov. A link for people; the app never fetches it."""
    return f"{_archive_folder(cik, accession)}/{accession}-index.html"
