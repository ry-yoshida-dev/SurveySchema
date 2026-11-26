from decimal import Decimal

import pytest

from survey_schema import (
    InvalidAnswerError,
    MeasurementLevel,
    SpecialResponse,
    SpecialResponseKind,
    SpecialResponses,
    VisualAnalogScaleQuestion,
)

QUESTION = VisualAnalogScaleQuestion(
    id="Q1", text="Pain", left_anchor="None", right_anchor="Worst"
)
STEPPED = VisualAnalogScaleQuestion(
    id="Q1",
    text="Pain",
    left_anchor="None",
    right_anchor="Worst",
    minimum=Decimal(-10),
    maximum=Decimal(10),
    resolution=Decimal("0.5"),
)


def _special(code: int) -> SpecialResponses:
    return SpecialResponses(
        (SpecialResponse(code, "Don't know", SpecialResponseKind.DONT_KNOW),)
    )


def test_value_and_validation() -> None:
    assert QUESTION.is_value(Decimal("42.5"))
    assert not QUESTION.is_value(3) and not QUESTION.is_value(False)
    assert QUESTION.measurement_level is MeasurementLevel.INTERVAL
    QUESTION.validate(Decimal(0))
    QUESTION.validate(Decimal("100.0"))
    QUESTION.validate(Decimal("12.3456"))


@pytest.mark.parametrize("value", ["-0.1", "100.1", "NaN", "Infinity"])
def test_rejects_off_line_positions(value: str) -> None:
    with pytest.raises(InvalidAnswerError):
        QUESTION.validate(Decimal(value))


@pytest.mark.parametrize("value", ["-10", "-9.5", "0", "7.50", "10"])
def test_resolution_accepts_steps_from_minimum(value: str) -> None:
    STEPPED.validate(Decimal(value))


@pytest.mark.parametrize("value", ["-9.75", "0.1", "9.99"])
def test_resolution_rejects_positions_between_steps(value: str) -> None:
    with pytest.raises(InvalidAnswerError):
        STEPPED.validate(Decimal(value))


def test_is_value_code_follows_the_line() -> None:
    assert QUESTION.is_value_code(0) and QUESTION.is_value_code(100)
    assert not QUESTION.is_value_code(-1) and not QUESTION.is_value_code(101)
    VisualAnalogScaleQuestion(
        id="Q1",
        text="T",
        left_anchor="A",
        right_anchor="B",
        special_responses=_special(999),
    )
    with pytest.raises(ValueError):
        VisualAnalogScaleQuestion(
            id="Q1",
            text="T",
            left_anchor="A",
            right_anchor="B",
            special_responses=_special(99),
        )


@pytest.mark.parametrize(
    ("minimum", "maximum", "resolution"),
    [
        ("10", "10", None),
        ("10", "0", None),
        ("0", "Infinity", None),
        ("NaN", "10", None),
        ("0", "10", "0"),
        ("0", "10", "-1"),
        ("0", "10", "Infinity"),
    ],
)
def test_rejects_invalid_ends_and_resolution(
    minimum: str, maximum: str, resolution: str | None
) -> None:
    with pytest.raises(ValueError):
        VisualAnalogScaleQuestion(
            id="Q1",
            text="T",
            left_anchor="A",
            right_anchor="B",
            minimum=Decimal(minimum),
            maximum=Decimal(maximum),
            resolution=None if resolution is None else Decimal(resolution),
        )


def test_rejects_blank_anchor() -> None:
    with pytest.raises(ValueError):
        VisualAnalogScaleQuestion(id="Q1", text="T", left_anchor=" ", right_anchor="B")
    with pytest.raises(ValueError):
        VisualAnalogScaleQuestion(id="Q1", text="T", left_anchor="A", right_anchor=" ")


def test_rejects_nan_end_with_special_responses() -> None:
    with pytest.raises(ValueError):
        VisualAnalogScaleQuestion(
            id="Q1",
            text="T",
            left_anchor="A",
            right_anchor="B",
            minimum=Decimal("NaN"),
            special_responses=_special(999),
        )


def test_resolution_is_exact_beyond_context_precision() -> None:
    question = VisualAnalogScaleQuestion(
        id="Q1",
        text="T",
        left_anchor="A",
        right_anchor="B",
        maximum=Decimal(10) ** 30,
        resolution=Decimal(1),
    )
    question.validate(Decimal("1" + "0" * 29))
    with pytest.raises(InvalidAnswerError):
        question.validate(Decimal("1" + "0" * 29 + ".5"))


def test_tiny_resolution() -> None:
    question = VisualAnalogScaleQuestion(
        id="Q1",
        text="T",
        left_anchor="A",
        right_anchor="B",
        resolution=Decimal("1E-30"),
    )
    question.validate(Decimal("50"))
    question.validate(Decimal("0." + "0" * 29 + "1"))
    with pytest.raises(InvalidAnswerError):
        question.validate(Decimal("0." + "0" * 30 + "1"))
