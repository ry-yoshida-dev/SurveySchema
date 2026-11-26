from dataclasses import dataclass
from decimal import MAX_PREC, Decimal, localcontext
from typing import ClassVar, TypeGuard, override

from variable import MeasurementLevel

from ..answer.error import InvalidAnswerError
from ..answer.option_amount import OptionAmount
from ..answer.value import AnswerValue
from ..choice.options import ChoiceOptions
from ..decimal_places import count_decimal_places
from ..question import Question
from ..question_type import QuestionType


@dataclass(frozen=True, kw_only=True)
class ConstantSumQuestion(Question[tuple[OptionAmount, ...]]):
    """
    Question answered by distributing a fixed total across options, such as ``Split 100 points``.

    The answer is a ``tuple[OptionAmount, ...]`` in any order; omitted options count as zero.

    Parameters
    ----------
    options : ChoiceOptions
        Options that receive amounts. They cannot be exclusive, but ``Other (please specify)``
        may have a field to write in.
    total : Decimal
        Amount that the answer must add up to exactly.
    decimal_places : int
        Most digits accepted after the decimal point of each amount, such as 1 for ``33.3%``.
    unit : str | None
        Unit of the amounts, such as ``points`` or ``%``. ``None`` for unitless amounts.

    Raises
    ------
    ValueError
        If an option is exclusive, ``total`` is not positive and finite or has more decimal
        places than allowed, ``decimal_places`` is negative, or ``unit`` is blank.
    """

    question_type: ClassVar[QuestionType] = QuestionType.CONSTANT_SUM

    options: ChoiceOptions
    total: Decimal
    decimal_places: int = 0
    unit: str | None = None

    def __post_init__(self) -> None:
        # Fields are checked before the base class compares special-response codes with them.
        if self.options.is_exclusive_included:
            raise ValueError(
                f"Options of constant-sum question {self.id} cannot be exclusive."
            )
        if self.decimal_places < 0:
            raise ValueError(
                f"decimal_places of question {self.id} must not be negative."
            )
        if not (self.total.is_finite() and self.total > 0):
            raise ValueError(
                f"total of question {self.id} must be positive and finite."
            )
        if count_decimal_places(self.total) > self.decimal_places:
            raise ValueError(
                f"total of question {self.id} has more than {self.decimal_places} decimal places."
            )
        if self.unit is not None and not self.unit.strip():
            raise ValueError(f"unit of question {self.id} must not be blank.")
        super().__post_init__()

    @override
    def is_value_code(self, code: int) -> bool:
        """
        Whether the code is an option code or could be an amount, from zero to the total.
        """
        return code in self.options or 0 <= code <= self.total

    @property
    @override
    def measurement_level(self) -> MeasurementLevel:
        """
        Always ``RATIO``.
        """
        return MeasurementLevel.RATIO

    @override
    def is_value(self, value: AnswerValue) -> TypeGuard[tuple[OptionAmount, ...]]:
        """
        Whether the value is a tuple of ``OptionAmount``.
        """
        return isinstance(value, tuple) and all(
            isinstance(item, OptionAmount) for item in value
        )

    @override
    def validate(self, value: tuple[OptionAmount, ...]) -> None:
        """
        Check the options, the amounts, and that they add up to the total.

        Raises
        ------
        InvalidAnswerError
            If an option is unknown, repeated, or given text without a field or without an
            amount, an amount is negative, not finite, or too precise, or the sum differs from
            :attr:`total`.
        """
        for entry in value:
            self.options.validate(entry.selection)
            if not entry.amount.is_finite() or entry.amount < 0:
                raise InvalidAnswerError(
                    f"Amount {entry.amount} of question {self.id} must be finite and not negative."
                )
            if count_decimal_places(entry.amount) > self.decimal_places:
                raise InvalidAnswerError(
                    f"Amount {entry.amount} of question {self.id} has more than {self.decimal_places} decimal places."
                )
            if entry.selection.free_text is not None and entry.amount == 0:
                raise InvalidAnswerError(
                    f"Option {entry.selection.code} of question {self.id} has text but no amount."
                )
        codes = [entry.selection.code for entry in value]
        if len(set(codes)) != len(codes):
            raise InvalidAnswerError(f"Options {codes} of question {self.id} repeat.")
        # Add exactly: the default context would round past 28 significant digits.
        with localcontext(prec=MAX_PREC):
            amount_sum = sum((entry.amount for entry in value), Decimal(0))
        if amount_sum != self.total:
            raise InvalidAnswerError(
                f"Amounts of question {self.id} add up to {amount_sum}, not {self.total}."
            )
