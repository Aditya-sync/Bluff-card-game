from random import shuffle

from .card import Card, Rank, Suit


class Deck:
    def __init__(self, deck_count: int = 1):
        if deck_count < 1:
            raise ValueError("deck_count must be at least 1")

        self.cards = []

        for _ in range(deck_count):
            for suit in Suit:
                for rank in Rank:
                    self.cards.append(Card(rank, suit))

    def shuffle(self):
        shuffle(self.cards)

    def __len__(self):
        return len(self.cards)