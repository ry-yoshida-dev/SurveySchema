# answer

## Overview

Answers of respondents, their value types, the reasons an answer is missing, and whole responses.

## Components

| Component | Description |
|---|---|
| [answer.py](answer.py) | `Answer`, one answer with its status and its value, special-response code, or captured content. |
| [status.py](status.py) | `AnswerStatus`, such as answered, special response, no answer, not applicable, not reached, invalid, and unreadable. |
| [value.py](value.py) | `AnswerValue`, the union of every answer value type. |
| [selection.py](selection.py) | `ChoiceSelection`, one option chosen by a respondent, with optional free text. |
| [option_amount.py](option_amount.py) | `OptionAmount`, the amount given to one option of a constant-sum question. |
| [best_worst.py](best_worst.py) | `BestWorstChoice`, the options chosen as the best and the worst. |
| [year_month.py](year_month.py) | `YearMonth`, a month of a year. |
| [matrix.py](matrix.py) | `MatrixAnswer`, the answers to the items of a matrix, each with its own status. |
| [response.py](response.py) | `Response`, every answer of one respondent. |
| [error.py](error.py) | `InvalidAnswerError`, raised when a value breaks a question's constraint. |
