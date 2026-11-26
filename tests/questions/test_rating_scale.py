import pytest

from survey_schema import (
    InvalidAnswerError,
    MeasurementLevel,
    RatingScale,
    RatingScaleQuestion,
    SpecialResponse,
    SpecialResponseKind,
    SpecialResponses,
)

QUESTION = RatingScaleQuestion(
    id="Q1", text="Satisfaction", scale=RatingScale(minimum=0, maximum=10)
)


def test_value_and_validation() -> None:
    assert QUESTION.is_value(10) and not QUESTION.is_value(True)
    assert QUESTION.measurement_level is MeasurementLevel.ORDINAL
    assert all(QUESTION.is_value_code(point) for point in range(11))
    assert not QUESTION.is_value_code(-1) and not QUESTION.is_value_code(11)
    with pytest.raises(InvalidAnswerError):
        QUESTION.validate(11)


def test_semantic_differential() -> None:
    question = RatingScaleQuestion(
        id="Q1",
        text="Impression",
        scale=RatingScale.bipolar(minimum=-3, maximum=3, left="Cold", right="Warm"),
    )
    question.validate(-3)
    question.validate(0)
    with pytest.raises(InvalidAnswerError):
        question.validate(4)


def test_special_code_on_step_gap_is_allowed() -> None:
    scale = RatingScale(minimum=0, maximum=100, step=10)
    question = RatingScaleQuestion(
        id="Q1",
        text="T",
        scale=scale,
        special_responses=SpecialResponses(
            (SpecialResponse(99, "Don't know", SpecialResponseKind.DONT_KNOW),)
        ),
    )
    assert not question.is_value_code(99) and question.is_value_code(90)
    with pytest.raises(ValueError):
        RatingScaleQuestion(
            id="Q1",
            text="T",
            scale=scale,
            special_responses=SpecialResponses(
                (SpecialResponse(90, "Don't know", SpecialResponseKind.DONT_KNOW),)
            ),
        )
