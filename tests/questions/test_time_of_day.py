from datetime import UTC, time

import pytest

from survey_schema import (
    Bounds,
    InvalidAnswerError,
    MeasurementLevel,
    TimeOfDayQuestion,
)

QUESTION = TimeOfDayQuestion(
    id="Q1", text="Bedtime", bounds=Bounds(maximum=time(23, 59))
)


def test_value_and_validation() -> None:
    assert QUESTION.is_value(time(22, 30))
    QUESTION.validate(time(22, 30))
    with pytest.raises(InvalidAnswerError):
        QUESTION.validate(time(22, 30, tzinfo=UTC))


def test_measurement_level_is_cyclic() -> None:
    assert QUESTION.measurement_level is MeasurementLevel.CYCLIC


def test_rejects_aware_bounds() -> None:
    with pytest.raises(ValueError):
        TimeOfDayQuestion(id="Q1", text="T", bounds=Bounds(minimum=time(1, tzinfo=UTC)))
    with pytest.raises(ValueError):
        TimeOfDayQuestion(id="Q1", text="T", bounds=Bounds(maximum=time(1, tzinfo=UTC)))
