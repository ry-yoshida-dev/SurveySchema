class InvalidAnswerError(ValueError):
    """
    Raised when an answer has the right type but breaks a constraint of its question.

    A capture tool can catch this error and record the answer as ``AnswerStatus.INVALID``.
    """
