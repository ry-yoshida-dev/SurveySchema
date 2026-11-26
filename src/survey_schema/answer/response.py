from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType

from .answer import Answer
from .status import AnswerStatus
from .value import AnswerValue


@dataclass(frozen=True, kw_only=True)
class Response:
    """
    Every answer of one respondent, from a paper sheet, a web session, or an interview.

    Parameters
    ----------
    respondent_id : str
        Identifier of the respondent, such as a sheet serial number or a session ID.
    answers : Mapping[str, Answer[AnswerValue]]
        Answers keyed by question ID. A response still being collected may omit questions.

    Raises
    ------
    ValueError
        If ``respondent_id`` is blank.
    """

    respondent_id: str
    answers: Mapping[str, Answer[AnswerValue]] = field(hash=False)

    def __post_init__(self) -> None:
        if not self.respondent_id.strip():
            raise ValueError("respondent_id must not be blank.")
        object.__setattr__(self, "answers", MappingProxyType(dict(self.answers)))

    def answer(self, question_id: str) -> Answer[AnswerValue]:
        """
        Look up the answer to a question.

        Parameters
        ----------
        question_id : str
            ID of the question.

        Returns
        -------
        Answer[AnswerValue]
            The recorded answer, or a ``NOT_REACHED`` answer if none is recorded yet.
        """
        return self.answers.get(question_id, Answer.missing(AnswerStatus.NOT_REACHED))
