from decimal import Decimal

from survey_schema import ChoiceSelection, OptionAmount


def test_fields_and_equality() -> None:
    amount = OptionAmount(ChoiceSelection(3, "Books"), Decimal("30"))
    assert amount.selection.free_text == "Books"
    assert amount == OptionAmount(ChoiceSelection(3, "Books"), Decimal("30.0"))
