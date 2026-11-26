# pyright: reportImportCycles=false
# Answer, AnswerValue, and MatrixAnswer refer to each other, because a matrix answer holds answers.
from datetime import date, time, timedelta
from decimal import Decimal
from typing import TYPE_CHECKING

from .best_worst import BestWorstChoice
from .option_amount import OptionAmount
from .selection import ChoiceSelection
from .year_month import YearMonth

if TYPE_CHECKING:
    # Imported only for type checking: MatrixAnswer holds Answer, whose type bound is this alias,
    # and the alias is evaluated lazily, so a runtime import would only create a cycle.
    from .matrix import MatrixAnswer

type AnswerValue = (
    int
    | Decimal
    | str
    | date
    | YearMonth
    | time
    | timedelta
    | ChoiceSelection
    | BestWorstChoice
    | tuple[ChoiceSelection, ...]
    | tuple[OptionAmount, ...]
    | tuple[str, ...]
    | MatrixAnswer
)
"""Union of the value types of every question type."""
