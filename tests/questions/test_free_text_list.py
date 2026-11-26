import pytest

from survey_schema import ChoiceSelection, FreeTextListQuestion, InvalidAnswerError

QUESTION = FreeTextListQuestion(
    id="Q1", text="Brands", max_entries=3, min_entries=2, max_length=5
)


def test_value_and_validation() -> None:
    assert QUESTION.is_value(("A", "B")) and QUESTION.is_value(())
    assert not QUESTION.is_value("A") and not QUESTION.is_value((ChoiceSelection(1),))
    assert QUESTION.measurement_level is None
    QUESTION.validate(("Sony", "Canon"))
    QUESTION.validate(("Sony", "Canon", "Nikon"))


@pytest.mark.parametrize(
    "value",
    [
        ("Sony",),
        ("A", "B", "C", "D"),
        ("Sony", " "),
        ("Sony", "Panasonic"),
        ("Sony", " Sony "),
    ],
)
def test_rejects_invalid_entries(value: tuple[str, ...]) -> None:
    with pytest.raises(InvalidAnswerError):
        QUESTION.validate(value)


def test_repetition_allowed() -> None:
    question = FreeTextListQuestion(
        id="Q1", text="T", max_entries=2, is_repetition_allowed=True
    )
    question.validate(("Sony", "Sony"))


@pytest.mark.parametrize(
    ("min_entries", "max_entries", "max_length"),
    [(0, 3, None), (4, 3, None), (1, 3, 0)],
)
def test_rejects_invalid_definitions(
    min_entries: int, max_entries: int, max_length: int | None
) -> None:
    with pytest.raises(ValueError):
        FreeTextListQuestion(
            id="Q1",
            text="T",
            min_entries=min_entries,
            max_entries=max_entries,
            max_length=max_length,
        )
