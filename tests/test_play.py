import pytest

from backend.game.card import Card, Rank, Suit
from backend.game.play import Play


def test_play_stores_cards_and_declaration():
    cards = [
        Card(Rank.KING, Suit.HEARTS),
        Card(Rank.KING, Suit.SPADES),
        Card(Rank.QUEEN, Suit.CLUBS),
    ]

    play = Play(
        player_id="p1",
        cards=cards,
        declared_rank=Rank.KING,
    )

    assert play.player_id == "p1"
    assert play.cards == cards
    assert play.declared_rank == Rank.KING
    assert play.card_count == 3


def test_play_cannot_be_empty():
    with pytest.raises(ValueError):
        Play(
            player_id="p1",
            cards=[],
            declared_rank=Rank.KING,
        )
        
