from dataclasses import dataclass
from typing import ClassVar, TypeGuard, override

from ..answer.error import InvalidAnswerError
from ..answer.value import AnswerValue
from ..question import Question
from ..question_type import QuestionType


@dataclass(frozen=True, kw_only=True)
class FreeTextListQuestion(Question[tuple[str, ...]]):
    """
    Question answered by writing several short texts in separate fields, such as ``Name up to three brands``.

    The answer is a ``tuple[str, ...]`` of the filled fields in the order written, which keeps
    the first mention first. Fields left empty are omitted, because they mean fewer mentions,
    not a missing answer.

    Parameters
    ----------
    max_entries : int
        Number of fields.
    min_entries : int
        Fewest fields to fill.
    max_length : int | None
        Most characters accepted in each field. ``None`` means no limit.
    is_repetition_allowed : bool
        Whether the same text may appear in two fields, compared without surrounding whitespace.

    Raises
    ------
    ValueError
        If the limits are outside ``1 <= min_entries <= max_entries``, or ``max_length`` is not positive.
    """

    question_type: ClassVar[QuestionType] = QuestionType.FREE_TEXT_LIST

    max_entries: int
    min_entries: int = 1
    max_length: int | None = None
    is_repetition_allowed: bool = False

    def __post_init__(self) -> None:
        super().__post_init__()
        if not 1 <= self.min_entries <= self.max_entries:
            raise ValueError(
                f"Entry limits of question {self.id} must satisfy 1 <= min_entries <= max_entries."
            )
        if self.max_length is not None and self.max_length <= 0:
            raise ValueError(f"max_length of question {self.id} must be positive.")

    @property
    @override
    def measurement_level(self) -> None:
        """
        Always ``None``, because text has no level of measurement until it is coded.
        """
        return None

    @override
    def is_value(self, value: AnswerValue) -> TypeGuard[tuple[str, ...]]:
        """
        Whether the value is a tuple of ``str``.
        """
        return isinstance(value, tuple) and all(isinstance(item, str) for item in value)

    @override
    def validate(self, value: tuple[str, ...]) -> None:
        """
        Check the number of entries, their text, and repetition.

        Raises
        ------
        InvalidAnswerError
            If an entry is blank or too long, an entry repeats when that is not allowed, or the
            number of entries is outside the limits.
        """
        if any(not entry.strip() for entry in value):
            raise InvalidAnswerError(
                f"Entries of question {self.id} must not be blank; omit empty fields."
            )
        if self.max_length is not None and any(
            len(entry) > self.max_length for entry in value
        ):
            raise InvalidAnswerError(
                f"An entry of question {self.id} exceeds {self.max_length} characters."
            )
        if not self.is_repetition_allowed and len(
            {entry.strip() for entry in value}
        ) != len(value):
            raise InvalidAnswerError(f"Entries of question {self.id} repeat.")
        if not self.min_entries <= len(value) <= self.max_entries:
            raise InvalidAnswerError(
                f"Question {self.id} needs {self.min_entries} to {self.max_entries} entries but {len(value)} were given."
            )
