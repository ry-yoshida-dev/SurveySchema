from dataclasses import dataclass
from typing import ClassVar, TypeGuard, override

from variable import MeasurementLevel

from ..answer.error import InvalidAnswerError
from ..answer.selection import ChoiceSelection
from ..answer.value import AnswerValue
from ..choice.options import ChoiceOptions
from ..question import Question
from ..question_type import QuestionType


@dataclass(frozen=True, kw_only=True)
class MultipleChoiceQuestion(Question[tuple[ChoiceSelection, ...]]):
    """
    Question answered by choosing any number of options (MA), or a limited number (LA).

    The answer is a ``tuple[ChoiceSelection, ...]``.

    Parameters
    ----------
    options : ChoiceOptions
        Options in defined order. Exclusive options, such as ``None of the above``, must be chosen alone.
    min_selections : int
        Fewest options to choose, unless an exclusive option is chosen alone. It is at least 1:
        choosing nothing is ``NO_ANSWER``, so a survey that lets respondents choose none offers an
        exclusive option such as ``None of the above``.
    max_selections : int | None
        Most options to choose, such as 3 for ``Choose up to three``. ``None`` means no limit.

    Raises
    ------
    ValueError
        If the selection limits are outside ``1 <= min_selections <= max_selections <= n``, where
        ``n`` is the number of options that are not exclusive.
    """

    question_type: ClassVar[QuestionType] = QuestionType.MULTIPLE_CHOICE

    options: ChoiceOptions
    min_selections: int = 1
    max_selections: int | None = None

    def __post_init__(self) -> None:
        super().__post_init__()
        combinable_count = sum(not option.is_exclusive for option in self.options)
        if not 1 <= self.min_selections <= combinable_count:
            raise ValueError(
                f"min_selections of question {self.id} must be between 1 and {combinable_count}."
            )
        if (
            self.max_selections is not None
            and not self.min_selections <= self.max_selections <= combinable_count
        ):
            raise ValueError(
                f"max_selections of question {self.id} must be between {self.min_selections} and {combinable_count}."
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
        Always ``NOMINAL``.
        """
        return MeasurementLevel.NOMINAL

    @override
    def is_value(self, value: AnswerValue) -> TypeGuard[tuple[ChoiceSelection, ...]]:
        """
        Whether the value is a tuple of ``ChoiceSelection``.
        """
        return isinstance(value, tuple) and all(
            isinstance(item, ChoiceSelection) for item in value
        )

    @override
    def validate(self, value: tuple[ChoiceSelection, ...]) -> None:
        """
        Check the selected options, their count, and exclusivity.

        Raises
        ------
        InvalidAnswerError
            If a selection is invalid or repeated, the count is out of range,
            or an exclusive option is chosen together with another.
        """
        for selection in value:
            self.options.validate(selection)
        codes = [selection.code for selection in value]
        if len(set(codes)) != len(codes):
            raise InvalidAnswerError(f"Options {codes} of question {self.id} repeat.")
        is_exclusive_chosen = any(self.options[code].is_exclusive for code in codes)
        if is_exclusive_chosen:
            if len(codes) > 1:
                raise InvalidAnswerError(
                    f"An exclusive option of question {self.id} is chosen with other options."
                )
            return
        if len(codes) < self.min_selections:
            raise InvalidAnswerError(
                f"Question {self.id} needs at least {self.min_selections} selections."
            )
        if self.max_selections is not None and len(codes) > self.max_selections:
            raise InvalidAnswerError(
                f"Question {self.id} allows at most {self.max_selections} selections."
            )
