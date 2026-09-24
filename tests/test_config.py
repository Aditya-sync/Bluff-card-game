import pytest
from backend.game.config import GameConfig
def test_default_config():
    config = GameConfig()

    assert config.player_count == 2
    assert config.deck_count == 1
    assert config.finish_target == 1


def test_custom_config():
    config = GameConfig(
        player_count=6,
        deck_count=3,
        finish_target=2,
    )

    assert config.player_count == 6
    assert config.deck_count == 3
    assert config.finish_target == 2


def test_invalid_player_count():
    config = GameConfig(player_count=1)

    with pytest.raises(ValueError):
        config.validate()


def test_player_count_cannot_exceed_six():
    config = GameConfig(player_count=7)

    with pytest.raises(ValueError):
        config.validate()


def test_invalid_deck_count():
    config = GameConfig(deck_count=0)

    with pytest.raises(ValueError):
        config.validate()


def test_invalid_finish_target():
    config = GameConfig(finish_target=0)

    with pytest.raises(ValueError):
        config.validate()


def test_finish_target_cannot_reach_player_count():
    config = GameConfig(
        player_count=4,
        finish_target=4,
    )

    with pytest.raises(ValueError):
        config.validate()