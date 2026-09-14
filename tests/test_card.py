from backend.game.card import Card, Rank, Suit


def test_card():
    card = Card(Rank.KING, Suit.HEARTS)

    assert card.rank == Rank.KING
    assert card.suit == Suit.HEARTS