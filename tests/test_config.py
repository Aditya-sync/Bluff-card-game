import pytest

from backend.game.config import GameConfig


def test_default_config():
    config = GameConfig()

    assert config.deck_count == 1
    assert config.finish_target == 1


def test_custom_config():
    config = GameConfig(
        deck_count=3,
        finish_target=2,
    )

    assert config.deck_count == 3
    assert config.finish_target == 2


def test_invalid_deck_count():
    with pytest.raises(ValueError):
        GameConfig(deck_count=0)


def test_invalid_finish_target():
    with pytest.raises(ValueError):
        GameConfig(finish_target=0)


def test_finish_target_cannot_exceed_player_count():
    config = GameConfig(
        deck_count=1,
        finish_target=4,
    )

    with pytest.raises(ValueError):
        config.validate(player_count=3)


def test_player_count_must_be_between_2_and_6():
    config = GameConfig()

    with pytest.raises(ValueError):
        config.validate(player_count=1)

    with pytest.raises(ValueError):
        config.validate(player_count=7)