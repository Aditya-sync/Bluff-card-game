from .card import Card, Rank


class Play:
    def __init__(
        self,
        player_id: str,
        cards: list[Card],
        declared_rank: Rank,
    ):
        if not cards:
            raise ValueError("A play must contain at least one card")

        self.player_id = player_id
        self.cards = cards
        self.declared_rank = declared_rank

    @property
    def card_count(self):
        return len(self.cards)