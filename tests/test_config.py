import pytest

from backend.game.config import GameConfig


def test_finish_target_can_be_set():
    config = GameConfig(
        player_count=4,
        deck_count=1,
        finish_target=2,
    )

    config.validate()

    assert config.finish_target == 2


def test_finish_target_cannot_equal_player_count():
    config = GameConfig(
        player_count=4,
        deck_count=1,
        finish_target=4,
    )

    with pytest.raises(ValueError):
        config.validate()


def test_finish_target_cannot_exceed_player_count():
    config = GameConfig(
        player_count=4,
        deck_count=1,
        finish_target=5,
    )

    with pytest.raises(ValueError):
        config.validate()


def test_finish_target_must_be_at_least_one():
    config = GameConfig(
        player_count=4,
        deck_count=1,
        finish_target=0,
    )

    with pytest.raises(ValueError):
        config.validate()