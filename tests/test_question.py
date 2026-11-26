import pytest

from survey_schema import (
    Answer,
    AnswerStatus,
    Bounds,
    ChoiceOptions,
    ChoiceSelection,
    DateQuestion,
    IntegerQuestion,
    InvalidAnswerError,
    SingleChoiceQuestion,
    SpecialResponse,
    SpecialResponseKind,
    SpecialResponses,
)

DONT_KNOW = SpecialResponses(
    (SpecialResponse(99, "Don't know", SpecialResponseKind.DONT_KNOW),)
)
AGE = IntegerQuestion(
    id="Q1", text="Age", bounds=Bounds(maximum=98), special_responses=DONT_KNOW
)


def test_rejects_blank_id_and_text() -> None:
    with pytest.raises(ValueError):
        IntegerQuestion(id=" ", text="Age")
    with pytest.raises(ValueError):
        IntegerQuestion(id="Q1", text=" ")


def test_rejects_special_code_used_by_answers() -> None:
    with pytest.raises(ValueError):
        SingleChoiceQuestion(
            id="Q1",
            text="Pick",
            options=ChoiceOptions.from_labels(["A", "B"]),
            special_responses=SpecialResponses(
                (SpecialResponse(2, "Refused", SpecialResponseKind.REFUSED),)
            ),
        )


def test_check_accepts_offered_special_response_only() -> None:
    AGE.check(Answer.special(99))
    with pytest.raises(InvalidAnswerError):
        AGE.check(Answer.special(98))


def test_check_rejects_wrong_type_and_passes_missing() -> None:
    with pytest.raises(TypeError):
        AGE.check(Answer.answered("forty"))
    AGE.check(Answer.missing(AnswerStatus.UNREADABLE))


def test_check_passes_captured_content_of_unusable_answers() -> None:
    AGE.check(Answer.invalid((ChoiceSelection(1), ChoiceSelection(2))))
    AGE.check(Answer.invalid(200, transcription="200"))
    AGE.check(Answer.unreadable("4?"))


def test_check_validates_value() -> None:
    AGE.check(Answer.answered(40))
    with pytest.raises(InvalidAnswerError):
        AGE.check(Answer.answered(99))


def test_types_without_integer_answers_have_no_value_codes() -> None:
    assert not DateQuestion(id="Q1", text="T").is_value_code(1)


def test_answer_validates() -> None:
    assert AGE.answer(40).value == 40
    with pytest.raises(InvalidAnswerError):
        AGE.answer(99)
