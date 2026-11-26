from enum import Enum


class QuestionType(Enum):
    """
    Response format of a question, which decides the type of its answer value.

    Each member corresponds to exactly one question class in :mod:`survey_schema.questions`,
    and names that format independently of the class.
    """

    SINGLE_CHOICE = "single_choice"
    """One option out of several (SA), including yes or no. The answer is a ``ChoiceSelection``."""

    MULTIPLE_CHOICE = "multiple_choice"
    """Any number of options, optionally limited (MA and LA). The answer is a ``tuple[ChoiceSelection, ...]``."""

    RATING_SCALE = "rating_scale"
    """A point on a numbered scale, such as a Likert scale, NPS, or semantic differential. The answer is an ``int``."""

    VISUAL_ANALOG_SCALE = "visual_analog_scale"
    """A position on a continuous line or slider. The answer is a ``Decimal``."""

    RANKING = "ranking"
    """Options put in order of preference. The answer is a ``tuple[ChoiceSelection, ...]`` from rank 1."""

    BEST_WORST = "best_worst"
    """The best and the worst of a set of options (MaxDiff). The answer is a ``BestWorstChoice``."""

    CONSTANT_SUM = "constant_sum"
    """A fixed total distributed across options. The answer is a ``tuple[OptionAmount, ...]``."""

    INTEGER = "integer"
    """A whole number entered, such as an age, a count, or a year. The answer is an ``int``."""

    REAL_NUMBER = "real_number"
    """A number with a fractional part entered, such as a height. The answer is a ``Decimal``."""

    DATE = "date"
    """A calendar date entered. The answer is a ``datetime.date``."""

    YEAR_MONTH = "year_month"
    """A year and a month entered, such as a birth month. The answer is a ``YearMonth``."""

    TIME_OF_DAY = "time_of_day"
    """A clock time entered. The answer is a ``datetime.time``."""

    DURATION = "duration"
    """A length of time entered, such as hours and minutes of sleep. The answer is a ``datetime.timedelta``."""

    FREE_TEXT = "free_text"
    """Text entered freely. The answer is a ``str``."""

    FREE_TEXT_LIST = "free_text_list"
    """Several short texts entered in separate fields. The answer is a ``tuple[str, ...]``."""

    MATRIX = "matrix"
    """A grid of items sharing one answer format. The answer is a ``MatrixAnswer`` of per-item answers."""
