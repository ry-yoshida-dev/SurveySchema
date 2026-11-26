from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Self

from .answer.error import InvalidAnswerError


@dataclass(frozen=True, kw_only=True)
class RatingScale:
    """
    Numbered scale of evenly spaced integer points, such as 1 to 5, -3 to +3, or 0 to 100 by 10.

    Responses outside the scale, such as ``Don't know``, are the question's special responses.
    A scale whose points are not evenly spaced is an ordered single-choice question instead.

    Parameters
    ----------
    minimum : int
        Lowest point.
    maximum : int
        Highest point.
    step : int
        Distance between neighboring points.
    anchors : Mapping[int, str]
        Labels shown at some or all points, such as ``{1: "Disagree", 5: "Agree"}``. A semantic
        differential labels both ends with opposite adjectives, such as ``Cold`` and ``Warm``.

    Raises
    ------
    TypeError
        If ``minimum``, ``maximum``, or ``step`` is a ``bool``.
    ValueError
        If ``minimum`` is not less than ``maximum``, ``step`` is not positive or does not reach
        ``maximum`` from ``minimum``, an anchor is not a point, or a label is blank.

    Examples
    --------
    >>> likert = RatingScale(minimum=1, maximum=5, anchors={1: "Disagree", 3: "Neutral", 5: "Agree"})
    >>> likert.points
    (1, 2, 3, 4, 5)
    >>> RatingScale(minimum=0, maximum=100, step=25).points
    (0, 25, 50, 75, 100)
    """

    minimum: int
    maximum: int
    step: int = 1
    anchors: Mapping[int, str] = field(default_factory=dict[int, str], hash=False)

    def __post_init__(self) -> None:
        if any(
            isinstance(number, bool)
            for number in (self.minimum, self.maximum, self.step)
        ):
            raise TypeError("minimum, maximum, and step must be int, not bool.")
        if self.minimum >= self.maximum:
            raise ValueError(
                f"minimum {self.minimum} must be less than maximum {self.maximum}."
            )
        if self.step <= 0:
            raise ValueError(f"step {self.step} must be positive.")
        if (self.maximum - self.minimum) % self.step != 0:
            raise ValueError(
                f"step {self.step} does not reach maximum {self.maximum} from minimum {self.minimum}."
            )
        off_scale = [point for point in self.anchors if point not in self]
        if off_scale:
            raise ValueError(f"Anchors {off_scale} are not points of the scale.")
        if any(not label.strip() for label in self.anchors.values()):
            raise ValueError("Anchor labels must not be blank.")
        # Copy into a read-only view so the frozen scale cannot change through the caller's dict.
        object.__setattr__(self, "anchors", MappingProxyType(dict(self.anchors)))

    @classmethod
    def bipolar(cls, *, minimum: int, maximum: int, left: str, right: str) -> Self:
        """
        Create a scale between two opposite adjectives, as in the semantic differential method.

        Parameters
        ----------
        minimum : int
            Point at ``left``.
        maximum : int
            Point at ``right``.
        left : str
            Adjective at the low end, such as ``Cold``.
        right : str
            Adjective at the high end, such as ``Warm``.

        Returns
        -------
        Self
            Scale anchored only at both ends.

        Raises
        ------
        ValueError
            If both adjectives are the same, or the scale is invalid.
        """
        if left.strip() == right.strip():
            raise ValueError(f"Both ends of the scale are {left!r}; they must differ.")
        return cls(
            minimum=minimum, maximum=maximum, anchors={minimum: left, maximum: right}
        )

    def __contains__(self, value: int) -> bool:
        return (
            self.minimum <= value <= self.maximum
            and (value - self.minimum) % self.step == 0
        )

    @property
    def points(self) -> tuple[int, ...]:
        """
        Every point of the scale in ascending order.
        """
        return tuple(range(self.minimum, self.maximum + 1, self.step))

    @property
    def point_count(self) -> int:
        """
        Number of points on the scale.
        """
        return (self.maximum - self.minimum) // self.step + 1

    def validate(self, value: int) -> None:
        """
        Check that a value is a point on the scale.

        Parameters
        ----------
        value : int
            Value to check.

        Raises
        ------
        InvalidAnswerError
            If the value is not a point of the scale.
        """
        if value not in self:
            raise InvalidAnswerError(
                f"{value} is not a point of the scale {self.points}."
            )
