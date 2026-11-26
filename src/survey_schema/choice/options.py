from collections.abc import Iterator, Sequence
from dataclasses import dataclass, field
from typing import Self

from ..answer.error import InvalidAnswerError
from ..answer.selection import ChoiceSelection
from .option import ChoiceOption


@dataclass(frozen=True)
class ChoiceOptions:
    """
    Ordered set of options of a choice, ranking, best-worst, or constant-sum question.

    Parameters
    ----------
    items : tuple[ChoiceOption, ...]
        Options in defined order.

    Raises
    ------
    ValueError
        If there are fewer than two options, or codes or labels repeat.

    Examples
    --------
    >>> options = ChoiceOptions.from_labels(["Yes", "No", "Not sure"])
    >>> options[2].label
    'No'
    """

    items: tuple[ChoiceOption, ...]
    _index: dict[int, ChoiceOption] = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        if len(self.items) < 2:
            raise ValueError("A list of options needs at least two options.")
        index = {option.code: option for option in self.items}
        if len(index) != len(self.items):
            raise ValueError("Option codes must be unique.")
        if len({option.label for option in self.items}) != len(self.items):
            raise ValueError("Option labels must be unique.")
        object.__setattr__(self, "_index", index)

    @classmethod
    def from_labels(cls, labels: Sequence[str], *, start: int = 1) -> Self:
        """
        Create plain options numbered in defined order.

        Parameters
        ----------
        labels : Sequence[str]
            Displayed text of each option.
        start : int
            Code of the first option.

        Returns
        -------
        Self
            Options coded ``start``, ``start + 1``, and so on.
        """
        return cls(
            tuple(
                ChoiceOption(start + offset, label)
                for offset, label in enumerate(labels)
            )
        )

    @classmethod
    def yes_no(cls, *, yes: str = "Yes", no: str = "No") -> Self:
        """
        Create the two options of a yes-or-no question, coded 1 and 2.

        Parameters
        ----------
        yes : str
            Label of the affirmative option, coded 1, such as ``I agree``.
        no : str
            Label of the negative option, coded 2.

        Returns
        -------
        Self
            Options ``1. yes`` and ``2. no``.
        """
        return cls.from_labels([yes, no])

    def __getitem__(self, code: int) -> ChoiceOption:
        return self._index[code]

    def __contains__(self, code: object) -> bool:
        return code in self._index

    def __iter__(self) -> Iterator[ChoiceOption]:
        return iter(self.items)

    def __len__(self) -> int:
        return len(self.items)

    @property
    def codes(self) -> tuple[int, ...]:
        """
        Option codes in defined order.
        """
        return tuple(option.code for option in self.items)

    @property
    def is_exclusive_included(self) -> bool:
        """
        Whether any option is exclusive.
        """
        return any(option.is_exclusive for option in self.items)

    @property
    def is_free_text_included(self) -> bool:
        """
        Whether any option has a field to write in.
        """
        return any(option.is_free_text_allowed for option in self.items)

    def validate(self, selection: ChoiceSelection) -> None:
        """
        Check that a selection refers to one of the options and uses its field correctly.

        Parameters
        ----------
        selection : ChoiceSelection
            Selection to check.

        Raises
        ------
        InvalidAnswerError
            If the code is unknown, free text is given for an option without a field, or no free
            text is given for an option that requires it.
        """
        option = self._index.get(selection.code)
        if option is None:
            raise InvalidAnswerError(
                f"Option code {selection.code} is not one of {self.codes}."
            )
        if selection.free_text is not None and not option.is_free_text_allowed:
            raise InvalidAnswerError(
                f"Option {selection.code} does not accept free text."
            )
        if selection.free_text is None and option.is_free_text_required:
            raise InvalidAnswerError(f"Option {selection.code} requires free text.")
