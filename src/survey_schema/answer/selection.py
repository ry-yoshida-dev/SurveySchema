from dataclasses import dataclass


@dataclass(frozen=True)
class ChoiceSelection:
    """
    One option chosen by a respondent.

    Parameters
    ----------
    code : int
        Code of the chosen option.
    free_text : str | None
        Text entered in the option's field, such as the content of ``Other``.
        ``None`` when nothing is entered.

    Raises
    ------
    TypeError
        If ``code`` is a ``bool``.
    ValueError
        If ``free_text`` is blank. Use ``None`` for an empty field.
    """

    code: int
    free_text: str | None = None

    def __post_init__(self) -> None:
        if isinstance(self.code, bool):
            raise TypeError("code must be an int, not a bool.")
        if self.free_text is not None and not self.free_text.strip():
            raise ValueError(
                "free_text must not be blank; use None when nothing is entered."
            )
