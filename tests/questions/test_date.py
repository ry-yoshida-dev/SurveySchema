from datetime import date, datetime

import pytest

from survey_schema import Bounds, DateQuestion, InvalidAnswerError

QUESTION = DateQuestion(id="Q1", text="Visit", bounds=Bounds(minimum=date(2026, 1, 1)))


def test_value_and_validation() -> None:
    assert QUESTION.is_value(date(2026, 5, 1))
    assert not QUESTION.is_value(datetime(2026, 5, 1))
    with pytest.raises(InvalidAnswerError):
        QUESTION.validate(date(2025, 12, 31))


def test_rejects_datetime_bounds() -> None:
    with pytest.raises(ValueError):
        DateQuestion(id="Q1", text="T", bounds=Bounds(minimum=datetime(2026, 1, 1)))
    with pytest.raises(ValueError):
        DateQuestion(id="Q1", text="T", bounds=Bounds(maximum=datetime(2026, 1, 1)))
