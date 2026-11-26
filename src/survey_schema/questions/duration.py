from dataclasses import dataclass, field
from datetime import timedelta
from typing import ClassVar, TypeGuard, override

from variable import MeasurementLevel

from ..answer.error import InvalidAnswerError
from ..answer.value import AnswerValue
from ..bounds import Bounds
from ..question import Question
from ..question_type import QuestionType


@dataclass(frozen=True, kw_only=True)
class DurationQuestion(Question[timedelta]):
    """
    Question answered by entering a length of time, such as ``__ hours __ minutes`` of sleep.

    The answer is a non-negative ``datetime.timedelta``, so that 1 hour 50 minutes is never
    confused with 1.5 hours. A clock time is a time-of-day question instead.

    Parameters
    ----------
    bounds : Bounds[timedelta]
        Accepted range.
    resolution : timedelta | None
        Smallest unit that can be entered, such as one minute for hours and minutes, which the
        answer must be a whole multiple of. ``None`` accepts any length.

    Raises
    ------
    ValueError
        If ``bounds`` admits only negative lengths, or ``resolution`` is not positive.
    """

    question_type: ClassVar[QuestionType] = QuestionType.DURATION

    bounds: Bounds[timedelta] = field(default_factory=Bounds[timedelta])
    resolution: timedelta | None = None

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.bounds.maximum is not None and self.bounds.maximum < timedelta(0):
            raise ValueError(
                f"bounds of question {self.id} must admit non-negative lengths."
            )
        if self.resolution is not None and self.resolution <= timedelta(0):
            raise ValueError(f"resolution of question {self.id} must be positive.")

    @property
    @override
    def measurement_level(self) -> MeasurementLevel:
        """
        Always ``RATIO``, because zero means no time at all.
        """
        return MeasurementLevel.RATIO

    @override
    def is_value(self, value: AnswerValue) -> TypeGuard[timedelta]:
        """
        Whether the value is a ``datetime.timedelta``.
        """
        return isinstance(value, timedelta)

    @override
    def validate(self, value: timedelta) -> None:
        """
        Check that the length is not negative, within the bounds, and a multiple of the resolution.

        Raises
        ------
        InvalidAnswerError
            If the length is negative, out of bounds, or not a multiple of :attr:`resolution`.
        """
        if value < timedelta(0):
            raise InvalidAnswerError(
                f"Length {value} of question {self.id} is negative."
            )
        self.bounds.validate(value)
        if self.resolution is not None and value % self.resolution:
            raise InvalidAnswerError(
                f"Length {value} of question {self.id} is not a multiple of {self.resolution}."
            )
