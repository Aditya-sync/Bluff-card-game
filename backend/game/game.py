import random

from .deck import Deck
from .player import Player
from .play import Play
from .card import Rank


class Game:
    def __init__(self, players: list[Player], deck_count: int = 1):
        if len(players) < 2:
            raise ValueError("A game needs at least 2 players")

        self.players = players
        self.deck = Deck(deck_count)
        self.center_pile = []
        self.current_player_index = None
        self.current_rank = None
        self.last_actual_play = None

    def setup(self):
        self.deck.shuffle()

        cards_per_player = len(self.deck) // len(self.players)

        for player in self.players:
            player.hand = []

        for _ in range(cards_per_player):
            for player in self.players:
                player.add_card(self.deck.cards.pop())

        self.center_pile = self.deck.cards.copy()
        self.deck.cards.clear()

        self.current_player_index = random.randrange(len(self.players))

    @property
    def current_player(self):
        return self.players[self.current_player_index]

    def play(
        self,
        player_id: str,
        cards: list,
        declared_rank: Rank,
    ):
        player = self._get_player(player_id)

        if player != self.current_player:
            raise ValueError("It is not this player's turn")

        if self.current_rank is not None and declared_rank != self.current_rank:
            raise ValueError("Must follow the current declared rank")

        for card in cards:
            if card not in player.hand:
                raise ValueError("Player does not have one or more of these cards")

        for card in cards:
            player.remove_card(card)
            self.center_pile.append(card)

        play = Play(
            player_id=player_id,
            cards=cards,
            declared_rank=declared_rank,
        )

        self.last_actual_play = play
        self.current_rank = declared_rank

        self._advance_turn()

        return play

    def _get_player(self, player_id: str):
        for player in self.players:
            if player.player_id == player_id:
                return player

        raise ValueError("Player not found")

    def _advance_turn(self):
        self.current_player_index = (
            self.current_player_index + 1
        ) % len(self.players)