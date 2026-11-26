from dataclasses import dataclass, field
from datetime import date, datetime
from typing import ClassVar, TypeGuard, override

from variable import MeasurementLevel

from ..answer.value import AnswerValue
from ..bounds import Bounds
from ..question import Question
from ..question_type import QuestionType


@dataclass(frozen=True, kw_only=True)
class DateQuestion(Question[date]):
    """
    Question answered by entering a calendar date, such as a birth date or a visit date.

    The answer is a ``datetime.date``.

    Parameters
    ----------
    bounds : Bounds[date]
        Accepted range, with ends that are dates, not date-times.

    Raises
    ------
    ValueError
        If an end of ``bounds`` is a ``datetime.datetime``.
    """

    question_type: ClassVar[QuestionType] = QuestionType.DATE

    bounds: Bounds[date] = field(default_factory=Bounds[date])

    def __post_init__(self) -> None:
        super().__post_init__()
        if any(
            isinstance(end, datetime)
            for end in (self.bounds.minimum, self.bounds.maximum)
        ):
            raise ValueError(
                f"bounds of question {self.id} must be dates, not date-times."
            )

    @property
    @override
    def measurement_level(self) -> MeasurementLevel:
        """
        Always ``INTERVAL``.
        """
        return MeasurementLevel.INTERVAL

    @override
    def is_value(self, value: AnswerValue) -> TypeGuard[date]:
        """
        Whether the value is a ``datetime.date`` but not a ``datetime.datetime``.
        """
        return isinstance(value, date) and not isinstance(value, datetime)

    @override
    def validate(self, value: date) -> None:
        """
        Check that the date is within the bounds.

        Raises
        ------
        InvalidAnswerError
            If the date is out of bounds.
        """
        self.bounds.validate(value)
