from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import ClassVar, TypeGuard

from variable import MeasurementLevel

from .answer.answer import Answer
from .answer.error import InvalidAnswerError
from .answer.status import AnswerStatus
from .answer.value import AnswerValue
from .question_type import QuestionType
from .special.responses import SpecialResponses


@dataclass(frozen=True, kw_only=True)
class Question[ValueT: AnswerValue](ABC):
    """
    One question, whose type fixes the format of its answer on any medium.

    Parameters
    ----------
    id : str
        Identifier of the question, which keys its answer in a response, such as ``Q1``.
    text : str
        Question text.
    special_responses : SpecialResponses
        Responses offered beside the substantive answers, such as ``Don't know``.

    Raises
    ------
    ValueError
        If ``id`` or ``text`` is blank, or a special-response code could also be read as a
        substantive answer.
    """

    question_type: ClassVar[QuestionType]

    id: str
    text: str
    special_responses: SpecialResponses = field(default_factory=SpecialResponses)

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("id must not be blank.")
        if not self.text.strip():
            raise ValueError(f"text of question {self.id} must not be blank.")
        colliding = sorted(
            code for code in self.special_responses.codes if self.is_value_code(code)
        )
        if colliding:
            raise ValueError(
                f"Special-response codes {colliding} of question {self.id} could also be substantive answers."
            )

    def is_value_code(self, code: int) -> bool:
        """
        Whether an integer could be recorded as, or inside, a substantive answer.

        Such an integer cannot be a special-response code, because a code sheet or data column
        that holds both would be ambiguous. Questions whose answers are not integers, such as
        dates or text, have no such integers: their special responses are separate marks.

        Parameters
        ----------
        code : int
            Candidate special-response code.

        Returns
        -------
        bool
            ``True`` if a substantive answer could use the integer.
        """
        del code  # No integer is a substantive answer unless a question type says so.
        return False

    @property
    @abstractmethod
    def measurement_level(self) -> MeasurementLevel | None:
        """
        Level of measurement of the answer. ``None`` for answers without one, such as free text.
        """

    @abstractmethod
    def is_value(self, value: AnswerValue) -> TypeGuard[ValueT]:
        """
        Whether a value has the answer type of this question.

        Parameters
        ----------
        value : AnswerValue
            Value to check.

        Returns
        -------
        TypeGuard[ValueT]
            ``True`` if the value has the answer type, regardless of its constraints.
        """

    @abstractmethod
    def validate(self, value: ValueT) -> None:
        """
        Check that a value satisfies the constraints of this question.

        Parameters
        ----------
        value : ValueT
            Value to check.

        Raises
        ------
        InvalidAnswerError
            If the value breaks a constraint.
        """

    def answer(self, value: ValueT) -> Answer[ValueT]:
        """
        Validate a value and wrap it as an answered answer.

        Parameters
        ----------
        value : ValueT
            Captured value.

        Returns
        -------
        Answer[ValueT]
            Answer with status ``ANSWERED``.

        Raises
        ------
        InvalidAnswerError
            If the value breaks a constraint.
        """
        self.validate(value)
        return Answer.answered(value)

    def check(self, answer: Answer[AnswerValue]) -> None:
        """
        Check an answer of unknown value type against this question.

        Parameters
        ----------
        answer : Answer[AnswerValue]
            Answer to check. Answers without a value or special code always pass, and so do the
            captured contents of ``INVALID`` and ``UNREADABLE`` answers.

        Raises
        ------
        TypeError
            If the value does not have the answer type of this question.
        InvalidAnswerError
            If the value breaks a constraint, or the special code is not offered.
        """
        if answer.status is AnswerStatus.SPECIAL_RESPONSE:
            if answer.special_code not in self.special_responses:
                raise InvalidAnswerError(
                    f"Special code {answer.special_code} is not offered by question {self.id}."
                )
            return
        value = answer.value
        if value is None:
            return
        if not self.is_value(value):
            raise TypeError(
                f"{value!r} is not a valid answer type for {self.question_type.name} question {self.id}."
            )
        self.validate(value)
