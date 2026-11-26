# pyright: reportImportCycles=false
# Answer, AnswerValue, and MatrixAnswer refer to each other, because a matrix answer holds answers.
from collections.abc import Iterator, Mapping
from dataclasses import dataclass, field
from types import MappingProxyType

from .answer import Answer
from .status import AnswerStatus
from .value import AnswerValue


@dataclass(frozen=True)
class MatrixAnswer:
    """
    Answers to the items of one matrix question, each with its own status.

    On paper, one row of a grid can be left blank or marked ``Don't know`` while the others are
    answered, so each item keeps a full :class:`Answer`.

    Parameters
    ----------
    items : Mapping[str, Answer[AnswerValue]]
        Answers keyed by item ID. An item not recorded is treated as ``NO_ANSWER``, because the
        respondent reached the matrix.
    """

    items: Mapping[str, Answer[AnswerValue]] = field(hash=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "items", MappingProxyType(dict(self.items)))

    def __iter__(self) -> Iterator[str]:
        return iter(self.items)

    def __len__(self) -> int:
        return len(self.items)

    def answer(self, item_id: str) -> Answer[AnswerValue]:
        """
        Look up the answer to one item.

        Parameters
        ----------
        item_id : str
            ID of the item.

        Returns
        -------
        Answer[AnswerValue]
            The recorded answer, or a ``NO_ANSWER`` answer if none is recorded.
        """
        return self.items.get(item_id, Answer.missing(AnswerStatus.NO_ANSWER))
