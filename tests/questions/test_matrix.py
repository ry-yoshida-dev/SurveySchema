from datetime import date

import pytest

from survey_schema import (
    Answer,
    AnswerStatus,
    ChoiceOptions,
    ChoiceSelection,
    DateQuestion,
    IntegerQuestion,
    InvalidAnswerError,
    MatrixAnswer,
    MatrixQuestion,
    MeasurementLevel,
    RatingScale,
    RatingScaleQuestion,
    SingleChoiceQuestion,
    SpecialResponse,
    SpecialResponseKind,
    SpecialResponses,
)

DONT_KNOW = SpecialResponses(
    (SpecialResponse(9, "Don't know", SpecialResponseKind.DONT_KNOW),)
)
TEMPLATE = RatingScaleQuestion(
    id="T",
    text="T",
    scale=RatingScale(minimum=1, maximum=5),
    special_responses=DONT_KNOW,
)
ROWS = [("Q1_1", "Price"), ("Q1_2", "Quality"), ("Q1_3", "Service")]
QUESTION = MatrixQuestion[int].from_rows(
    id="Q1", text="Rate", template=TEMPLATE, rows=ROWS, min_answered_items=2
)


def test_from_rows() -> None:
    assert QUESTION.item_ids == ("Q1_1", "Q1_2", "Q1_3")
    assert [item.text for item in QUESTION.items] == ["Price", "Quality", "Service"]
    assert all(item.special_responses == DONT_KNOW for item in QUESTION.items)
    assert len(QUESTION.special_responses) == 0
    assert QUESTION.measurement_level is MeasurementLevel.ORDINAL
    assert QUESTION.min_answered_items == 2


def test_from_rows_special_responses() -> None:
    refused = SpecialResponses(
        (SpecialResponse(99, "Refused", SpecialResponseKind.REFUSED),)
    )
    question = MatrixQuestion[int].from_rows(
        id="Q1", text="Rate", template=TEMPLATE, rows=ROWS, special_responses=refused
    )
    assert question.special_responses == refused
    question.check(Answer.special(99))


def test_direct_construction() -> None:
    question = MatrixQuestion(
        id="Q2",
        text="Dates",
        items=(DateQuestion(id="Q2_1", text="A"), DateQuestion(id="Q2_2", text="B")),
    )
    question.validate(MatrixAnswer({"Q2_1": Answer.answered(date(2026, 1, 1))}))
    assert question.measurement_level is MeasurementLevel.INTERVAL


@pytest.mark.parametrize(
    "items",
    [
        {"Q1_1": Answer.answered(5), "Q1_2": Answer.answered(1)},
        {"Q1_1": Answer.answered(5), "Q1_2": Answer.special(9)},
        {
            "Q1_1": Answer.answered(5),
            "Q1_2": Answer.missing(AnswerStatus.NO_ANSWER),
            "Q1_3": Answer.special(9),
        },
    ],
)
def test_accepts_valid_answers(items: dict[str, Answer[int]]) -> None:
    QUESTION.validate(MatrixAnswer(items))
    QUESTION.check(Answer.answered(MatrixAnswer(items)))
    assert QUESTION.is_value(MatrixAnswer(items))


@pytest.mark.parametrize(
    "items",
    [
        {},
        {"Q1_1": Answer.answered(5)},
        {"Q1_1": Answer.answered(5), "Q1_2": Answer.invalid(transcription="6")},
        {"Q1_1": Answer.answered(5), "Q1_2": Answer.answered(6)},
        {"Q1_1": Answer.answered(5), "Q1_2": Answer.special(8)},
        {
            "Q1_1": Answer.answered(5),
            "Q1_2": Answer.answered(1),
            "Q9": Answer.answered(1),
        },
    ],
)
def test_rejects_invalid_answers(items: dict[str, Answer[int]]) -> None:
    with pytest.raises(InvalidAnswerError):
        QUESTION.validate(MatrixAnswer(items))


def test_rejects_wrong_item_type() -> None:
    with pytest.raises(TypeError):
        QUESTION.validate(
            MatrixAnswer({"Q1_1": Answer.answered("5"), "Q1_2": Answer.answered(1)})
        )
    assert not QUESTION.is_value(5)


def test_rejects_too_few_or_nested_items() -> None:
    with pytest.raises(ValueError):
        MatrixQuestion[int].from_rows(
            id="Q1", text="T", template=TEMPLATE, rows=ROWS[:1]
        )
    with pytest.raises(ValueError):
        MatrixQuestion[MatrixAnswer](id="Q2", text="T", items=(QUESTION, QUESTION))


@pytest.mark.parametrize(
    "rows",
    [
        [("Q1_1", "A"), ("Q1_1", "B")],
        [("Q1", "A"), ("Q1_2", "B")],
    ],
)
def test_rejects_repeated_item_ids(rows: list[tuple[str, str]]) -> None:
    with pytest.raises(ValueError):
        MatrixQuestion[int].from_rows(id="Q1", text="T", template=TEMPLATE, rows=rows)


@pytest.mark.parametrize("min_answered_items", [0, 4])
def test_rejects_invalid_min_answered_items(min_answered_items: int) -> None:
    with pytest.raises(ValueError):
        MatrixQuestion[int].from_rows(
            id="Q1",
            text="T",
            template=TEMPLATE,
            rows=ROWS,
            min_answered_items=min_answered_items,
        )


def test_rejects_items_with_different_formats() -> None:
    with pytest.raises(ValueError):
        MatrixQuestion(
            id="Q1",
            text="T",
            items=(
                RatingScaleQuestion(
                    id="A", text="A", scale=RatingScale(minimum=1, maximum=5)
                ),
                RatingScaleQuestion(
                    id="B", text="B", scale=RatingScale(minimum=1, maximum=7)
                ),
            ),
        )
    with pytest.raises(ValueError):
        MatrixQuestion[int](
            id="Q1",
            text="T",
            items=(
                IntegerQuestion(id="A", text="A"),
                RatingScaleQuestion(
                    id="B", text="B", scale=RatingScale(minimum=1, maximum=5)
                ),
            ),
        )
    with pytest.raises(ValueError):
        MatrixQuestion(
            id="Q1",
            text="T",
            items=(
                SingleChoiceQuestion(id="A", text="A", options=ChoiceOptions.yes_no()),
                SingleChoiceQuestion(
                    id="B",
                    text="B",
                    options=ChoiceOptions.yes_no(),
                    special_responses=DONT_KNOW,
                ),
            ),
        )


def test_single_choice_grid() -> None:
    question = MatrixQuestion[ChoiceSelection].from_rows(
        id="Q3",
        text="Used?",
        template=SingleChoiceQuestion(id="T", text="T", options=ChoiceOptions.yes_no()),
        rows=[("Q3_1", "A"), ("Q3_2", "B")],
    )
    question.validate(MatrixAnswer({"Q3_2": Answer.answered(ChoiceSelection(1))}))
    with pytest.raises(InvalidAnswerError):
        question.validate(MatrixAnswer({"Q3_1": Answer.answered(ChoiceSelection(3))}))


def _matrix_special(code: int) -> SpecialResponses:
    return SpecialResponses(
        (SpecialResponse(code, "Refused", SpecialResponseKind.REFUSED),)
    )


@pytest.mark.parametrize(("code", "is_value_code"), [(3, True), (9, True), (99, False)])
def test_matrix_special_codes_must_differ_from_item_codes(
    code: int, is_value_code: bool
) -> None:
    assert QUESTION.is_value_code(code) is is_value_code
    if is_value_code:
        with pytest.raises(ValueError):
            MatrixQuestion[int].from_rows(
                id="Q1",
                text="T",
                template=TEMPLATE,
                rows=ROWS,
                special_responses=_matrix_special(code),
            )


def test_is_value_checks_recorded_item_types() -> None:
    assert QUESTION.is_value(MatrixAnswer({"Q1_1": Answer.answered(1)}))
    assert QUESTION.is_value(MatrixAnswer({"Q1_1": Answer.special(9)}))
    assert not QUESTION.is_value(MatrixAnswer({"Q1_1": Answer.answered("1")}))
    with pytest.raises(TypeError):
        QUESTION.check(
            Answer.answered(
                MatrixAnswer({"Q1_1": Answer.answered("1"), "Q1_2": Answer.answered(1)})
            )
        )
