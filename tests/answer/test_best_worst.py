import pytest

from survey_schema import BestWorstChoice


def test_fields() -> None:
    choice = BestWorstChoice(best=1, worst=3)
    assert (choice.best, choice.worst) == (1, 3)


def test_rejects_invalid_choices() -> None:
    with pytest.raises(ValueError):
        BestWorstChoice(best=2, worst=2)
    with pytest.raises(TypeError):
        BestWorstChoice(best=True, worst=2)
    with pytest.raises(TypeError):
        BestWorstChoice(best=2, worst=False)
