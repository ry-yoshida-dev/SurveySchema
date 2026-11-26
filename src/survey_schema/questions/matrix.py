from collections.abc import Sequence
from dataclasses import dataclass, replace
from typing import ClassVar, Self, TypeGuard, override

from variable import MeasurementLevel

from ..answer.error import InvalidAnswerError
from ..answer.matrix import MatrixAnswer
from ..answer.value import AnswerValue
from ..question import Question
from ..question_type import QuestionType
from ..special.responses import SpecialResponses


@dataclass(frozen=True, kw_only=True)
class MatrixQuestion[CellT: AnswerValue](Question[MatrixAnswer]):
    """
    Grid of items that share one answer format, such as statements rated on the same scale.

    Each row is an ordinary question, so a grid can be single choice, multiple choice, rating,
    or numeric entry per row: ``Which services did you use, and how many times each`` is a
    matrix of integer questions. The answer is a :class:`MatrixAnswer` that keeps each item's
    own status and special response, such as one row marked ``Don't know``.

    A matrix left entirely blank is ``NO_ANSWER`` and one routed past is ``NOT_APPLICABLE``,
    recorded on the matrix itself.

    Parameters
    ----------
    items : tuple[Question[CellT], ...]
        Rows in displayed order, at least two. The ID of each identifies its answer, the text
        is the row label, and the special responses are columns such as ``Don't know``. All
        items have the same class and format, differing only in ID and text.
    min_answered_items : int
        Fewest items that must have a substantive or special response.

    Raises
    ------
    ValueError
        If there are fewer than two items, an item is a matrix, item IDs repeat or equal the
        matrix ID, items differ in format, or ``min_answered_items`` is outside ``[1, len(items)]``.
    """

    question_type: ClassVar[QuestionType] = QuestionType.MATRIX

    items: tuple[Question[CellT], ...]
    min_answered_items: int = 1

    def __post_init__(self) -> None:
        super().__post_init__()
        if len(self.items) < 2:
            raise ValueError(f"Matrix question {self.id} needs at least two items.")
        first = self.items[0]
        if any(isinstance(item, MatrixQuestion) for item in self.items):
            raise ValueError(f"Items of matrix question {self.id} cannot be matrices.")
        item_ids = [item.id for item in self.items]
        if len(set(item_ids)) != len(item_ids) or self.id in item_ids:
            raise ValueError(
                f"Item IDs {item_ids} of matrix question {self.id} must be unique and differ from it."
            )
        if any(
            type(item) is not type(first)
            or replace(item, id=first.id, text=first.text) != first
            for item in self.items[1:]
        ):
            raise ValueError(
                f"Items of matrix question {self.id} must share one format, differing only in ID and text."
            )
        if not 1 <= self.min_answered_items <= len(self.items):
            raise ValueError(
                f"min_answered_items of question {self.id} must be between 1 and {len(self.items)}."
            )

    @classmethod
    def from_rows(
        cls,
        *,
        id: str,
        text: str,
        template: Question[CellT],
        rows: Sequence[tuple[str, str]],
        min_answered_items: int = 1,
        special_responses: SpecialResponses | None = None,
    ) -> Self:
        """
        Create a matrix whose items copy one template, changing only their IDs and texts.

        Parameters
        ----------
        id : str
            Identifier of the matrix.
        text : str
            Text shown above the grid.
        template : Question[CellT]
            Question whose format every row shares. Its own ID and text are not used.
        rows : Sequence[tuple[str, str]]
            ID and label of each row, such as ``("Q5_1", "Price")``.
        min_answered_items : int
            Fewest items that must have a substantive or special response.
        special_responses : SpecialResponses | None
            Responses offered for the whole matrix, such as ``Prefer not to answer``.
            ``None`` offers none.

        Returns
        -------
        Self
            Matrix with one item per row.
        """
        return cls(
            id=id,
            text=text,
            items=tuple(
                replace(template, id=row_id, text=row_text) for row_id, row_text in rows
            ),
            min_answered_items=min_answered_items,
            special_responses=SpecialResponses()
            if special_responses is None
            else special_responses,
        )

    @override
    def is_value_code(self, code: int) -> bool:
        """
        Whether the code is a value code or a special-response code of any item.

        A special response of the whole matrix must be told apart from every answer of a row.
        """
        return any(
            item.is_value_code(code) or code in item.special_responses
            for item in self.items
        )

    @property
    def item_ids(self) -> tuple[str, ...]:
        """
        IDs of the items in displayed order.
        """
        return tuple(item.id for item in self.items)

    @property
    @override
    def measurement_level(self) -> MeasurementLevel | None:
        """
        Level of measurement shared by every item.
        """
        return self.items[0].measurement_level

    @override
    def is_value(self, value: AnswerValue) -> TypeGuard[MatrixAnswer]:
        """
        Whether the value is a ``MatrixAnswer`` whose recorded item values have their items' answer types.
        """
        if not isinstance(value, MatrixAnswer):
            return False
        recorded = ((item, value.items.get(item.id)) for item in self.items)
        return all(
            answer is None or answer.value is None or item.is_value(answer.value)
            for item, answer in recorded
        )

    @override
    def validate(self, value: MatrixAnswer) -> None:
        """
        Check every item's answer against its item, and the number of items answered.

        Raises
        ------
        TypeError
            If an item's value does not have the item's answer type, which :meth:`is_value` rules out.
        InvalidAnswerError
            If an item ID is unknown, an item's answer breaks a constraint or uses a special
            code the item does not offer, or too few items are answered.
        """
        unknown = sorted(set(value) - set(self.item_ids))
        if unknown:
            raise InvalidAnswerError(
                f"Items {unknown} are not items of matrix question {self.id}."
            )
        for item in self.items:
            item.check(value.answer(item.id))
        answered_count = sum(value.answer(item.id).is_given for item in self.items)
        if answered_count < self.min_answered_items:
            raise InvalidAnswerError(
                f"Matrix question {self.id} needs at least {self.min_answered_items} items answered, not {answered_count}."
            )
