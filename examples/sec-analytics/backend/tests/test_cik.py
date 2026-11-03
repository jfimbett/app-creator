"""CIK normalization (M1-E2 at unit level; brief §7 "CIK")."""

import pytest

from app.logic.cik import InvalidCik, normalize_cik


@pytest.mark.parametrize(
    "text",
    ["320193", "0000320193", "CIK320193", " 320193 ", "cik0000320193", "CIK 320193"],
)
def test_apple_cik_forms_normalize_to_ten_digits(text: str) -> None:
    assert normalize_cik(text) == "0000320193"


def test_ten_digit_cik_is_kept() -> None:
    assert normalize_cik("1652044") == "0001652044"
    assert normalize_cik("9999999999") == "9999999999"


@pytest.mark.parametrize(
    "text",
    ["abc", "12345678901", "-1", "", "   ", "CIK", "32 0193", "320193.0", "+320193", "٣٢٠١٩٣"],
)
def test_invalid_cik_is_rejected(text: str) -> None:
    with pytest.raises(InvalidCik) as caught:
        normalize_cik(text)
    assert str(caught.value) == "A CIK has up to 10 digits"


def test_non_string_is_rejected() -> None:
    with pytest.raises(InvalidCik):
        normalize_cik(320193)  # type: ignore[arg-type]
