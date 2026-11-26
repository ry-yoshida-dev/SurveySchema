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
class RankingQuestion(Question[tuple[ChoiceSelection, ...]]):
    """
    Question answered by putting options in order of preference, without ties.

    The answer is a ``tuple[ChoiceSelection, ...]`` from rank 1 downward. Options left unranked
    are ranked below every ranked one.

    Parameters
    ----------
    options : ChoiceOptions
        Options to rank. They cannot be exclusive, but ``Other (please specify)`` may have a
        field to write in.
    min_ranks : int | None
        Fewest ranks to fill. ``None`` makes it equal to the most ranks.
    max_ranks : int | None
        Most ranks to fill, such as 3 for ``Rank your top three``. ``None`` means every option.

    Raises
    ------
    ValueError
        If an option is exclusive, or the limits are outside
        ``1 <= min_ranks <= max_ranks <= len(options)``.

    Examples
    --------
    ``Rank every option`` leaves both limits ``None``, ``Rank your top three`` sets
    ``max_ranks=3``, and ``Rank up to three`` sets ``min_ranks=1, max_ranks=3``.
    """

    question_type: ClassVar[QuestionType] = QuestionType.RANKING

    options: ChoiceOptions
    min_ranks: int | None = None
    max_ranks: int | None = None

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.options.is_exclusive_included:
            raise ValueError(
                f"Options of ranking question {self.id} cannot be exclusive."
            )
        if (
            not 1
            <= self.required_min_ranks
            <= self.required_max_ranks
            <= len(self.options)
        ):
            raise ValueError(
                f"Rank limits of question {self.id} must satisfy 1 <= min_ranks <= max_ranks <= {len(self.options)}."
            )

    @property
    def required_max_ranks(self) -> int:
        """
        Most ranks to fill, resolving ``None`` to the number of options.
        """
        return len(self.options) if self.max_ranks is None else self.max_ranks

    @property
    def required_min_ranks(self) -> int:
        """
        Fewest ranks to fill, resolving ``None`` to :attr:`required_max_ranks`.
        """
        return self.required_max_ranks if self.min_ranks is None else self.min_ranks

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
        Always ``ORDINAL``.
        """
        return MeasurementLevel.ORDINAL

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
        Check that distinct options fill a permitted number of ranks.

        Raises
        ------
        InvalidAnswerError
            If a selection is invalid or repeated, so that ranks are tied, or the number of ranks
            is outside the limits.
        """
        for selection in value:
            self.options.validate(selection)
        codes = [selection.code for selection in value]
        if len(set(codes)) != len(codes):
            raise InvalidAnswerError(
                f"Options {codes} of question {self.id} repeat, so ranks are tied."
            )
        if not self.required_min_ranks <= len(codes) <= self.required_max_ranks:
            raise InvalidAnswerError(
                f"Question {self.id} needs {self.required_min_ranks} to {self.required_max_ranks} ranks but {len(codes)} were given."
            )
