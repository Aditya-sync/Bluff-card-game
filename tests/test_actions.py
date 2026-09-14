from backend.game.actions import ActionType


def test_action_types():
    assert ActionType.PLAY.value == "play"
    assert ActionType.SKIP.value == "skip"
    assert ActionType.CHECK.value == "check"