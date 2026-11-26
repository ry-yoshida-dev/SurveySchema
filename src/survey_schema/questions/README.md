# questions

## Overview

Concrete question types. Each fixes the Python type of its answer value, independent of how the question is shown. Every type also accepts the special responses it offers, such as ``Don't know``.

Formats whose answers depend on the medium or are not given by the respondent are excluded: file upload, signature, drawing, click positions on an image, device location, and calculated or hidden fields.

## Components

| Component | Category | Answer value | Measurement level | Description |
|---|---|---|---|---|
| [single_choice.py](single_choice.py) | Choice | `ChoiceSelection` | Nominal, or ordinal if ordered | `SingleChoiceQuestion`: exactly one option (SA), including yes or no. |
| [multiple_choice.py](multiple_choice.py) | Choice | `tuple[ChoiceSelection, ...]` | Nominal | `MultipleChoiceQuestion`: any or a limited number of options (MA / LA). |
| [rating_scale.py](rating_scale.py) | Scale | `int` | Ordinal | `RatingScaleQuestion`: a point on a numbered scale, such as Likert, NPS, or a semantic differential. |
| [visual_analog_scale.py](visual_analog_scale.py) | Scale | `Decimal` | Interval | `VisualAnalogScaleQuestion`: a position on a line or slider. |
| [ranking.py](ranking.py) | Ordering | `tuple[ChoiceSelection, ...]` | Ordinal | `RankingQuestion`: options from rank 1, for all, exactly *k*, or up to *k*. |
| [best_worst.py](best_worst.py) | Ordering | `BestWorstChoice` | Ordinal | `BestWorstQuestion`: the best and the worst of a set (MaxDiff). |
| [constant_sum.py](constant_sum.py) | Ordering | `tuple[OptionAmount, ...]` | Ratio | `ConstantSumQuestion`: a fixed total distributed across options. |
| [integer.py](integer.py) | Entry | `int` | Ratio or interval | `IntegerQuestion`: a whole number, such as an age or a year. |
| [real_number.py](real_number.py) | Entry | `Decimal` | Ratio or interval | `RealNumberQuestion`: a number with a fractional part, such as a height. |
| [date.py](date.py) | Entry | `datetime.date` | Interval | `DateQuestion`: a calendar date. |
| [year_month.py](year_month.py) | Entry | `YearMonth` | Interval | `YearMonthQuestion`: a year and a month, such as a birth month. |
| [time_of_day.py](time_of_day.py) | Entry | `datetime.time` | Cyclic | `TimeOfDayQuestion`: a clock time. |
| [duration.py](duration.py) | Entry | `datetime.timedelta` | Ratio | `DurationQuestion`: a length of time, such as hours and minutes. |
| [free_text.py](free_text.py) | Entry | `str` | None | `FreeTextQuestion`: free text, with optional length limits and a pattern. |
| [free_text_list.py](free_text_list.py) | Entry | `tuple[str, ...]` | None | `FreeTextListQuestion`: several short texts, such as up to three brands. |
| [matrix.py](matrix.py) | Grid | `MatrixAnswer` | That of its items | `MatrixQuestion`: items sharing one format, each with its own answer. |

## Examples

Other formats are built from these types.

| Format | Built as |
|---|---|
| Yes or no, consent | `SingleChoiceQuestion` with `ChoiceOptions.yes_no()` |
| Dropdown, image choice | `SingleChoiceQuestion` or `MultipleChoiceQuestion`; the image is presentation |
| Star rating, stepped slider, NPS, probability scale | `RatingScaleQuestion`, with `step` where points skip |
| Semantic differential | `RatingScaleQuestion` with `RatingScale.bipolar()` |
| Feeling thermometer | `IntegerQuestion` from 0 to 100, or `VisualAnalogScaleQuestion` |
| Matrix of SA, MA, ratings, or numbers | `MatrixQuestion` over the matching item type |
| Quantity per option, such as times used | `MatrixQuestion` of `IntegerQuestion` |
| Paired comparison | Two-option `SingleChoiceQuestion` per pair, or a bipolar `RatingScaleQuestion` for graded preference |
| Choice-based conjoint task | `SingleChoiceQuestion` over the profiles, one per task |
| Guttman, Bogardus, Thurstone | `MultipleChoiceQuestion` of the statements, or an ordered `SingleChoiceQuestion` |
| Closed card sort | `MatrixQuestion` of `SingleChoiceQuestion`, with the cards as items and the groups as options |
| Number with a unit the respondent chooses, such as kg or lb | `RealNumberQuestion` and a `SingleChoiceQuestion` of units; lengths of time are `DurationQuestion` |
| Year only | `IntegerQuestion` with `is_zero_absolute=False` |
| Postal code, telephone number, email address | `FreeTextQuestion` with a `pattern` |
| Range such as ``from __ to __``, cascading choice | One question per field |
