from dataclasses import dataclass, field
from typing import ClassVar, TypeGuard, override

from variable import MeasurementLevel

from ..answer.value import AnswerValue
from ..answer.year_month import YearMonth
from ..bounds import Bounds
from ..question import Question
from ..question_type import QuestionType


@dataclass(frozen=True, kw_only=True)
class YearMonthQuestion(Question[YearMonth]):
    """
    Question answered by entering a year and a month, such as a birth month or the month a job started.

    The answer is a :class:`YearMonth`. A year alone is an integer question with
    ``is_zero_absolute=False``, and a full date is a date question.

    Parameters
    ----------
    bounds : Bounds[YearMonth]
        Accepted range.
    """

    question_type: ClassVar[QuestionType] = QuestionType.YEAR_MONTH

    bounds: Bounds[YearMonth] = field(default_factory=Bounds[YearMonth])

    @property
    @override
    def measurement_level(self) -> MeasurementLevel:
        """
        Always ``INTERVAL``.
        """
        return MeasurementLevel.INTERVAL

    @override
    def is_value(self, value: AnswerValue) -> TypeGuard[YearMonth]:
        """
        Whether the value is a ``YearMonth``.
        """
        return isinstance(value, YearMonth)

    @override
    def validate(self, value: YearMonth) -> None:
        """
        Check that the month is within the bounds.

        Raises
        ------
        InvalidAnswerError
            If the month is out of bounds.
        """
        self.bounds.validate(value)
