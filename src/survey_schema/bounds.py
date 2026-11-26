from dataclasses import dataclass

from .answer.error import InvalidAnswerError
from .comparable import Comparable


@dataclass(frozen=True, kw_only=True)
class Bounds[ComparableT: Comparable]:
    """
    Inclusive range that an entered value must fall within.

    Parameters
    ----------
    minimum : ComparableT | None
        Smallest accepted value. ``None`` leaves the range open below.
    maximum : ComparableT | None
        Largest accepted value. ``None`` leaves the range open above.

    Raises
    ------
    ValueError
        If an end is not equal to itself, such as a NaN, or ``minimum`` is greater than ``maximum``.
    """

    minimum: ComparableT | None = None
    maximum: ComparableT | None = None

    def __post_init__(self) -> None:
        # A NaN equals nothing, not even itself, so it cannot order anything.
        if any(end is not None and end != end for end in (self.minimum, self.maximum)):
            raise ValueError(
                f"Ends {self.minimum!r} and {self.maximum!r} must be comparable."
            )
        if (
            self.minimum is not None
            and self.maximum is not None
            and self.maximum < self.minimum
        ):
            raise ValueError(
                f"minimum {self.minimum!r} is greater than maximum {self.maximum!r}."
            )

    def __contains__(self, value: ComparableT) -> bool:
        if self.minimum is not None and value < self.minimum:
            return False
        return self.maximum is None or value <= self.maximum

    def validate(self, value: ComparableT) -> None:
        """
        Check that a value falls within the range.

        Parameters
        ----------
        value : ComparableT
            Value to check.

        Raises
        ------
        InvalidAnswerError
            If the value is outside the range.
        """
        if value not in self:
            raise InvalidAnswerError(
                f"{value!r} is outside the range [{self.minimum!r}, {self.maximum!r}]."
            )
