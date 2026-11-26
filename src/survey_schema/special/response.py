from dataclasses import KW_ONLY, dataclass

from .kind import SpecialResponseKind


@dataclass(frozen=True)
class SpecialResponse:
    """
    Response offered beside the substantive answers of a question, such as ``9. Don't know``.

    Parameters
    ----------
    code : int
        Number that identifies the response in tabulation, such as 9 or 99.
    label : str
        Displayed text.
    kind : SpecialResponseKind
        Meaning of the response.
    is_volunteered : bool
        Whether the response is recorded only when the respondent volunteers it, without being
        shown or read out, such as ``Refused`` in an interview or a note in a paper margin.

    Raises
    ------
    TypeError
        If ``code`` is a ``bool``.
    ValueError
        If ``label`` is blank.
    """

    code: int
    label: str
    kind: SpecialResponseKind
    _: KW_ONLY
    is_volunteered: bool = False

    def __post_init__(self) -> None:
        if isinstance(self.code, bool):
            raise TypeError("code must be an int, not a bool.")
        if not self.label.strip():
            raise ValueError("label must not be blank.")
