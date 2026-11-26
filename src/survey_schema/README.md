# survey_schema

## Overview

Typed, medium-independent definitions of survey question types and the formats of their answers.

## Components

| Component | Description |
|---|---|
| [question.py](question.py) | `Question`, the abstract question that fixes the type and constraints of its answer. |
| [questions/](questions/README.md) | Concrete question types. |
| [question_type.py](question_type.py) | `QuestionType`, the enum of response formats. |
| [choice/](choice/README.md) | Options of choice, ranking, best-worst, and constant-sum questions. |
| [rating_scale.py](rating_scale.py) | `RatingScale`, an evenly spaced numbered scale with anchor labels. |
| [bounds.py](bounds.py) | `Bounds`, the inclusive range of an entered number, date, month, time, or duration. |
| [decimal_places.py](decimal_places.py) | `count_decimal_places`, the digits a decimal answer needs after the point. |
| [comparable.py](comparable.py) | `Comparable`, the protocol of values that `Bounds` can order. |
| [special/](special/README.md) | Special responses such as ``Don't know`` and ``Refused``. |
| [answer/](answer/README.md) | Answers, their value types and statuses, and respondents' responses. |
