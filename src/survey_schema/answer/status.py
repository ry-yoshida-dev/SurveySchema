from enum import Enum


class AnswerStatus(Enum):
    """
    Outcome of capturing one answer, on any medium.

    ``ANSWERED`` carries a value and ``SPECIAL_RESPONSE`` carries a special-response code.
    The other members distinguish the reasons nothing usable was captured,
    because they are tabulated separately.
    """

    ANSWERED = "answered"
    """A substantive answer that satisfies the question's constraints."""

    SPECIAL_RESPONSE = "special_response"
    """
    A response outside the substantive answers, such as ``Don't know`` or ``Refused``.

    It excludes substantive answers and other special responses: one marked together with
    options is ``INVALID``, with the marks kept as the answer's raw value.
    """

    NO_ANSWER = "no_answer"
    """The respondent reached the question but left it blank."""

    NOT_APPLICABLE = "not_applicable"
    """The respondent was not meant to answer, because the survey routed them past the question."""

    NOT_REACHED = "not_reached"
    """The respondent stopped before reaching the question, as when a web session is abandoned."""

    INVALID = "invalid"
    """
    An answer was captured but breaks a constraint, such as two marks on a single-choice question.

    The captured content can be kept as the answer's raw value or transcription.
    """

    UNREADABLE = "unreadable"
    """
    An answer was given but cannot be interpreted, such as illegible handwriting or an inaudible reply.

    Whatever part can be made out can be kept as the answer's transcription.
    """
