from dataclasses import dataclass
from typing import ClassVar, TypeGuard, override

from variable import MeasurementLevel

from ..answer.selection import ChoiceSelection
from ..answer.value import AnswerValue
from ..choice.options import ChoiceOptions
from ..question import Question
from ..question_type import QuestionType


@dataclass(frozen=True, kw_only=True)
class SingleChoiceQuestion(Question[ChoiceSelection]):
    """
    Question answered by choosing exactly one option (SA), shown as radio buttons, a list, or a dropdown.

    A yes-or-no question is a single-choice question with :meth:`ChoiceOptions.yes_no`, which gives
    both answers tabulation codes and leaves room for a third option.

    The answer is a ``ChoiceSelection``.

    Parameters
    ----------
    options : ChoiceOptions
        Options in defined order.
    is_ordered : bool
        Whether the options follow a natural order, such as age groups or frequencies,
        which makes the answer ordinal instead of nominal.

    Raises
    ------
    ValueError
        If an option is exclusive, which only applies to multiple choice, or the options are
        ordered but one has a field to write in, which has no place in the order.
    """

    question_type: ClassVar[QuestionType] = QuestionType.SINGLE_CHOICE

    options: ChoiceOptions
    is_ordered: bool = False

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.options.is_exclusive_included:
            raise ValueError(
                f"Question {self.id} is single choice, so its options cannot be exclusive."
            )
        if self.is_ordered and self.options.is_free_text_included:
            raise ValueError(
                f"Options of question {self.id} are ordered, so none can have a field to write in."
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
        ``ORDINAL`` if the options are ordered, otherwise ``NOMINAL``.
        """
        return MeasurementLevel.ORDINAL if self.is_ordered else MeasurementLevel.NOMINAL

    @override
    def is_value(self, value: AnswerValue) -> TypeGuard[ChoiceSelection]:
        """
        Whether the value is a ``ChoiceSelection``.
        """
        return isinstance(value, ChoiceSelection)

    @override
    def validate(self, value: ChoiceSelection) -> None:
        """
        Check that the selection is one of the options.

        Raises
        ------
        InvalidAnswerError
            If the code is unknown, or free text is given for an option without a field.
        """
        self.options.validate(value)
