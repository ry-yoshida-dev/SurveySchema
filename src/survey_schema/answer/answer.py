# pyright: reportImportCycles=false
# Answer, AnswerValue, and MatrixAnswer refer to each other, because a matrix answer holds answers.
from dataclasses import dataclass
from typing import Generic, Never, TypeVar

from .status import AnswerStatus
from .value import AnswerValue

# Declared covariant explicitly: since Python 3.13 dataclasses synthesize __replace__, which makes
# inferred PEP 695 variance invariant, and a Response must hold answers of different value types.
ValueT_co = TypeVar("ValueT_co", bound=AnswerValue, covariant=True)


@dataclass(frozen=True, kw_only=True)
class Answer(Generic[ValueT_co]):  # noqa: UP046
    """
    Answer of one respondent to one question.

    Prefer :meth:`Question.answer` for substantive values, which also validates them,
    :meth:`special` for special responses, :meth:`invalid` and :meth:`unreadable` for captured
    content that cannot be used, and :meth:`missing` for every other status.

    Parameters
    ----------
    status : AnswerStatus
        Outcome of capturing the answer.
    value : ValueT_co | None
        Substantive value, present exactly when ``status`` is ``ANSWERED``.
    special_code : int | None
        Code of the special response, present exactly when ``status`` is ``SPECIAL_RESPONSE``.
    raw_value : AnswerValue | None
        Captured value that breaks a constraint, kept so that it can be reviewed, such as both
        selections of a single-choice question marked twice. Only for ``INVALID``. Its type need
        not be the question's answer type.
    transcription : str | None
        Captured content written down as seen, when it cannot be typed, such as ``1?5`` or
        ``Tokyo, [illegible] ward``. Only for ``INVALID`` and ``UNREADABLE``.

    Raises
    ------
    ValueError
        If ``value``, ``special_code``, ``raw_value``, or ``transcription`` does not match
        ``status``, or ``transcription`` is blank.
    """

    status: AnswerStatus
    value: ValueT_co | None = None
    special_code: int | None = None
    raw_value: AnswerValue | None = None
    transcription: str | None = None

    def __post_init__(self) -> None:
        is_answered = self.status is AnswerStatus.ANSWERED
        if is_answered != (self.value is not None):
            raise ValueError(
                f"An answer with status {self.status.name} must {'' if is_answered else 'not '}have a value."
            )
        is_special = self.status is AnswerStatus.SPECIAL_RESPONSE
        if is_special != (self.special_code is not None):
            raise ValueError(
                f"An answer with status {self.status.name} must {'' if is_special else 'not '}have a special code."
            )
        if self.raw_value is not None and self.status is not AnswerStatus.INVALID:
            raise ValueError(
                f"Only an INVALID answer can have a raw value, not {self.status.name}."
            )
        if self.transcription is not None:
            if self.status not in (AnswerStatus.INVALID, AnswerStatus.UNREADABLE):
                raise ValueError(
                    f"Only an INVALID or UNREADABLE answer can have a transcription, not {self.status.name}."
                )
            if not self.transcription.strip():
                raise ValueError(
                    "transcription must not be blank; use None when nothing is written down."
                )

    @staticmethod
    def answered[AnsweredT: AnswerValue](value: AnsweredT) -> "Answer[AnsweredT]":
        """
        Create an answer that carries a value, without validating it against a question.

        Parameters
        ----------
        value : AnsweredT
            Substantive value.

        Returns
        -------
        Answer[AnsweredT]
            Answer with status ``ANSWERED``.
        """
        return Answer(status=AnswerStatus.ANSWERED, value=value)

    @staticmethod
    def special(code: int) -> "Answer[Never]":
        """
        Create a special response, such as ``Don't know``.

        Parameters
        ----------
        code : int
            Code of the special response defined on the question.

        Returns
        -------
        Answer[Never]
            Answer with status ``SPECIAL_RESPONSE``, usable for a question of any value type.

        Raises
        ------
        TypeError
            If ``code`` is a ``bool``.
        """
        if isinstance(code, bool):
            raise TypeError("code must be an int, not a bool.")
        return Answer(status=AnswerStatus.SPECIAL_RESPONSE, special_code=code)

    @staticmethod
    def invalid(
        raw_value: AnswerValue | None = None, *, transcription: str | None = None
    ) -> "Answer[Never]":
        """
        Create an answer that was captured but breaks a constraint of its question.

        Parameters
        ----------
        raw_value : AnswerValue | None
            Captured value, such as ``(ChoiceSelection(1), ChoiceSelection(3))`` for two marks on
            a single-choice question, or a special-response code marked together with options.
        transcription : str | None
            Captured content as seen, such as ``12.5`` entered for a whole number.

        Returns
        -------
        Answer[Never]
            Answer with status ``INVALID``, usable for a question of any value type.
        """
        return Answer(
            status=AnswerStatus.INVALID,
            raw_value=raw_value,
            transcription=transcription,
        )

    @staticmethod
    def unreadable(transcription: str | None = None) -> "Answer[Never]":
        """
        Create an answer that was given but cannot be interpreted.

        Parameters
        ----------
        transcription : str | None
            Whatever part can be made out, such as ``1?5``. ``None`` when nothing can.

        Returns
        -------
        Answer[Never]
            Answer with status ``UNREADABLE``, usable for a question of any value type.
        """
        return Answer(status=AnswerStatus.UNREADABLE, transcription=transcription)

    @staticmethod
    def missing(status: AnswerStatus) -> "Answer[Never]":
        """
        Create an answer that carries neither a value nor a special code.

        Parameters
        ----------
        status : AnswerStatus
            Reason nothing usable was captured.

        Returns
        -------
        Answer[Never]
            Answer usable for a question of any value type.

        Raises
        ------
        ValueError
            If ``status`` is ``ANSWERED`` or ``SPECIAL_RESPONSE``.
        """
        return Answer(status=status)

    @property
    def is_answered(self) -> bool:
        """
        Whether the answer carries a substantive value.
        """
        return self.status is AnswerStatus.ANSWERED

    @property
    def is_given(self) -> bool:
        """
        Whether the respondent gave a usable response: a substantive value or a special response.
        """
        return self.status in (AnswerStatus.ANSWERED, AnswerStatus.SPECIAL_RESPONSE)
