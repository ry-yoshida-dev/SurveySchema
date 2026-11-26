import pytest

from survey_schema import Answer, AnswerStatus, ChoiceSelection

MISSING_STATUSES = [
    AnswerStatus.NO_ANSWER,
    AnswerStatus.NOT_APPLICABLE,
    AnswerStatus.NOT_REACHED,
    AnswerStatus.INVALID,
    AnswerStatus.UNREADABLE,
]


def test_factories() -> None:
    assert Answer.answered(3).is_answered
    special = Answer.special(9)
    assert special.status is AnswerStatus.SPECIAL_RESPONSE and special.special_code == 9
    assert not Answer.missing(AnswerStatus.NO_ANSWER).is_answered


def test_invalid_keeps_captured_content() -> None:
    marks = (ChoiceSelection(1), ChoiceSelection(3))
    invalid = Answer.invalid(marks, transcription="1 and 3")
    assert invalid.status is AnswerStatus.INVALID
    assert invalid.raw_value == marks and invalid.transcription == "1 and 3"
    assert invalid.value is None and invalid.special_code is None
    assert Answer.invalid().raw_value is None
    assert Answer.invalid(transcription="12.5").transcription == "12.5"


def test_unreadable_keeps_transcription() -> None:
    unreadable = Answer.unreadable("1?5")
    assert unreadable.status is AnswerStatus.UNREADABLE
    assert unreadable.transcription == "1?5" and unreadable.raw_value is None
    assert Answer.unreadable().transcription is None


@pytest.mark.parametrize(
    ("answer", "is_given"),
    [
        (Answer.answered(1), True),
        (Answer.special(9), True),
        *((Answer.missing(status), False) for status in MISSING_STATUSES),
        (Answer.invalid(2, transcription="2?"), False),
    ],
)
def test_is_given(answer: Answer[int], is_given: bool) -> None:
    assert answer.is_given is is_given


@pytest.mark.parametrize(
    "status", [AnswerStatus.ANSWERED, AnswerStatus.SPECIAL_RESPONSE]
)
def test_missing_rejects_statuses_with_content(status: AnswerStatus) -> None:
    with pytest.raises(ValueError):
        Answer.missing(status)


def test_rejects_mismatched_fields() -> None:
    with pytest.raises(ValueError):
        Answer(status=AnswerStatus.NO_ANSWER, value=1)
    with pytest.raises(ValueError):
        Answer(status=AnswerStatus.ANSWERED, value=1, special_code=9)
    with pytest.raises(ValueError):
        Answer(status=AnswerStatus.NO_ANSWER, special_code=9)


@pytest.mark.parametrize(
    "status",
    [
        AnswerStatus.NO_ANSWER,
        AnswerStatus.NOT_APPLICABLE,
        AnswerStatus.NOT_REACHED,
        AnswerStatus.UNREADABLE,
    ],
)
def test_raw_value_only_for_invalid(status: AnswerStatus) -> None:
    with pytest.raises(ValueError):
        Answer(status=status, raw_value=1)


def test_raw_value_rejected_with_value_or_special_code() -> None:
    with pytest.raises(ValueError):
        Answer(status=AnswerStatus.ANSWERED, value=1, raw_value=2)
    with pytest.raises(ValueError):
        Answer(status=AnswerStatus.SPECIAL_RESPONSE, special_code=9, raw_value=2)


@pytest.mark.parametrize(
    "status",
    [AnswerStatus.NO_ANSWER, AnswerStatus.NOT_APPLICABLE, AnswerStatus.NOT_REACHED],
)
def test_transcription_only_for_invalid_or_unreadable(status: AnswerStatus) -> None:
    with pytest.raises(ValueError):
        Answer(status=status, transcription="text")


def test_transcription_rejected_with_value_or_special_code() -> None:
    with pytest.raises(ValueError):
        Answer(status=AnswerStatus.ANSWERED, value=1, transcription="1")
    with pytest.raises(ValueError):
        Answer(status=AnswerStatus.SPECIAL_RESPONSE, special_code=9, transcription="9")


@pytest.mark.parametrize("transcription", ["", " ", "\n\t"])
def test_rejects_blank_transcription(transcription: str) -> None:
    with pytest.raises(ValueError):
        Answer.invalid(transcription=transcription)
    with pytest.raises(ValueError):
        Answer.unreadable(transcription)


def test_special_rejects_bool_code() -> None:
    with pytest.raises(TypeError):
        Answer.special(True)
