import pytest

from survey_schema import YearMonth


def test_order_and_str() -> None:
    assert YearMonth(1990, 12) < YearMonth(1991, 1) < YearMonth(1991, 2)
    assert YearMonth(1991, 1) == YearMonth(1991, 1)
    assert str(YearMonth(987, 4)) == "0987-04"


@pytest.mark.parametrize(("year", "month"), [(2000, 0), (2000, 13), (0, 1), (10000, 1)])
def test_rejects_out_of_range(year: int, month: int) -> None:
    with pytest.raises(ValueError):
        YearMonth(year, month)


def test_rejects_bool() -> None:
    with pytest.raises(TypeError):
        YearMonth(2000, True)
    with pytest.raises(TypeError):
        YearMonth(True, 1)
