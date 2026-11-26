import pytest

from survey_schema import (
    ChoiceOption,
    ChoiceOptions,
    ChoiceSelection,
    InvalidAnswerError,
)

OPTIONS = ChoiceOptions(
    (
        ChoiceOption(1, "A"),
        ChoiceOption(2, "Other", is_free_text_allowed=True),
    )
)


def test_lookup() -> None:
    assert OPTIONS.codes == (1, 2)
    assert OPTIONS[2].is_free_text_allowed
    assert 1 in OPTIONS and 3 not in OPTIONS
    assert len(OPTIONS) == 2
    assert OPTIONS.is_free_text_included and not OPTIONS.is_exclusive_included


def test_from_labels() -> None:
    assert ChoiceOptions.from_labels(["A", "B"], start=0).codes == (0, 1)


def test_rejects_invalid_definitions() -> None:
    with pytest.raises(ValueError):
        ChoiceOptions((ChoiceOption(1, "A"),))
    with pytest.raises(ValueError):
        ChoiceOptions((ChoiceOption(1, "A"), ChoiceOption(1, "B")))
    with pytest.raises(ValueError):
        ChoiceOptions((ChoiceOption(1, "A"), ChoiceOption(2, "A")))
    with pytest.raises(TypeError):
        ChoiceOption(True, "A")
    with pytest.raises(ValueError):
        ChoiceOption(1, " ")


def test_validate() -> None:
    OPTIONS.validate(ChoiceSelection(2, "Books"))
    with pytest.raises(InvalidAnswerError):
        OPTIONS.validate(ChoiceSelection(3))
    with pytest.raises(InvalidAnswerError):
        OPTIONS.validate(ChoiceSelection(1, "text"))


def test_required_free_text() -> None:
    options = ChoiceOptions(
        (
            ChoiceOption(1, "A"),
            ChoiceOption(
                2, "Other", is_free_text_allowed=True, is_free_text_required=True
            ),
        )
    )
    options.validate(ChoiceSelection(2, "Books"))
    options.validate(ChoiceSelection(1))
    with pytest.raises(InvalidAnswerError):
        options.validate(ChoiceSelection(2))
    with pytest.raises(ValueError):
        ChoiceOption(2, "Other", is_free_text_required=True)


def test_yes_no() -> None:
    options = ChoiceOptions.yes_no()
    assert options.codes == (1, 2)
    assert [option.label for option in options] == ["Yes", "No"]
