from decimal import Decimal

import pytest

from survey_schema import (
    Bounds,
    InvalidAnswerError,
    MeasurementLevel,
    RealNumberQuestion,
    SpecialResponse,
    SpecialResponseKind,
    SpecialResponses,
)

QUESTION = RealNumberQuestion(
    id="Q1",
    text="Height",
    bounds=Bounds(minimum=Decimal(50), maximum=Decimal(250)),
    decimal_places=1,
)
REFUSED = SpecialResponses(
    (SpecialResponse(999, "Refused", SpecialResponseKind.REFUSED),)
)


def test_value_and_validation() -> None:
    assert QUESTION.is_value(Decimal("170.5"))
    assert not QUESTION.is_value(170)
    QUESTION.validate(Decimal("170.5"))
    QUESTION.validate(Decimal("170.50"))
    QUESTION.validate(Decimal("2E+2"))


@pytest.mark.parametrize("value", ["Infinity", "NaN", "300", "49.9", "170.55"])
def test_rejects_invalid_values(value: str) -> None:
    with pytest.raises(InvalidAnswerError):
        QUESTION.validate(Decimal(value))


def test_unlimited_decimal_places() -> None:
    RealNumberQuestion(id="Q1", text="T").validate(Decimal("1.23456789"))


def test_measurement_level() -> None:
    assert QUESTION.measurement_level is MeasurementLevel.RATIO
    celsius = RealNumberQuestion(id="Q1", text="T", is_zero_absolute=False)
    assert celsius.measurement_level is MeasurementLevel.INTERVAL


@pytest.mark.parametrize(
    ("bounds", "is_inside"),
    [
        (Bounds[Decimal](), True),
        (Bounds(minimum=Decimal(0)), True),
        (Bounds(maximum=Decimal(1000)), True),
        (Bounds(maximum=Decimal("998.9")), False),
        (Bounds(minimum=Decimal(0), maximum=Decimal(250)), False),
    ],
)
def test_special_codes_must_lie_outside_bounds(
    bounds: Bounds[Decimal], is_inside: bool
) -> None:
    question = RealNumberQuestion(id="Q1", text="T", bounds=bounds)
    assert question.is_value_code(999) is is_inside
    if is_inside:
        with pytest.raises(ValueError):
            RealNumberQuestion(
                id="Q1", text="T", bounds=bounds, special_responses=REFUSED
            )
    else:
        RealNumberQuestion(id="Q1", text="T", bounds=bounds, special_responses=REFUSED)


def test_rejects_invalid_definitions() -> None:
    with pytest.raises(ValueError):
        RealNumberQuestion(id="Q1", text="T", decimal_places=-1)
    with pytest.raises(ValueError):
        RealNumberQuestion(id="Q1", text="T", unit=" ")
