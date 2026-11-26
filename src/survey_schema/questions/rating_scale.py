from dataclasses import dataclass
from typing import ClassVar, TypeGuard, override

from variable import MeasurementLevel

from ..answer.value import AnswerValue
from ..question import Question
from ..question_type import QuestionType
from ..rating_scale import RatingScale


@dataclass(frozen=True, kw_only=True)
class RatingScaleQuestion(Question[int]):
    """
    Question answered by choosing a point on a numbered scale, such as a Likert scale or NPS.

    Star ratings and semantic differentials between two opposite adjectives are rating scales too.
    The answer is an ``int`` point on the scale. Use it when the code is a number on the scale;
    when each code stands for a labeled category, use an ordered single-choice question instead.

    Parameters
    ----------
    scale : RatingScale
        Scale to rate on.
    """

    question_type: ClassVar[QuestionType] = QuestionType.RATING_SCALE

    scale: RatingScale

    @override
    def is_value_code(self, code: int) -> bool:
        """
        Whether the code is a point of the scale.
        """
        return code in self.scale

    @property
    @override
    def measurement_level(self) -> MeasurementLevel:
        """
        Always ``ORDINAL``.
        """
        return MeasurementLevel.ORDINAL

    @override
    def is_value(self, value: AnswerValue) -> TypeGuard[int]:
        """
        Whether the value is an ``int`` other than a ``bool``.
        """
        return isinstance(value, int) and not isinstance(value, bool)

    @override
    def validate(self, value: int) -> None:
        """
        Check that the value is a point on the scale.

        Raises
        ------
        InvalidAnswerError
            If the value is not a point of the scale.
        """
        self.scale.validate(value)
