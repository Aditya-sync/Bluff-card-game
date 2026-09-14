from backend.game.card import Card, Rank, Suit
from backend.game.player import Player


def test_player_starts_with_empty_hand():
    player = Player("p1", "Aditya")

    assert player.player_id == "p1"
    assert player.name == "Aditya"
    assert player.hand == []
    assert player.card_count() == 0


def test_player_can_add_card():
    player = Player("p1", "Aditya")
    card = Card(Rank.KING, Suit.HEARTS)

    player.add_card(card)

    assert player.card_count() == 1
    assert player.hand[0] == card


def test_player_can_remove_card():
    player = Player("p1", "Aditya")
    card = Card(Rank.KING, Suit.HEARTS)

    player.add_card(card)
    player.remove_card(card)

    assert player.card_count() == 0
    assert player.hand == []