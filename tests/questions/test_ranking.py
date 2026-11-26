import pytest

from survey_schema import (
    ChoiceOption,
    ChoiceOptions,
    ChoiceSelection,
    InvalidAnswerError,
    MeasurementLevel,
    RankingQuestion,
)

OPTIONS = ChoiceOptions(
    (
        ChoiceOption(1, "A"),
        ChoiceOption(2, "B"),
        ChoiceOption(3, "C"),
        ChoiceOption(4, "Other", is_free_text_allowed=True),
    )
)
FULL = RankingQuestion(id="Q1", text="Rank", options=OPTIONS)
TOP_TWO = RankingQuestion(id="Q1", text="Rank", options=OPTIONS, max_ranks=2)
UP_TO_TWO = RankingQuestion(
    id="Q1", text="Rank", options=OPTIONS, min_ranks=1, max_ranks=2
)
AT_LEAST_TWO = RankingQuestion(id="Q1", text="Rank", options=OPTIONS, min_ranks=2)


def _ranks(*codes: int) -> tuple[ChoiceSelection, ...]:
    return tuple(ChoiceSelection(code) for code in codes)


@pytest.mark.parametrize(
    ("question", "minimum", "maximum"),
    [(FULL, 4, 4), (TOP_TWO, 2, 2), (UP_TO_TWO, 1, 2), (AT_LEAST_TWO, 2, 4)],
)
def test_required_limits(question: RankingQuestion, minimum: int, maximum: int) -> None:
    assert question.required_min_ranks == minimum
    assert question.required_max_ranks == maximum


def test_accepts_valid_rankings() -> None:
    FULL.validate((ChoiceSelection(4, "Books"), *_ranks(3, 1, 2)))
    TOP_TWO.validate(_ranks(2, 1))
    UP_TO_TWO.validate(_ranks(3))
    AT_LEAST_TWO.validate(_ranks(1, 2, 3))
    assert FULL.is_value(_ranks(1, 2)) and not FULL.is_value(("1", "2"))
    assert FULL.measurement_level is MeasurementLevel.ORDINAL
    assert FULL.is_value_code(4) and not FULL.is_value_code(5)


@pytest.mark.parametrize(
    ("question", "value"),
    [
        (FULL, _ranks(1, 2, 3)),
        (FULL, _ranks(1, 1, 2, 3)),
        (FULL, _ranks(1, 2, 3, 5)),
        (FULL, (ChoiceSelection(1, "text"), *_ranks(2, 3, 4))),
        (TOP_TWO, _ranks(1)),
        (TOP_TWO, _ranks(1, 2, 3)),
        (UP_TO_TWO, ()),
        (AT_LEAST_TWO, _ranks(1)),
    ],
)
def test_rejects_invalid_ranking(
    question: RankingQuestion, value: tuple[ChoiceSelection, ...]
) -> None:
    with pytest.raises(InvalidAnswerError):
        question.validate(value)


@pytest.mark.parametrize(
    ("min_ranks", "max_ranks"), [(None, 5), (0, None), (3, 2), (5, None), (None, 0)]
)
def test_rejects_invalid_limits(min_ranks: int | None, max_ranks: int | None) -> None:
    with pytest.raises(ValueError):
        RankingQuestion(
            id="Q1",
            text="Rank",
            options=OPTIONS,
            min_ranks=min_ranks,
            max_ranks=max_ranks,
        )


def test_rejects_exclusive_option() -> None:
    with pytest.raises(ValueError):
        RankingQuestion(
            id="Q1",
            text="Rank",
            options=ChoiceOptions(
                (ChoiceOption(1, "A"), ChoiceOption(2, "None", is_exclusive=True))
            ),
        )
