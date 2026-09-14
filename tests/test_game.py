import pytest

from backend.game.game import Game
from backend.game.player import Player
from backend.game.card import Card, Rank, Suit

def create_players(count):
    return [
        Player(f"p{i}", f"Player {i}")
        for i in range(count)
    ]

def test_player_can_play_cards():
    players = create_players(2)
    game = Game(players)

    game.setup()

    current_player = game.current_player

    cards = current_player.hand[:2]

    play = game.play(
        player_id=current_player.player_id,
        cards=cards,
        declared_rank=Rank.KING,
    )

    assert play.player_id == current_player.player_id
    assert play.cards == cards
    assert play.declared_rank == Rank.KING

    assert all(card not in current_player.hand for card in cards)
    assert all(card in game.center_pile for card in cards)

    assert game.current_rank == Rank.KING
    assert game.last_actual_play == play


def test_player_cannot_play_when_not_their_turn():
    players = create_players(2)
    game = Game(players)

    game.setup()

    current_player = game.current_player
    other_player = players[
        1 if game.current_player_index == 0 else 0
    ]

    cards = other_player.hand[:1]

    with pytest.raises(ValueError):
        game.play(
            player_id=other_player.player_id,
            cards=cards,
            declared_rank=Rank.KING,
        )


def test_player_cannot_play_cards_they_do_not_have():
    players = create_players(2)
    game = Game(players)

    game.setup()

    current_player = game.current_player
    other_player = players[
        1 if game.current_player_index == 0 else 0
    ]

    card_from_other_player = other_player.hand[0]

    with pytest.raises(ValueError):
        game.play(
            player_id=current_player.player_id,
            cards=[card_from_other_player],
            declared_rank=Rank.KING,
        )


def test_subsequent_player_must_follow_declared_rank():
    players = create_players(2)
    game = Game(players)

    game.setup()

    first_player = game.current_player

    first_cards = first_player.hand[:1]

    game.play(
        player_id=first_player.player_id,
        cards=first_cards,
        declared_rank=Rank.KING,
    )

    second_player = game.current_player

    second_cards = second_player.hand[:1]

    with pytest.raises(ValueError):
        game.play(
            player_id=second_player.player_id,
            cards=second_cards,
            declared_rank=Rank.QUEEN,
        )