from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True)
class BestWorstChoice:
    """
    Options chosen as the best and the worst of one set.

    Parameters
    ----------
    best : int
        Code of the option chosen as the best, or the most important.
    worst : int
        Code of the option chosen as the worst, or the least important.

    Raises
    ------
    TypeError
        If a code is a ``bool``.
    ValueError
        If both codes are the same.
    """

    best: int
    worst: int

    def __post_init__(self) -> None:
        if isinstance(self.best, bool) or isinstance(self.worst, bool):
            raise TypeError("Codes must be int, not bool.")
        if self.best == self.worst:
            raise ValueError(
                f"Option {self.best} cannot be chosen as both the best and the worst."
            )
