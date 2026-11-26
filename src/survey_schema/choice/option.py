from dataclasses import KW_ONLY, dataclass


@dataclass(frozen=True)
class ChoiceOption:
    """
    One option of a choice question, such as ``1. Satisfied``.

    Parameters
    ----------
    code : int
        Number that identifies the option in tabulation, usually the displayed number.
    label : str
        Displayed text of the option.
    is_exclusive : bool
        Whether choosing the option rules out every other option, such as ``None of the above``.
        Applies only to multiple-choice questions.
    is_free_text_allowed : bool
        Whether the option has a field to write in, such as ``Other (please specify)``.
    is_free_text_required : bool
        Whether choosing the option requires writing in its field. Requires ``is_free_text_allowed``.

    Raises
    ------
    TypeError
        If ``code`` is a ``bool``.
    ValueError
        If ``label`` is blank, or free text is required but not allowed.
    """

    code: int
    label: str
    _: KW_ONLY
    is_exclusive: bool = False
    is_free_text_allowed: bool = False
    is_free_text_required: bool = False

    def __post_init__(self) -> None:
        if isinstance(self.code, bool):
            raise TypeError("code must be an int, not a bool.")
        if not self.label.strip():
            raise ValueError("label must not be blank.")
        if self.is_free_text_required and not self.is_free_text_allowed:
            raise ValueError(
                f"Option {self.code} requires free text, so it must allow free text."
            )
