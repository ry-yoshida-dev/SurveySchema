from enum import Enum


class SpecialResponseKind(Enum):
    """
    Meaning of a special response, which tabulation keeps apart from substantive answers.
    """

    DONT_KNOW = "dont_know"
    """The respondent does not know the answer."""

    NO_OPINION = "no_opinion"
    """The respondent has no opinion on the matter."""

    REFUSED = "refused"
    """
    The respondent declines to answer, whether by choosing ``Prefer not to answer`` or by refusing
    in an interview.
    """

    DOES_NOT_APPLY = "does_not_apply"
    """The respondent states that the question does not apply to them."""
