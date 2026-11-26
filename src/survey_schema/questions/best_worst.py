from dataclasses import dataclass
from typing import ClassVar, TypeGuard, override

from variable import MeasurementLevel

from ..answer.best_worst import BestWorstChoice
from ..answer.error import InvalidAnswerError
from ..answer.value import AnswerValue
from ..choice.options import ChoiceOptions
from ..question import Question
from ..question_type import QuestionType


@dataclass(frozen=True, kw_only=True)
class BestWorstQuestion(Question[BestWorstChoice]):
    """
    Question answered by choosing the best and the worst of a set of options (MaxDiff).

    The answer is a :class:`BestWorstChoice`. A best-worst exercise repeats this question over
    several sets of options; the experimental design that builds the sets is outside this package.

    Parameters
    ----------
    options : ChoiceOptions
        Options of the set, at least three. They cannot be exclusive or have a field to write in.

    Raises
    ------
    ValueError
        If there are fewer than three options, or an option is exclusive or has a field.
    """

    question_type: ClassVar[QuestionType] = QuestionType.BEST_WORST

    options: ChoiceOptions

    def __post_init__(self) -> None:
        super().__post_init__()
        # With two options, choosing the best already decides the worst.
        if len(self.options) < 3:
            raise ValueError(
                f"Best-worst question {self.id} needs at least three options."
            )
        if self.options.is_exclusive_included or self.options.is_free_text_included:
            raise ValueError(
                f"Options of best-worst question {self.id} cannot be exclusive or have a field."
            )

    @override
    def is_value_code(self, code: int) -> bool:
        """
        Whether the code is an option code.
        """
        return code in self.options

    @property
    @override
    def measurement_level(self) -> MeasurementLevel:
        """
        Always ``ORDINAL``, because the answer is a partial ranking.
        """
        return MeasurementLevel.ORDINAL

    @override
    def is_value(self, value: AnswerValue) -> TypeGuard[BestWorstChoice]:
        """
        Whether the value is a ``BestWorstChoice``.
        """
        return isinstance(value, BestWorstChoice)

    @override
    def validate(self, value: BestWorstChoice) -> None:
        """
        Check that both codes are options.

        Raises
        ------
        InvalidAnswerError
            If a code is not an option.
        """
        unknown = [
            code for code in (value.best, value.worst) if code not in self.options
        ]
        if unknown:
            raise InvalidAnswerError(
                f"Codes {unknown} of question {self.id} are not options."
            )
