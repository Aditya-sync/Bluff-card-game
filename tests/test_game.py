import pytest

from backend.game.game import Game
from backend.game.player import Player
from backend.game.card import Card, Rank, Suit
from backend.game.challenge import ChallengeResult

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
        
def test_player_can_skip():
    players = create_players(3)
    game = Game(players)

    game.setup()

    current_player = game.current_player
    current_index = game.current_player_index

    game.skip(current_player.player_id)

    expected_index = (current_index + 1) % len(players)

    assert game.current_player_index == expected_index
    assert game.current_player == players[expected_index]
    
def test_skip_does_not_change_last_actual_play():
    players = create_players(3)
    game = Game(players)

    game.setup()

    first_player = game.current_player

    cards = first_player.hand[:2]

    play = game.play(
        player_id=first_player.player_id,
        cards=cards,
        declared_rank=Rank.KING,
    )

    second_player = game.current_player

    game.skip(second_player.player_id)

    assert game.last_actual_play == play
    assert game.current_rank == Rank.KING
    
def test_player_cannot_skip_when_not_their_turn():
    players = create_players(3)
    game = Game(players)

    game.setup()

    current_player = game.current_player

    other_player = players[
        (game.current_player_index + 1) % len(players)
    ]

    with pytest.raises(ValueError):
        game.skip(other_player.player_id)
        
        
        
def test_check_catches_bluff():
    players = create_players(2)
    game = Game(players)

    game.setup()

    first_player = game.current_player
    second_player = players[
        (game.current_player_index + 1) % len(players)
    ]

    # Make sure first player has a King and a non-King.
    king = next(
        card for card in first_player.hand
        if card.rank == Rank.KING
    )

    non_king = next(
        card for card in first_player.hand
        if card.rank != Rank.KING
    )

    cards = [king, non_king]

    game.play(
        player_id=first_player.player_id,
        cards=cards,
        declared_rank=Rank.KING,
    )

    pile_size = len(game.center_pile)

    result = game.check(second_player.player_id)

    assert result == ChallengeResult.BLUFF_CAUGHT

    assert first_player.card_count() == (
        len(first_player.hand)
    )

    assert len(game.center_pile) == 0
    assert game.current_player == second_player
    assert game.current_rank is None
    assert game.last_actual_play is None
    
def test_check_catches_bluff():
    players = create_players(2)
    game = Game(players)

    game.setup()

    first_player = game.current_player
    second_player = players[
        (game.current_player_index + 1) % len(players)
    ]

    king = next(
        card for card in first_player.hand
        if card.rank == Rank.KING
    )

    non_king = next(
        card for card in first_player.hand
        if card.rank != Rank.KING
    )

    cards = [king, non_king]

    game.play(
        player_id=first_player.player_id,
        cards=cards,
        declared_rank=Rank.KING,
    )

    pile_size = len(game.center_pile)
    first_player_hand_before_check = first_player.card_count()

    result = game.check(second_player.player_id)

    assert result == ChallengeResult.BLUFF_CAUGHT
    assert len(game.center_pile) == 0
    assert first_player.card_count() == (
        first_player_hand_before_check + pile_size
    )
    assert game.current_player == second_player
    assert game.current_rank is None
    assert game.last_actual_play is None
    
def test_check_on_truthful_play():
    players = create_players(2)
    game = Game(players)

    game.setup()

    first_player = game.current_player
    second_player = players[
        (game.current_player_index + 1) % len(players)
    ]

    kings = [
        card for card in first_player.hand
        if card.rank == Rank.KING
    ][:2]

    game.play(
        player_id=first_player.player_id,
        cards=kings,
        declared_rank=Rank.KING,
    )

    pile_size = len(game.center_pile)
    second_player_hand_before_check = second_player.card_count()

    result = game.check(second_player.player_id)

    assert result == ChallengeResult.TRUTHFUL_PLAY
    assert len(game.center_pile) == 0

    assert second_player.card_count() == (
        second_player_hand_before_check + pile_size
    )

    assert game.current_player == first_player
    assert game.current_rank is None
    assert game.last_actual_play is None
    
def test_check_after_skips_targets_last_actual_play():
    players = create_players(4)
    game = Game(players)

    game.setup()

    first_player = game.current_player

    king = next(
        card for card in first_player.hand
        if card.rank == Rank.KING
    )

    non_king = next(
        card for card in first_player.hand
        if card.rank != Rank.KING
    )

    game.play(
        player_id=first_player.player_id,
        cards=[king, non_king],
        declared_rank=Rank.KING,
    )

    second_player = game.current_player
    game.skip(second_player.player_id)

    third_player = game.current_player
    game.skip(third_player.player_id)

    fourth_player = game.current_player

    result = game.check(fourth_player.player_id)

    assert result == ChallengeResult.BLUFF_CAUGHT
    assert game.current_player == fourth_player
    assert game.last_actual_play is None
    assert game.current_rank is None