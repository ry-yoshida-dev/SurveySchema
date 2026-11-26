import re

import pytest

from survey_schema import FreeTextQuestion, InvalidAnswerError

QUESTION = FreeTextQuestion(
    id="Q1", text="Postal code", max_length=8, pattern=re.compile(r"\d{3}-\d{4}")
)


def test_validation() -> None:
    QUESTION.validate("100-0001")
    assert QUESTION.measurement_level is None
    for value in (" ", "100-00011", "abc-defg"):
        with pytest.raises(InvalidAnswerError):
            QUESTION.validate(value)


def test_rejects_non_positive_length() -> None:
    with pytest.raises(ValueError):
        FreeTextQuestion(id="Q1", text="T", max_length=0)


def test_min_length() -> None:
    question = FreeTextQuestion(id="Q1", text="Describe", min_length=10)
    question.validate("0123456789")
    with pytest.raises(InvalidAnswerError):
        question.validate("012345678")


@pytest.mark.parametrize(("min_length", "max_length"), [(0, None), (5, 4)])
def test_rejects_invalid_lengths(min_length: int, max_length: int | None) -> None:
    with pytest.raises(ValueError):
        FreeTextQuestion(
            id="Q1", text="T", min_length=min_length, max_length=max_length
        )
