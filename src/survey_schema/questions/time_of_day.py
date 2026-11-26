from dataclasses import dataclass, field
from datetime import time
from typing import ClassVar, TypeGuard, override

from variable import MeasurementLevel

from ..answer.error import InvalidAnswerError
from ..answer.value import AnswerValue
from ..bounds import Bounds
from ..question import Question
from ..question_type import QuestionType


@dataclass(frozen=True, kw_only=True)
class TimeOfDayQuestion(Question[time]):
    """
    Question answered by entering a clock time, such as a bedtime.

    The answer is a naive ``datetime.time``. Lengths of time, such as hours of sleep, are durations instead.

    Parameters
    ----------
    bounds : Bounds[time]
        Accepted range, with naive ends. It cannot wrap around midnight.

    Raises
    ------
    ValueError
        If an end of ``bounds`` has a time zone.
    """

    question_type: ClassVar[QuestionType] = QuestionType.TIME_OF_DAY

    bounds: Bounds[time] = field(default_factory=Bounds[time])

    def __post_init__(self) -> None:
        super().__post_init__()
        if any(
            end is not None and end.tzinfo is not None
            for end in (self.bounds.minimum, self.bounds.maximum)
        ):
            raise ValueError(f"bounds of question {self.id} must not have a time zone.")

    @property
    @override
    def measurement_level(self) -> MeasurementLevel:
        """
        Always ``CYCLIC``, because clock times wrap around at midnight.
        """
        return MeasurementLevel.CYCLIC

    @override
    def is_value(self, value: AnswerValue) -> TypeGuard[time]:
        """
        Whether the value is a ``datetime.time``.
        """
        return isinstance(value, time)

    @override
    def validate(self, value: time) -> None:
        """
        Check that the time has no time zone and is within the bounds.

        Raises
        ------
        InvalidAnswerError
            If the time has a time zone or is out of bounds.
        """
        if value.tzinfo is not None:
            raise InvalidAnswerError(
                f"Time {value} of question {self.id} must not have a time zone."
            )
        self.bounds.validate(value)
