# SurveySchema

## Overview

`survey_schema` defines which kinds of survey questions exist and the format of each one's answer, independent of the medium: paper, web, telephone, or face-to-face. Each question type fixes the Python type of its answer, its constraints, and its level of measurement. Answers record why a value is missing (blank, routed past, not reached, invalid, or unreadable) and keep what was captured when it cannot be used, and any question can offer special responses such as ``Don't know``.

| Category | Question types |
|---|---|
| [Choice](src/survey_schema/questions/README.md) | Single choice (SA, including yes or no), multiple choice (MA / LA) |
| [Scale](src/survey_schema/questions/README.md) | Rating scale (Likert, NPS, semantic differential), visual analog scale |
| [Ordering](src/survey_schema/questions/README.md) | Ranking, best-worst (MaxDiff), constant sum |
| [Entry](src/survey_schema/questions/README.md) | Integer, real number, date, year and month, time of day, duration, free text, list of free texts |
| [Grid](src/survey_schema/questions/README.md) | Matrix of items sharing one format |

See [src/survey_schema/questions/README.md](src/survey_schema/questions/README.md) for how other formats, such as paired comparisons and conjoint tasks, are built from these types, and [src/survey_schema/README.md](src/survey_schema/README.md) for the package layout.

## Installation

Requires Python 3.12+.

```bash
git clone https://github.com/ry-yoshida-dev/SurveySchema.git
cd SurveySchema
pip install .
```

## Usage

```python
from decimal import Decimal

from survey_schema import (
    Answer,
    AnswerStatus,
    Bounds,
    ChoiceOption,
    ChoiceOptions,
    ChoiceSelection,
    IntegerQuestion,
    MatrixAnswer,
    MatrixQuestion,
    MultipleChoiceQuestion,
    RatingScale,
    RatingScaleQuestion,
    RealNumberQuestion,
    SpecialResponse,
    SpecialResponseKind,
    SpecialResponses,
)

age = IntegerQuestion(
    id="Q1",
    text="How old are you?",
    bounds=Bounds(minimum=0, maximum=120),  # special codes such as 999 must lie outside
    unit="years",
    special_responses=SpecialResponses(
        (SpecialResponse(999, "Prefer not to answer", SpecialResponseKind.REFUSED),)
    ),
)
bought = MultipleChoiceQuestion(
    id="Q2",
    text="What did you buy?",
    options=ChoiceOptions(
        (
            ChoiceOption(1, "Food"),
            ChoiceOption(2, "Clothes"),
            ChoiceOption(3, "Other", is_free_text_allowed=True),
            ChoiceOption(9, "Nothing", is_exclusive=True),
        )
    ),
)
satisfaction = MatrixQuestion.from_rows(
    id="Q3",
    text="How satisfied are you with each?",
    template=RatingScaleQuestion(
        id="_",
        text="_",
        scale=RatingScale(
            minimum=1, maximum=5, anchors={1: "Dissatisfied", 5: "Satisfied"}
        ),
        special_responses=SpecialResponses(
            (SpecialResponse(9, "Don't know", SpecialResponseKind.DONT_KNOW),)
        ),
    ),
    rows=[("Q3_1", "Price"), ("Q3_2", "Service")],
)
height = RealNumberQuestion(id="Q4", text="Your height?", unit="cm", decimal_places=1)

age.answer(34)  # Answer(status=ANSWERED, value=34)
age.check(Answer.special(999))  # passes: 999 is an offered special response
bought.answer((ChoiceSelection(1), ChoiceSelection(3, "Books")))
bought.check(Answer.unreadable("Fo?d"))  # keeps what can be made out
satisfaction.answer(
    MatrixAnswer({"Q3_1": Answer.answered(4), "Q3_2": Answer.special(9)})
)
height.answer(Decimal("172.5"))
bought.measurement_level  # MeasurementLevel.NOMINAL
```

`question.answer(value)` raises `InvalidAnswerError` when a value breaks a constraint, such as `bought.answer((ChoiceSelection(1), ChoiceSelection(9)))`, so the answer can be recorded as `Answer.invalid((ChoiceSelection(1), ChoiceSelection(9)))`, which keeps the captured marks.
