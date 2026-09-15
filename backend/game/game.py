import random

from .deck import Deck
from .player import Player
from .play import Play
from .card import Rank
from .challenge import ChallengeResult

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
        self.finished_players = []
        self.pending_finisher = None

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
    
        self.center_pile.extend(cards)
    
        play = Play(
            player_id=player_id,
            cards=cards,
            declared_rank=declared_rank,
        )
    
        # If the previous player was waiting to finish,
        # their play is now safe because a new actual play happened.
        if self.pending_finisher is not None:
            self._finish_pending_player()
    
        # The current player may now become a pending finisher.
        if player.card_count() == 0:
            self.pending_finisher = player
    
        self.last_actual_play = play
        self.current_rank = declared_rank
    
        self._advance_turn()
    
        return play    

    def skip(self, player_id: str):
        player = self._get_player(player_id)

        if player != self.current_player:
            raise ValueError("It is not this player's turn")

        self._advance_turn()
        
    def check(self, player_id: str):
        challenger = self._get_player(player_id)

        if challenger != self.current_player:
            raise ValueError("It is not this player's turn")

        if self.last_actual_play is None:
            raise ValueError("There is no play to challenge")

        previous_play = self.last_actual_play

        is_truthful = all(
            card.rank == previous_play.declared_rank
            for card in previous_play.cards
        )

        if is_truthful:
            result = ChallengeResult.TRUTHFUL_PLAY
            pile_receiver = challenger
            next_starter = self._get_player(previous_play.player_id)

        else:
            result = ChallengeResult.BLUFF_CAUGHT
            pile_receiver = self._get_player(previous_play.player_id)
            next_starter = challenger

        pile_receiver.hand.extend(self.center_pile)
        self.center_pile.clear()

        self.current_rank = None
        self.last_actual_play = None

        self.current_player_index = self.players.index(next_starter)
        if result == ChallengeResult.TRUTHFUL_PLAY:
            self._finish_pending_player()
        else:
            self.pending_finisher = None

        return result
    def _finish_pending_player(self):
        if self.pending_finisher is None:
            return
        player = self.pending_finisher
        player.finished = True
        self.finished_players.append(player)
        self.pending_finisher = None
    
    def _get_player(self, player_id: str):
        for player in self.players:
            if player.player_id == player_id:
                return player

        raise ValueError("Player not found")
    
    def _advance_turn(self):
        start_index = self.current_player_index
    
        while True:
            self.current_player_index = (
                self.current_player_index + 1
            ) % len(self.players)
    
            if not self.current_player.finished:
                return
    
            if self.current_player_index == start_index:
                raise ValueError("No active players remaining")    