from decimal import Decimal

import pytest

from survey_schema.decimal_places import count_decimal_places


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("0", 0),
        ("12", 0),
        ("1.5", 1),
        ("1.50", 1),
        ("-0.25", 2),
        ("0.000", 0),
        ("1E+3", 0),
        ("1.2E-3", 4),
        ("100.00", 0),
    ],
)
def test_counts_significant_decimal_places(value: str, expected: int) -> None:
    assert count_decimal_places(Decimal(value)) == expected


@pytest.mark.parametrize("value", ["NaN", "sNaN", "Infinity", "-Infinity"])
def test_rejects_non_finite(value: str) -> None:
    with pytest.raises(ValueError):
        count_decimal_places(Decimal(value))


def test_counts_beyond_context_precision() -> None:
    value = Decimal("1." + "0" * 40 + "1")
    assert count_decimal_places(value) == 41
    assert count_decimal_places(Decimal("1" * 40 + ".5")) == 1


@pytest.mark.parametrize(
    ("value", "expected"),
    [("1.0000000000000000000000000001", 28), ("0.00", 0), ("-0.0", 0)],
)
def test_does_not_round_or_count_zero_digits(value: str, expected: int) -> None:
    assert count_decimal_places(Decimal(value)) == expected
