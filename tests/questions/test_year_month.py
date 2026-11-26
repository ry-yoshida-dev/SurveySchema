from datetime import date

import pytest

from survey_schema import (
    Bounds,
    InvalidAnswerError,
    MeasurementLevel,
    YearMonth,
    YearMonthQuestion,
)

QUESTION = YearMonthQuestion(
    id="Q1",
    text="Start",
    bounds=Bounds(minimum=YearMonth(2000, 4), maximum=YearMonth(2026, 3)),
)


def test_value_and_validation() -> None:
    assert QUESTION.is_value(YearMonth(2010, 1))
    assert not QUESTION.is_value(date(2010, 1, 1)) and not QUESTION.is_value(2010)
    assert QUESTION.measurement_level is MeasurementLevel.INTERVAL
    assert not QUESTION.is_value_code(2010)
    QUESTION.validate(YearMonth(2000, 4))
    QUESTION.validate(YearMonth(2026, 3))


@pytest.mark.parametrize("value", [YearMonth(2000, 3), YearMonth(2026, 4)])
def test_rejects_out_of_bounds(value: YearMonth) -> None:
    with pytest.raises(InvalidAnswerError):
        QUESTION.validate(value)


def test_unbounded_by_default() -> None:
    YearMonthQuestion(id="Q1", text="T").validate(YearMonth(1, 1))
