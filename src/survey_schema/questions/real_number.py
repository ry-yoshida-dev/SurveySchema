from dataclasses import dataclass, field
from decimal import Decimal
from typing import ClassVar, TypeGuard, override

from variable import MeasurementLevel

from ..answer.error import InvalidAnswerError
from ..answer.value import AnswerValue
from ..bounds import Bounds
from ..decimal_places import count_decimal_places
from ..question import Question
from ..question_type import QuestionType


@dataclass(frozen=True, kw_only=True)
class RealNumberQuestion(Question[Decimal]):
    """
    Question answered by entering a number that may have a fractional part, such as a height or an amount of money.

    The answer is a ``Decimal``, so that the digits the respondent wrote are kept exactly.
    Lengths of time are durations instead.

    Parameters
    ----------
    bounds : Bounds[Decimal]
        Accepted range. Special-response codes must lie outside it.
    unit : str | None
        Unit of the value, such as ``cm`` or ``thousand yen``. ``None`` for a unitless value.
    decimal_places : int | None
        Most digits accepted after the decimal point. ``None`` means no limit.
    is_zero_absolute : bool
        Whether zero means none of the quantity, as in a weight, which makes the answer
        ratio-scaled. ``False`` for an arbitrary zero, as in degrees Celsius, which makes it interval-scaled.

    Raises
    ------
    ValueError
        If ``unit`` is blank, ``decimal_places`` is negative, or a special-response code lies
        within ``bounds``.
    """

    question_type: ClassVar[QuestionType] = QuestionType.REAL_NUMBER

    bounds: Bounds[Decimal] = field(default_factory=Bounds[Decimal])
    unit: str | None = None
    decimal_places: int | None = None
    is_zero_absolute: bool = True

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.unit is not None and not self.unit.strip():
            raise ValueError(f"unit of question {self.id} must not be blank.")
        if self.decimal_places is not None and self.decimal_places < 0:
            raise ValueError(
                f"decimal_places of question {self.id} must not be negative."
            )

    @override
    def is_value_code(self, code: int) -> bool:
        """
        Whether the code lies within the bounds.
        """
        return Decimal(code) in self.bounds

    @property
    @override
    def measurement_level(self) -> MeasurementLevel:
        """
        ``RATIO`` if zero is absolute, otherwise ``INTERVAL``.
        """
        return (
            MeasurementLevel.RATIO
            if self.is_zero_absolute
            else MeasurementLevel.INTERVAL
        )

    @override
    def is_value(self, value: AnswerValue) -> TypeGuard[Decimal]:
        """
        Whether the value is a ``Decimal``.

        A ``float`` is rejected, because it cannot hold most decimal fractions exactly.
        """
        return isinstance(value, Decimal)

    @override
    def validate(self, value: Decimal) -> None:
        """
        Check that the value is finite, within the bounds, and not more precise than allowed.

        Raises
        ------
        InvalidAnswerError
            If the value is not finite, out of bounds, or has too many decimal places.
        """
        if not value.is_finite():
            raise InvalidAnswerError(
                f"Value {value} of question {self.id} is not finite."
            )
        self.bounds.validate(value)
        if (
            self.decimal_places is not None
            and count_decimal_places(value) > self.decimal_places
        ):
            raise InvalidAnswerError(
                f"Value {value} of question {self.id} has more than {self.decimal_places} decimal places."
            )
