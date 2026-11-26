from typing import Protocol, Self


class Comparable(Protocol):
    """
    Type that can be ordered against values of its own type.
    """

    def __lt__(self, other: Self, /) -> bool: ...

    def __le__(self, other: Self, /) -> bool: ...
