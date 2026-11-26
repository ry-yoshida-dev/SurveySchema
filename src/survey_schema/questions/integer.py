from dataclasses import dataclass, field
from typing import ClassVar, TypeGuard, override

from variable import MeasurementLevel

from ..answer.value import AnswerValue
from ..bounds import Bounds
from ..question import Question
from ..question_type import QuestionType


@dataclass(frozen=True, kw_only=True)
class IntegerQuestion(Question[int]):
    """
    Question answered by entering a whole number, such as an age or a household size.

    The answer is an ``int``.

    Parameters
    ----------
    bounds : Bounds[int]
        Accepted range. Special-response codes must lie outside it, so a question that offers
        special responses needs a bound on the side of their codes, such as a maximum of 120
        for an age with ``999. Prefer not to answer``.
    unit : str | None
        Unit of the value, such as ``years``. ``None`` for a unitless value.
    is_zero_absolute : bool
        Whether zero means none of the quantity, as in a count or a weight, which makes the answer
        ratio-scaled. ``False`` for an arbitrary zero, as in a calendar year, which makes it interval-scaled.

    Raises
    ------
    ValueError
        If ``unit`` is blank, or a special-response code lies within ``bounds``.
    """

    question_type: ClassVar[QuestionType] = QuestionType.INTEGER

    bounds: Bounds[int] = field(default_factory=Bounds[int])
    unit: str | None = None
    is_zero_absolute: bool = True

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.unit is not None and not self.unit.strip():
            raise ValueError(f"unit of question {self.id} must not be blank.")

    @override
    def is_value_code(self, code: int) -> bool:
        """
        Whether the code lies within the bounds.
        """
        return code in self.bounds

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
    def is_value(self, value: AnswerValue) -> TypeGuard[int]:
        """
        Whether the value is an ``int`` other than a ``bool``.
        """
        return isinstance(value, int) and not isinstance(value, bool)

    @override
    def validate(self, value: int) -> None:
        """
        Check that the value is within the bounds.

        Raises
        ------
        InvalidAnswerError
            If the value is out of bounds.
        """
        self.bounds.validate(value)
