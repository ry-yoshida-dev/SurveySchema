from survey_schema import Answer, AnswerStatus, MatrixAnswer


def test_lookup_defaults_to_no_answer() -> None:
    matrix = MatrixAnswer({"Q1_1": Answer.answered(3), "Q1_2": Answer.special(9)})
    assert matrix.answer("Q1_1").value == 3
    assert matrix.answer("Q1_2").special_code == 9
    assert matrix.answer("Q1_3").status is AnswerStatus.NO_ANSWER
    assert list(matrix) == ["Q1_1", "Q1_2"] and len(matrix) == 2


def test_copies_items() -> None:
    items = {"Q1_1": Answer.answered(3)}
    matrix = MatrixAnswer(items)
    items["Q1_2"] = Answer.answered(4)
    assert "Q1_2" not in matrix


def test_is_hashable() -> None:
    items = {"Q1_1": Answer.answered(3)}
    matrix = MatrixAnswer(items)
    assert matrix == MatrixAnswer(dict(items))
    assert hash(matrix) == hash(MatrixAnswer(dict(items)))
    assert hash(Answer.answered(matrix)) == hash(Answer.answered(matrix))
