from dataclasses import dataclass
from decimal import Decimal

from .selection import ChoiceSelection


@dataclass(frozen=True)
class OptionAmount:
    """
    Amount that a respondent gives to one option of a constant-sum question.

    Parameters
    ----------
    selection : ChoiceSelection
        Option given the amount, with the text entered in its field, such as the content of ``Other``.
    amount : Decimal
        Amount given, such as ``Decimal("30")`` points or ``Decimal("33.3")`` percent.
    """

    selection: ChoiceSelection
    amount: Decimal
