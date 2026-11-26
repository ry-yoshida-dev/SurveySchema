import pytest

from survey_schema import (
    ChoiceOption,
    ChoiceOptions,
    ChoiceSelection,
    InvalidAnswerError,
    MeasurementLevel,
    SingleChoiceQuestion,
)

OPTIONS = ChoiceOptions.from_labels(["Low", "Mid", "High"])
WITH_OTHER = ChoiceOptions(
    (ChoiceOption(1, "A"), ChoiceOption(2, "Other", is_free_text_allowed=True))
)


def test_value_and_validation() -> None:
    question = SingleChoiceQuestion(id="Q1", text="Level", options=OPTIONS)
    assert question.is_value(ChoiceSelection(1))
    assert not question.is_value((ChoiceSelection(1),))
    assert all(question.is_value_code(code) for code in (1, 2, 3))
    assert not question.is_value_code(0) and not question.is_value_code(4)
    with pytest.raises(InvalidAnswerError):
        question.validate(ChoiceSelection(4))


def test_yes_no() -> None:
    question = SingleChoiceQuestion(
        id="Q1", text="Agree?", options=ChoiceOptions.yes_no(yes="I agree")
    )
    assert question.options.codes == (1, 2)
    assert question.options[1].label == "I agree" and question.options[2].label == "No"
    question.validate(ChoiceSelection(2))


def test_measurement_level_follows_order() -> None:
    nominal = SingleChoiceQuestion(id="Q1", text="Level", options=OPTIONS)
    ordinal = SingleChoiceQuestion(
        id="Q1", text="Level", options=OPTIONS, is_ordered=True
    )
    assert nominal.measurement_level is MeasurementLevel.NOMINAL
    assert ordinal.measurement_level is MeasurementLevel.ORDINAL


def test_free_text_option() -> None:
    question = SingleChoiceQuestion(id="Q1", text="T", options=WITH_OTHER)
    question.validate(ChoiceSelection(2, "Books"))
    with pytest.raises(InvalidAnswerError):
        question.validate(ChoiceSelection(1, "Books"))


def test_rejects_invalid_definitions() -> None:
    with pytest.raises(ValueError):
        SingleChoiceQuestion(
            id="Q1",
            text="T",
            options=ChoiceOptions(
                (ChoiceOption(1, "A"), ChoiceOption(2, "None", is_exclusive=True))
            ),
        )
    with pytest.raises(ValueError):
        SingleChoiceQuestion(id="Q1", text="T", options=WITH_OTHER, is_ordered=True)
