from dataclasses import dataclass
from typing import override


@dataclass(frozen=True, order=True)
class YearMonth:
    """
    Calendar month of a year, such as a birth month or the month a job started.

    Instances order chronologically. Years in another calendar, such as Japanese eras, are
    converted to the Gregorian year when captured.

    Parameters
    ----------
    year : int
        Gregorian year.
    month : int
        Month from 1 to 12.

    Raises
    ------
    TypeError
        If ``year`` or ``month`` is a ``bool``.
    ValueError
        If ``month`` is outside 1 to 12, or ``year`` is outside 1 to 9999 like ``datetime.date``.

    Examples
    --------
    >>> YearMonth(1990, 4) < YearMonth(1991, 1)
    True
    """

    year: int
    month: int

    def __post_init__(self) -> None:
        if isinstance(self.year, bool) or isinstance(self.month, bool):
            raise TypeError("year and month must be int, not bool.")
        if not 1 <= self.year <= 9999:
            raise ValueError(f"year {self.year} must be between 1 and 9999.")
        if not 1 <= self.month <= 12:
            raise ValueError(f"month {self.month} must be between 1 and 12.")

    @override
    def __str__(self) -> str:
        return f"{self.year:04d}-{self.month:02d}"
