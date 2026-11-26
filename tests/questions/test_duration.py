from datetime import timedelta

import pytest

from survey_schema import (
    Bounds,
    DurationQuestion,
    InvalidAnswerError,
    MeasurementLevel,
)

QUESTION = DurationQuestion(
    id="Q1",
    text="Sleep",
    bounds=Bounds(maximum=timedelta(hours=24)),
    resolution=timedelta(minutes=1),
)


def test_value_and_validation() -> None:
    assert QUESTION.is_value(timedelta(hours=7))
    assert not QUESTION.is_value(7)
    assert QUESTION.measurement_level is MeasurementLevel.RATIO
    QUESTION.validate(timedelta(0))
    QUESTION.validate(timedelta(hours=1, minutes=50))
    QUESTION.validate(timedelta(hours=24))


@pytest.mark.parametrize(
    "value",
    [timedelta(minutes=-1), timedelta(hours=24, minutes=1), timedelta(seconds=90)],
)
def test_rejects_invalid_lengths(value: timedelta) -> None:
    with pytest.raises(InvalidAnswerError):
        QUESTION.validate(value)


def test_any_length_without_resolution() -> None:
    DurationQuestion(id="Q1", text="T").validate(timedelta(microseconds=1))


def test_accepts_negative_minimum_bound() -> None:
    question = DurationQuestion(
        id="Q1", text="T", bounds=Bounds(minimum=timedelta(-1), maximum=timedelta(1))
    )
    with pytest.raises(InvalidAnswerError):
        question.validate(timedelta(seconds=-1))


@pytest.mark.parametrize(
    ("bounds", "resolution"),
    [
        (Bounds(maximum=timedelta(seconds=-1)), None),
        (Bounds[timedelta](), timedelta(0)),
        (Bounds[timedelta](), timedelta(minutes=-1)),
    ],
)
def test_rejects_invalid_definitions(
    bounds: Bounds[timedelta], resolution: timedelta | None
) -> None:
    with pytest.raises(ValueError):
        DurationQuestion(id="Q1", text="T", bounds=bounds, resolution=resolution)
