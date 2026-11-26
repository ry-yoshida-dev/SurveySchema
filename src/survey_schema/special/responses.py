from collections.abc import Iterator
from dataclasses import dataclass, field

from .response import SpecialResponse


@dataclass(frozen=True)
class SpecialResponses:
    """
    Special responses offered by one question, in displayed order. Empty when none are offered.

    A respondent gives at most one of them, and never together with a substantive answer. A
    response that may be combined under the question's own rules, such as ``None of the above``
    on a multiple-choice question, is an exclusive option instead.

    Parameters
    ----------
    items : tuple[SpecialResponse, ...]
        Special responses in displayed order.

    Raises
    ------
    ValueError
        If codes or labels repeat.
    """

    items: tuple[SpecialResponse, ...] = ()
    _index: dict[int, SpecialResponse] = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        index = {response.code: response for response in self.items}
        if len(index) != len(self.items):
            raise ValueError("Special response codes must be unique.")
        if len({response.label for response in self.items}) != len(self.items):
            raise ValueError("Special response labels must be unique.")
        object.__setattr__(self, "_index", index)

    def __getitem__(self, code: int) -> SpecialResponse:
        return self._index[code]

    def __contains__(self, code: object) -> bool:
        return code in self._index

    def __iter__(self) -> Iterator[SpecialResponse]:
        return iter(self.items)

    def __len__(self) -> int:
        return len(self.items)

    @property
    def codes(self) -> frozenset[int]:
        """
        Codes of every special response.
        """
        return frozenset(self._index)
