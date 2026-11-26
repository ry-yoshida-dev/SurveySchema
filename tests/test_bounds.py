from decimal import Decimal

import pytest

from survey_schema import Bounds, InvalidAnswerError


def test_contains_and_validate() -> None:
    bounds = Bounds(minimum=0, maximum=10)
    assert 0 in bounds and 10 in bounds and 11 not in bounds
    with pytest.raises(InvalidAnswerError):
        bounds.validate(-1)


def test_open_bounds_and_inverted_range() -> None:
    assert 10**9 in Bounds[int](minimum=0)
    with pytest.raises(ValueError):
        Bounds(minimum=5, maximum=1)


@pytest.mark.parametrize(
    ("minimum", "maximum"),
    [(Decimal("NaN"), None), (None, Decimal("NaN")), (Decimal(0), Decimal("NaN"))],
)
def test_rejects_nan_ends(minimum: Decimal | None, maximum: Decimal | None) -> None:
    with pytest.raises(ValueError):
        Bounds(minimum=minimum, maximum=maximum)
