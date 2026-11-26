import pytest

from survey_schema import Answer, AnswerStatus, Response


def test_answer_defaults_to_not_reached() -> None:
    response = Response(respondent_id="1", answers={"Q1": Answer.answered(1)})
    assert response.answer("Q1").value == 1
    assert response.answer("Q2").status is AnswerStatus.NOT_REACHED


def test_rejects_blank_id_and_copies_answers() -> None:
    with pytest.raises(ValueError):
        Response(respondent_id=" ", answers={})
    answers = {"Q1": Answer.answered(1)}
    response = Response(respondent_id="1", answers=answers)
    answers["Q2"] = Answer.answered(2)
    assert "Q2" not in response.answers


def test_is_hashable() -> None:
    response = Response(respondent_id="1", answers={"Q1": Answer.answered(1)})
    assert hash(response) == hash(Response(respondent_id="1", answers={}))
