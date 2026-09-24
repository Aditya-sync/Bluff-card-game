import random

from .deck import Deck
from .player import Player
from .play import Play
from .card import Rank
from .challenge import ChallengeResult
from .config import GameConfig


class Game:
    def __init__(
        self,
        players: list[Player],
        config: GameConfig | None = None,
    ):
        
        if len(players) < 2:
            raise ValueError("A game needs at least 2 players")

        # If no config is supplied, automatically create one
        # using the actual number of players.
        if config is None:
            self.config = GameConfig(player_count=len(players))
        else:
            self.config = config

        self.config.validate()

        # Config and actual player list must agree.
        if self.config.player_count != len(players):
            raise ValueError(
                "Config player count must match the number of players"
            )

        self.players = players

        # Create the required number of decks.
        self.deck = Deck(self.config.deck_count)

        # Cards played into the middle.
        self.center_pile = []

        # Index of the player whose turn it currently is.
        self.current_player_index = None

        # Rank that players must declare for the current sequence.
        self.current_rank = None

        # Most recent actual play.
        self.last_actual_play = None

        # Players who have permanently finished.
        self.finished_players = []

        # A player who has emptied their hand but is not
        # officially finished until another actual play happens
        # or their play is checked and found truthful.
        self.pending_finisher = None

    # ---------------------------------------------------------
    # GAME SETUP
    # ---------------------------------------------------------

    def setup(self):
        """Shuffle, deal cards, and select the starting player."""

        self.deck.shuffle()

        cards_per_player = len(self.deck) // len(self.players)

        # Clear existing hands.
        for player in self.players:
            player.hand = []
            player.finished = False

        # Deal equally to all players.
        for _ in range(cards_per_player):
            for player in self.players:
                player.add_card(self.deck.cards.pop())

        # Any remaining cards become the center pile.
        self.center_pile = self.deck.cards.copy()
        self.deck.cards.clear()

        # Randomly select the first player.
        # The player holding a King starts the game.
        for index, player in enumerate(self.players):
            if any(card.rank == Rank.KING for card in player.hand):
                self.current_player_index = index
                break
        else:
            raise ValueError("No player has a King")
        # Reset game state.
        self.current_rank = None
        self.last_actual_play = None
        self.finished_players = []
        self.pending_finisher = None

    # ---------------------------------------------------------
    # CURRENT PLAYER
    # ---------------------------------------------------------

    @property
    def current_player(self):
        """Return the player whose turn it currently is."""

        return self.players[self.current_player_index]

    # ---------------------------------------------------------
    # PLAY CARDS
    # ---------------------------------------------------------

    def play(
        self,
        player_id: str,
        cards: list,
        declared_rank: Rank,
    ):
        """Play one or more cards and declare their rank."""

        player = self._get_player(player_id)

        # It must be this player's turn.
        if player != self.current_player:
            raise ValueError("It is not this player's turn")

        # The declared rank must follow the current sequence.
        if (
            self.current_rank is not None
            and declared_rank != self.current_rank
        ):
            raise ValueError("Must follow the current declared rank")

        # A play must contain at least one card.
        if not cards:
            raise ValueError("A play must contain at least one card")

        # Make sure the player actually owns every card.
        for card in cards:
            if card not in player.hand:
                raise ValueError(
                    "Player does not have one or more of these cards"
                )

        # Remove cards from the player's hand.
        for card in cards:
            player.remove_card(card)

        # Put the cards into the center pile.
        self.center_pile.extend(cards)

        # Record the actual play.
        play = Play(
            player_id=player_id,
            cards=cards,
            declared_rank=declared_rank,
        )

        # If another player was waiting to finish,
        # their previous empty-hand state is now safe.
        if self.pending_finisher is not None:
            self._finish_pending_player()

        # If this player has emptied their hand,
        # they become a pending finisher.
        if player.card_count() == 0:
            self.pending_finisher = player

        # Update current sequence state.
        self.last_actual_play = play
        self.current_rank = declared_rank

        # Move to the next active player.
        self._advance_turn()

        return play

    # ---------------------------------------------------------
    # SKIP TURN
    # ---------------------------------------------------------

    def skip(self, player_id: str):
        """Skip the current player's turn."""

        player = self._get_player(player_id)

        if player != self.current_player:
            raise ValueError("It is not this player's turn")

        self._advance_turn()

    # ---------------------------------------------------------
    # CHALLENGE / CHECK
    # ---------------------------------------------------------

    def check(self, player_id: str):
        """Challenge the previous player's declared play."""

        challenger = self._get_player(player_id)

        # Only the current player can challenge.
        if challenger != self.current_player:
            raise ValueError("It is not this player's turn")

        # There must be a previous play to challenge.
        if self.last_actual_play is None:
            raise ValueError("There is no play to challenge")

        previous_play = self.last_actual_play

        # Determine whether the previous play was truthful.
        is_truthful = all(
            card.rank == previous_play.declared_rank
            for card in previous_play.cards
        )

        # -----------------------------------------------------
        # TRUTHFUL PLAY
        # -----------------------------------------------------

        if is_truthful:
            result = ChallengeResult.TRUTHFUL_PLAY

            # Challenger takes the pile.
            pile_receiver = challenger

            # The player who made the truthful play starts next.
            next_starter = self._get_player(previous_play.player_id)

        # -----------------------------------------------------
        # BLUFF CAUGHT
        # -----------------------------------------------------

        else:
            result = ChallengeResult.BLUFF_CAUGHT

            # Player who bluffed takes the pile.
            pile_receiver = self._get_player(previous_play.player_id)

            # Challenger starts next.
            next_starter = challenger

        # Give the entire center pile to the appropriate player.
        pile_receiver.hand.extend(self.center_pile)

        # Clear the pile.
        self.center_pile.clear()

        # Reset sequence state.
        self.current_rank = None
        self.last_actual_play = None

        # Set next player directly.
        self.current_player_index = self.players.index(next_starter)

        # -----------------------------------------------------
        # HANDLE FINISHING PLAYER
        # -----------------------------------------------------

        if result == ChallengeResult.TRUTHFUL_PLAY:
            # The player really had no cards,
            # so they officially finish.
            self._finish_pending_player()

        else:
            # Bluff was caught, so the player who emptied
            # their hand gets the pile back and is no longer
            # considered a pending finisher.
            self.pending_finisher = None

        return result

    # ---------------------------------------------------------
    # FINISH PLAYER
    # ---------------------------------------------------------

    def _finish_pending_player(self):
        """Move the pending finisher into the finished list."""

        if self.pending_finisher is None:
            return

        player = self.pending_finisher

        player.finished = True

        self.finished_players.append(player)

        self.pending_finisher = None
        
# ---------------------------------------------------------
# GAME STATUS
# ---------------------------------------------------------

    @property
    def is_over(self) -> bool:
        """Return True when enough players have officially finished."""
        return len(self.finished_players) >= self.config.finish_target

    # ---------------------------------------------------------
    # FIND PLAYER
    # ---------------------------------------------------------

    def _get_player(self, player_id: str):
        """Find a player by ID."""

        for player in self.players:
            if player.player_id == player_id:
                return player

        raise ValueError("Player not found")

    # ---------------------------------------------------------
    # ADVANCE TURN
    # ---------------------------------------------------------

    def _advance_turn(self):
        """Move to the next player who has not finished."""

        start_index = self.current_player_index

        while True:
            self.current_player_index = (
                self.current_player_index + 1
            ) % len(self.players)

            current_player = self.current_player

            # Skip players who have already finished.
            if not current_player.finished:
                return

            # If we've looped all the way around,
            # there are no active players remaining.
            if self.current_player_index == start_index:
                raise ValueError("No active players remaining")