from decimal import Decimal

import pytest

from survey_schema import (
    ChoiceOption,
    ChoiceOptions,
    ChoiceSelection,
    ConstantSumQuestion,
    InvalidAnswerError,
    MeasurementLevel,
    OptionAmount,
    SpecialResponse,
    SpecialResponseKind,
    SpecialResponses,
)

OPTIONS = ChoiceOptions(
    (
        ChoiceOption(1, "A"),
        ChoiceOption(2, "B"),
        ChoiceOption(3, "Other", is_free_text_allowed=True),
    )
)
QUESTION = ConstantSumQuestion(
    id="Q1", text="Split", options=OPTIONS, total=Decimal(100), unit="%"
)
PRECISE = ConstantSumQuestion(
    id="Q1", text="Split", options=OPTIONS, total=Decimal(100), decimal_places=1
)


def _amount(code: int, amount: str, free_text: str | None = None) -> OptionAmount:
    return OptionAmount(ChoiceSelection(code, free_text), Decimal(amount))


def _special(code: int) -> SpecialResponses:
    return SpecialResponses(
        (SpecialResponse(code, "Refused", SpecialResponseKind.REFUSED),)
    )


def test_accepts_total_with_omitted_options() -> None:
    QUESTION.validate((_amount(1, "100"),))
    QUESTION.validate((_amount(2, "70"), _amount(1, "30")))
    QUESTION.validate((_amount(1, "0"), _amount(3, "100", "Books")))
    QUESTION.validate((_amount(1, "100.00"),))
    PRECISE.validate((_amount(1, "33.3"), _amount(2, "33.3"), _amount(3, "33.4")))
    assert QUESTION.is_value((_amount(1, "2"),)) and QUESTION.is_value(())
    assert not QUESTION.is_value((ChoiceSelection(1),))
    assert QUESTION.measurement_level is MeasurementLevel.RATIO


@pytest.mark.parametrize(
    "value",
    [
        (_amount(1, "50"),),
        (_amount(1, "120"), _amount(2, "-20")),
        (_amount(4, "100"),),
        (_amount(1, "50"), _amount(1, "50")),
        (_amount(1, "50.5"), _amount(2, "49.5")),
        (_amount(1, "Infinity"),),
        (_amount(1, "NaN"),),
        (_amount(1, "100", "text"),),
        (_amount(1, "100"), _amount(3, "0", "Books")),
        (),
    ],
)
def test_rejects_invalid_amounts(value: tuple[OptionAmount, ...]) -> None:
    with pytest.raises(InvalidAnswerError):
        QUESTION.validate(value)


def test_is_value_code_covers_zero_to_total() -> None:
    assert QUESTION.is_value_code(0) and QUESTION.is_value_code(100)
    assert not QUESTION.is_value_code(-1) and not QUESTION.is_value_code(101)
    ConstantSumQuestion(
        id="Q1",
        text="T",
        options=OPTIONS,
        total=Decimal(100),
        special_responses=_special(999),
    )
    with pytest.raises(ValueError):
        ConstantSumQuestion(
            id="Q1",
            text="T",
            options=OPTIONS,
            total=Decimal(100),
            special_responses=_special(99),
        )


@pytest.mark.parametrize(
    ("total", "decimal_places"),
    [("0", 0), ("-10", 0), ("Infinity", 0), ("NaN", 0), ("100.5", 0), ("10", -1)],
)
def test_rejects_invalid_totals(total: str, decimal_places: int) -> None:
    with pytest.raises(ValueError):
        ConstantSumQuestion(
            id="Q1",
            text="T",
            options=OPTIONS,
            total=Decimal(total),
            decimal_places=decimal_places,
        )


def test_rejects_invalid_definitions() -> None:
    with pytest.raises(ValueError):
        ConstantSumQuestion(
            id="Q1", text="T", options=OPTIONS, total=Decimal(10), unit=" "
        )
    with pytest.raises(ValueError):
        ConstantSumQuestion(
            id="Q1",
            text="T",
            options=ChoiceOptions(
                (ChoiceOption(1, "A"), ChoiceOption(2, "None", is_exclusive=True))
            ),
            total=Decimal(10),
        )


def test_rejects_nan_total_with_special_responses() -> None:
    with pytest.raises(ValueError):
        ConstantSumQuestion(
            id="Q1",
            text="T",
            options=OPTIONS,
            total=Decimal("NaN"),
            special_responses=_special(999),
        )


def test_option_codes_are_value_codes() -> None:
    question = ConstantSumQuestion(
        id="Q1",
        text="T",
        options=ChoiceOptions.from_labels(["A", "B"], start=101),
        total=Decimal(10),
    )
    assert question.is_value_code(101) and question.is_value_code(5)
    assert not question.is_value_code(50)


def test_sum_is_exact_beyond_context_precision() -> None:
    tiny = "0." + "0" * 30 + "1"
    question = ConstantSumQuestion(
        id="Q1", text="T", options=OPTIONS, total=Decimal(1), decimal_places=31
    )
    with pytest.raises(InvalidAnswerError):
        question.validate((_amount(1, "1"), _amount(2, tiny)))


def test_sum_does_not_round_at_28_digits() -> None:
    question = ConstantSumQuestion(
        id="Q1", text="T", options=OPTIONS, total=Decimal(100), decimal_places=28
    )
    with pytest.raises(InvalidAnswerError):
        question.validate(
            (_amount(1, "1.0000000000000000000000000001"), _amount(2, "99"))
        )
