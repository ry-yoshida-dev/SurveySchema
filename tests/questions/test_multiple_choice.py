import pytest

from survey_schema import (
    ChoiceOption,
    ChoiceOptions,
    ChoiceSelection,
    InvalidAnswerError,
    MultipleChoiceQuestion,
)

OPTIONS = ChoiceOptions(
    (
        ChoiceOption(1, "A"),
        ChoiceOption(2, "B"),
        ChoiceOption(3, "C"),
        ChoiceOption(9, "None", is_exclusive=True),
    )
)
QUESTION = MultipleChoiceQuestion(
    id="Q1", text="Pick", options=OPTIONS, max_selections=2
)


def test_accepts_valid_selection() -> None:
    QUESTION.validate((ChoiceSelection(1), ChoiceSelection(2)))
    QUESTION.validate((ChoiceSelection(9),))
    assert QUESTION.is_value(()) and not QUESTION.is_value(ChoiceSelection(1))


@pytest.mark.parametrize(
    "codes",
    [(), (1, 1), (1, 2, 3), (1, 9), (5,)],
)
def test_rejects_invalid_selection(codes: tuple[int, ...]) -> None:
    with pytest.raises(InvalidAnswerError):
        QUESTION.validate(tuple(ChoiceSelection(code) for code in codes))


def test_rejects_invalid_limits() -> None:
    with pytest.raises(ValueError):
        MultipleChoiceQuestion(id="Q1", text="T", options=OPTIONS, min_selections=0)
    with pytest.raises(ValueError):
        MultipleChoiceQuestion(
            id="Q1", text="T", options=OPTIONS, min_selections=3, max_selections=2
        )


def test_exclusive_option_alone_bypasses_min_selections() -> None:
    question = MultipleChoiceQuestion(
        id="Q1", text="Pick", options=OPTIONS, min_selections=2
    )
    question.validate((ChoiceSelection(9),))
    question.validate((ChoiceSelection(1), ChoiceSelection(3)))
    with pytest.raises(InvalidAnswerError):
        question.validate((ChoiceSelection(1),))
    with pytest.raises(InvalidAnswerError):
        question.validate((ChoiceSelection(1), ChoiceSelection(9)))


def test_limits_count_only_combinable_options() -> None:
    MultipleChoiceQuestion(id="Q1", text="T", options=OPTIONS, max_selections=3)
    with pytest.raises(ValueError):
        MultipleChoiceQuestion(id="Q1", text="T", options=OPTIONS, max_selections=4)
    with pytest.raises(ValueError):
        MultipleChoiceQuestion(id="Q1", text="T", options=OPTIONS, min_selections=4)


def test_min_selections_cannot_need_exclusive_option() -> None:
    options = ChoiceOptions(
        (
            ChoiceOption(1, "A"),
            ChoiceOption(2, "B"),
            ChoiceOption(9, "None", is_exclusive=True),
        )
    )
    MultipleChoiceQuestion(id="Q1", text="T", options=options, min_selections=2)
    with pytest.raises(ValueError):
        MultipleChoiceQuestion(id="Q1", text="T", options=options, min_selections=3)
