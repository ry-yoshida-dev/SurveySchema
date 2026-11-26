import re
from dataclasses import dataclass
from typing import ClassVar, TypeGuard, override

from ..answer.error import InvalidAnswerError
from ..answer.value import AnswerValue
from ..question import Question
from ..question_type import QuestionType


@dataclass(frozen=True, kw_only=True)
class FreeTextQuestion(Question[str]):
    """
    Question answered by entering text freely, from a short word to an open comment.

    The answer is a non-blank ``str``; a blank answer is ``AnswerStatus.NO_ANSWER``.

    Parameters
    ----------
    min_length : int
        Fewest characters accepted, such as 10 for ``Describe in at least 10 characters``.
    max_length : int | None
        Most characters accepted. ``None`` means no limit.
    pattern : re.Pattern[str] | None
        Pattern the whole text must match, such as a postal code, telephone number, or email
        address format. ``None`` accepts any text.

    Raises
    ------
    ValueError
        If ``min_length`` is not positive or ``max_length`` is less than it.
    """

    question_type: ClassVar[QuestionType] = QuestionType.FREE_TEXT

    min_length: int = 1
    max_length: int | None = None
    pattern: re.Pattern[str] | None = None

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.min_length < 1:
            raise ValueError(f"min_length of question {self.id} must be positive.")
        if self.max_length is not None and self.max_length < self.min_length:
            raise ValueError(
                f"max_length of question {self.id} must not be less than min_length {self.min_length}."
            )

    @property
    @override
    def measurement_level(self) -> None:
        """
        Always ``None``, because text has no level of measurement until it is coded.
        """
        return None

    @override
    def is_value(self, value: AnswerValue) -> TypeGuard[str]:
        """
        Whether the value is a ``str``.
        """
        return isinstance(value, str)

    @override
    def validate(self, value: str) -> None:
        """
        Check that the text is not blank, fits the length, and matches the pattern.

        Raises
        ------
        InvalidAnswerError
            If the text is blank, too short, too long, or does not match the pattern.
        """
        if not value.strip():
            raise InvalidAnswerError(
                f"Text of question {self.id} is blank; record it as NO_ANSWER instead."
            )
        if len(value) < self.min_length:
            raise InvalidAnswerError(
                f"Text of question {self.id} is shorter than {self.min_length} characters."
            )
        if self.max_length is not None and len(value) > self.max_length:
            raise InvalidAnswerError(
                f"Text of question {self.id} exceeds {self.max_length} characters."
            )
        if self.pattern is not None and self.pattern.fullmatch(value) is None:
            raise InvalidAnswerError(
                f"Text of question {self.id} does not match {self.pattern.pattern!r}."
            )
