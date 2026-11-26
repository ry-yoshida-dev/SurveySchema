from dataclasses import dataclass
from decimal import MAX_PREC, Decimal, localcontext
from typing import ClassVar, TypeGuard, override

from variable import MeasurementLevel

from ..answer.error import InvalidAnswerError
from ..answer.value import AnswerValue
from ..question import Question
from ..question_type import QuestionType


@dataclass(frozen=True, kw_only=True)
class VisualAnalogScaleQuestion(Question[Decimal]):
    """
    Question answered by marking a position on a continuous line between two anchors (VAS).

    Shown as a printed line on paper or a slider on screen. The answer is a ``Decimal`` between
    :attr:`minimum` at the left anchor and :attr:`maximum` at the right anchor; a capture tool
    converts a measured distance, such as millimeters on paper, into this range. A slider that
    snaps to a few labeled points is a rating scale instead.

    Parameters
    ----------
    left_anchor : str
        Label at the left end, such as ``No pain``.
    right_anchor : str
        Label at the right end, such as ``Worst pain imaginable``.
    minimum : Decimal
        Value at the left end.
    maximum : Decimal
        Value at the right end.
    resolution : Decimal | None
        Smallest step that can be recorded from ``minimum``, such as 1 mm on paper or the step
        of a slider. ``None`` records any position.

    Raises
    ------
    ValueError
        If an anchor is blank, the ends are not finite with ``minimum < maximum``, or
        ``resolution`` is not positive and finite.
    """

    question_type: ClassVar[QuestionType] = QuestionType.VISUAL_ANALOG_SCALE

    left_anchor: str
    right_anchor: str
    minimum: Decimal = Decimal(0)
    maximum: Decimal = Decimal(100)
    resolution: Decimal | None = None

    def __post_init__(self) -> None:
        # Fields are checked before the base class compares special-response codes with them.
        if not self.left_anchor.strip() or not self.right_anchor.strip():
            raise ValueError(f"Anchors of question {self.id} must not be blank.")
        if not (
            self.minimum.is_finite()
            and self.maximum.is_finite()
            and self.minimum < self.maximum
        ):
            raise ValueError(
                f"Ends of question {self.id} must be finite with minimum < maximum."
            )
        if self.resolution is not None and not (
            self.resolution.is_finite() and self.resolution > 0
        ):
            raise ValueError(
                f"resolution of question {self.id} must be positive and finite."
            )
        super().__post_init__()

    def _is_on_step(self, value: Decimal, resolution: Decimal) -> bool:
        # Compute exactly: the default context cannot divide past 28 significant digits.
        with localcontext(prec=MAX_PREC):
            return (value - self.minimum) % resolution == 0

    @override
    def is_value_code(self, code: int) -> bool:
        """
        Whether the code lies on the line at a recordable step.
        """
        return self.minimum <= code <= self.maximum and (
            self.resolution is None or self._is_on_step(Decimal(code), self.resolution)
        )

    @property
    @override
    def measurement_level(self) -> MeasurementLevel:
        """
        Always ``INTERVAL``.
        """
        return MeasurementLevel.INTERVAL

    @override
    def is_value(self, value: AnswerValue) -> TypeGuard[Decimal]:
        """
        Whether the value is a ``Decimal``.
        """
        return isinstance(value, Decimal)

    @override
    def validate(self, value: Decimal) -> None:
        """
        Check that the position lies on the line at a recordable step.

        Raises
        ------
        InvalidAnswerError
            If the value is not finite, lies outside ``[minimum, maximum]``, or falls between
            two steps of :attr:`resolution`.
        """
        if not value.is_finite() or not self.minimum <= value <= self.maximum:
            raise InvalidAnswerError(
                f"Position {value} of question {self.id} is outside [{self.minimum}, {self.maximum}]."
            )
        if self.resolution is not None and not self._is_on_step(value, self.resolution):
            raise InvalidAnswerError(
                f"Position {value} of question {self.id} is not a multiple of {self.resolution} from {self.minimum}."
            )
