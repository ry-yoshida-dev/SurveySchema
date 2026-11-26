import pytest

from survey_schema import (
    Bounds,
    IntegerQuestion,
    InvalidAnswerError,
    MeasurementLevel,
    SpecialResponse,
    SpecialResponseKind,
    SpecialResponses,
)

QUESTION = IntegerQuestion(
    id="Q1", text="Age", bounds=Bounds(minimum=0, maximum=120), unit="years"
)
REFUSED = SpecialResponses(
    (SpecialResponse(999, "Refused", SpecialResponseKind.REFUSED),)
)


def test_value_and_validation() -> None:
    assert QUESTION.is_value(30)
    assert not QUESTION.is_value("30") and not QUESTION.is_value(True)
    QUESTION.validate(0)
    QUESTION.validate(120)
    with pytest.raises(InvalidAnswerError):
        QUESTION.validate(121)


def test_measurement_level() -> None:
    assert QUESTION.measurement_level is MeasurementLevel.RATIO
    year = IntegerQuestion(id="Q1", text="Year", is_zero_absolute=False)
    assert year.measurement_level is MeasurementLevel.INTERVAL


@pytest.mark.parametrize(
    ("bounds", "is_inside"),
    [
        (Bounds[int](), True),
        (Bounds(minimum=0), True),
        (Bounds(maximum=999), True),
        (Bounds(minimum=1000), False),
        (Bounds(minimum=0, maximum=120), False),
    ],
)
def test_special_codes_must_lie_outside_bounds(
    bounds: Bounds[int], is_inside: bool
) -> None:
    assert IntegerQuestion(id="Q1", text="T", bounds=bounds).is_value_code(999) is (
        is_inside
    )
    if is_inside:
        with pytest.raises(ValueError):
            IntegerQuestion(id="Q1", text="T", bounds=bounds, special_responses=REFUSED)
    else:
        IntegerQuestion(id="Q1", text="T", bounds=bounds, special_responses=REFUSED)


def test_rejects_blank_unit() -> None:
    with pytest.raises(ValueError):
        IntegerQuestion(id="Q1", text="Age", unit=" ")
