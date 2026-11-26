import pytest

from survey_schema import SpecialResponse, SpecialResponseKind, SpecialResponses

DONT_KNOW = SpecialResponse(98, "Don't know", SpecialResponseKind.DONT_KNOW)
REFUSED = SpecialResponse(99, "Refused", SpecialResponseKind.REFUSED)


def test_lookup() -> None:
    responses = SpecialResponses((DONT_KNOW, REFUSED))
    assert responses.codes == {98, 99}
    assert responses[99] is REFUSED
    assert 98 in responses and len(responses) == 2
    assert len(SpecialResponses()) == 0


def test_rejects_duplicates_and_invalid_items() -> None:
    with pytest.raises(ValueError):
        SpecialResponses((DONT_KNOW, DONT_KNOW))
    with pytest.raises(ValueError):
        SpecialResponses(
            (
                DONT_KNOW,
                SpecialResponse(1, "Don't know", SpecialResponseKind.NO_OPINION),
            )
        )
    with pytest.raises(TypeError):
        SpecialResponse(True, "Yes", SpecialResponseKind.DONT_KNOW)
    with pytest.raises(ValueError):
        SpecialResponse(1, " ", SpecialResponseKind.DONT_KNOW)


def test_is_volunteered() -> None:
    assert not DONT_KNOW.is_volunteered
    volunteered = SpecialResponse(
        97, "Refused", SpecialResponseKind.REFUSED, is_volunteered=True
    )
    assert volunteered.is_volunteered and volunteered != REFUSED
