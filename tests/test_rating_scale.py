import pytest

from survey_schema import InvalidAnswerError, RatingScale

SCALE = RatingScale(minimum=1, maximum=5, anchors={1: "Disagree", 5: "Agree"})
STEPPED = RatingScale(minimum=0, maximum=100, step=25)


def test_points() -> None:
    assert SCALE.points == (1, 2, 3, 4, 5)
    assert SCALE.point_count == 5
    assert 5 in SCALE and 6 not in SCALE


def test_step() -> None:
    assert STEPPED.points == (0, 25, 50, 75, 100)
    assert STEPPED.point_count == 5
    assert 75 in STEPPED and 30 not in STEPPED and 125 not in STEPPED
    with pytest.raises(InvalidAnswerError):
        STEPPED.validate(30)


def test_validate() -> None:
    SCALE.validate(3)
    with pytest.raises(InvalidAnswerError):
        SCALE.validate(6)


def test_bipolar() -> None:
    scale = RatingScale.bipolar(minimum=-3, maximum=3, left="Cold", right="Warm")
    assert scale.points == (-3, -2, -1, 0, 1, 2, 3)
    assert dict(scale.anchors) == {-3: "Cold", 3: "Warm"}


@pytest.mark.parametrize(
    ("left", "right", "minimum", "maximum"),
    [("Cold", "Cold", 1, 7), ("Cold", " Cold ", 1, 7), ("Cold", "Warm", 7, 1)],
)
def test_bipolar_rejects_invalid_ends(
    left: str, right: str, minimum: int, maximum: int
) -> None:
    with pytest.raises(ValueError):
        RatingScale.bipolar(minimum=minimum, maximum=maximum, left=left, right=right)


@pytest.mark.parametrize(
    ("minimum", "maximum", "step", "anchors"),
    [
        (5, 1, 1, {}),
        (1, 1, 1, {}),
        (1, 5, 0, {}),
        (1, 5, -1, {}),
        (0, 10, 3, {}),
        (1, 5, 1, {6: "Off"}),
        (0, 10, 5, {3: "Off step"}),
        (1, 5, 1, {1: " "}),
    ],
)
def test_rejects_invalid_definitions(
    minimum: int, maximum: int, step: int, anchors: dict[int, str]
) -> None:
    with pytest.raises(ValueError):
        RatingScale(minimum=minimum, maximum=maximum, step=step, anchors=anchors)


def test_anchors_are_copied() -> None:
    anchors = {1: "Low"}
    scale = RatingScale(minimum=1, maximum=3, anchors=anchors)
    anchors[2] = "Mid"
    assert dict(scale.anchors) == {1: "Low"}


@pytest.mark.parametrize(
    ("minimum", "maximum", "step"), [(False, 5, 1), (1, True, 1), (0, 4, True)]
)
def test_rejects_bool_numbers(minimum: int, maximum: int, step: int) -> None:
    with pytest.raises(TypeError):
        RatingScale(minimum=minimum, maximum=maximum, step=step)
