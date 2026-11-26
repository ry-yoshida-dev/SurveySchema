import pytest

from survey_schema import (
    BestWorstChoice,
    BestWorstQuestion,
    ChoiceOption,
    ChoiceOptions,
    ChoiceSelection,
    InvalidAnswerError,
    MeasurementLevel,
)

QUESTION = BestWorstQuestion(
    id="Q1", text="Most and least", options=ChoiceOptions.from_labels(["A", "B", "C"])
)


def test_value_and_validation() -> None:
    assert QUESTION.is_value(BestWorstChoice(best=1, worst=2))
    assert not QUESTION.is_value(ChoiceSelection(1))
    assert QUESTION.measurement_level is MeasurementLevel.ORDINAL
    assert QUESTION.is_value_code(3) and not QUESTION.is_value_code(4)
    QUESTION.validate(BestWorstChoice(best=3, worst=1))


@pytest.mark.parametrize(("best", "worst"), [(4, 1), (1, 4), (4, 5)])
def test_rejects_unknown_codes(best: int, worst: int) -> None:
    with pytest.raises(InvalidAnswerError):
        QUESTION.validate(BestWorstChoice(best=best, worst=worst))


@pytest.mark.parametrize(
    "options",
    [
        ChoiceOptions.from_labels(["A", "B"]),
        ChoiceOptions(
            (
                ChoiceOption(1, "A"),
                ChoiceOption(2, "B"),
                ChoiceOption(3, "None", is_exclusive=True),
            )
        ),
        ChoiceOptions(
            (
                ChoiceOption(1, "A"),
                ChoiceOption(2, "B"),
                ChoiceOption(3, "Other", is_free_text_allowed=True),
            )
        ),
    ],
)
def test_rejects_invalid_options(options: ChoiceOptions) -> None:
    with pytest.raises(ValueError):
        BestWorstQuestion(id="Q1", text="T", options=options)
