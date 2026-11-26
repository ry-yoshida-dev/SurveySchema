import pytest

from survey_schema import ChoiceSelection


def test_rejects_bool_code_and_blank_text() -> None:
    with pytest.raises(TypeError):
        ChoiceSelection(True)
    with pytest.raises(ValueError):
        ChoiceSelection(1, " ")
