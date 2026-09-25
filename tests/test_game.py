import pytest

from backend.game.game import Game
from backend.game.player import Player
from backend.game.card import Card, Rank, Suit
from backend.game.play import Play
from backend.game.challenge import ChallengeResult
from backend.game.config import GameConfig


def create_players(count):
    return [
        Player(f"p{i}", f"Player {i}")
        for i in range(1, count + 1)
    ]


# ============================================================
# INITIALIZATION
# ============================================================

def test_game_requires_at_least_two_players():
    players = [Player("p1", "Player 1")]

    with pytest.raises(ValueError):
        Game(players)


def test_game_creates_default_config():
    players = create_players(3)

    game = Game(players)

    assert game.config.player_count == 3


def test_game_rejects_config_with_wrong_player_count():
    players = create_players(3)

    config = GameConfig(
        player_count=4,
        deck_count=1,
        finish_target=2,
    )

    with pytest.raises(ValueError):
        Game(players, config)


def test_game_initializes_empty_center_pile():
    players = create_players(3)

    game = Game(players)

    assert game.center_pile == []


def test_game_initializes_no_current_player():
    players = create_players(3)

    game = Game(players)

    assert game.current_player_index is None


def test_game_initializes_empty_finished_players():
    players = create_players(3)

    game = Game(players)

    assert game.finished_players == []


def test_game_initializes_no_pending_finisher():
    players = create_players(3)

    game = Game(players)

    assert game.pending_finisher is None


# ============================================================
# SETUP
# ============================================================

def test_game_setup_deals_cards():
    players = create_players(4)

    game = Game(players)
    game.setup()

    assert all(player.card_count() > 0 for player in players)


def test_game_setup_selects_player_with_king():
    players = create_players(4)

    game = Game(players)
    game.setup()

    current_player = game.current_player

    assert any(
        card.rank == Rank.KING
        for card in current_player.hand
    )


def test_game_setup_resets_player_finished_status():
    players = create_players(4)

    for player in players:
        player.finished = True

    game = Game(players)
    game.setup()

    assert all(player.finished is False for player in players)


def test_game_setup_resets_game_state():
    players = create_players(4)

    game = Game(players)

    game.current_rank = Rank.KING
    game.last_actual_play = "something"
    game.finished_players = [players[0]]
    game.pending_finisher = players[1]

    game.setup()

    assert game.current_rank is None
    assert game.last_actual_play is None
    assert game.finished_players == []
    assert game.pending_finisher is None


# ============================================================
# CURRENT PLAYER
# ============================================================

def test_current_player_returns_correct_player():
    players = create_players(3)

    game = Game(players)

    game.current_player_index = 1

    assert game.current_player == players[1]


# ============================================================
# PLAY
# ============================================================

def test_player_can_play_cards():
    players = create_players(3)

    game = Game(players)

    game.current_player_index = 0

    card = Card(Rank.KING, Suit.HEARTS)
    players[0].add_card(card)

    play = game.play(
        player_id="p1",
        cards=[card],
        declared_rank=Rank.KING,
    )

    assert play.player_id == "p1"
    assert play.cards == [card]
    assert play.declared_rank == Rank.KING


def test_play_removes_cards_from_player_hand():
    players = create_players(3)

    game = Game(players)
    game.current_player_index = 0

    card = Card(Rank.KING, Suit.HEARTS)
    players[0].add_card(card)

    game.play(
        player_id="p1",
        cards=[card],
        declared_rank=Rank.KING,
    )

    assert players[0].hand == []


def test_play_adds_cards_to_center_pile():
    players = create_players(3)

    game = Game(players)
    game.current_player_index = 0

    card = Card(Rank.KING, Suit.HEARTS)
    players[0].add_card(card)

    game.play(
        player_id="p1",
        cards=[card],
        declared_rank=Rank.KING,
    )

    assert card in game.center_pile


def test_play_updates_current_rank():
    players = create_players(3)

    game = Game(players)
    game.current_player_index = 0

    card = Card(Rank.KING, Suit.HEARTS)
    players[0].add_card(card)

    game.play(
        player_id="p1",
        cards=[card],
        declared_rank=Rank.KING,
    )

    assert game.current_rank == Rank.KING


def test_play_requires_at_least_one_card():
    players = create_players(3)

    game = Game(players)
    game.current_player_index = 0

    with pytest.raises(ValueError):
        game.play(
            player_id="p1",
            cards=[],
            declared_rank=Rank.KING,
        )


def test_player_cannot_play_out_of_turn():
    players = create_players(3)

    game = Game(players)
    game.current_player_index = 0

    card = Card(Rank.KING, Suit.HEARTS)
    players[1].add_card(card)

    with pytest.raises(ValueError):
        game.play(
            player_id="p2",
            cards=[card],
            declared_rank=Rank.KING,
        )


def test_player_cannot_play_card_they_do_not_have():
    players = create_players(3)

    game = Game(players)
    game.current_player_index = 0

    card = Card(Rank.KING, Suit.HEARTS)

    with pytest.raises(ValueError):
        game.play(
            player_id="p1",
            cards=[card],
            declared_rank=Rank.KING,
        )


def test_declared_rank_must_follow_current_rank():
    players = create_players(3)

    game = Game(players)
    game.current_player_index = 0
    game.current_rank = Rank.KING

    card = Card(Rank.QUEEN, Suit.HEARTS)
    players[0].add_card(card)

    with pytest.raises(ValueError):
        game.play(
            player_id="p1",
            cards=[card],
            declared_rank=Rank.QUEEN,
        )


# ============================================================
# SKIP
# ============================================================

def test_current_player_can_skip_turn():
    players = create_players(3)

    game = Game(players)
    game.current_player_index = 0

    game.skip("p1")

    assert game.current_player == players[1]


def test_player_cannot_skip_out_of_turn():
    players = create_players(3)

    game = Game(players)
    game.current_player_index = 0

    with pytest.raises(ValueError):
        game.skip("p2")


# ============================================================
# CHALLENGE
# ============================================================

def test_check_requires_previous_play():
    players = create_players(3)

    game = Game(players)
    game.current_player_index = 0

    with pytest.raises(ValueError):
        game.check("p1")


def test_check_can_catch_bluff():
    players = create_players(3)

    game = Game(players)

    real_card = Card(Rank.QUEEN, Suit.HEARTS)

    players[0].add_card(real_card)

    game.current_player_index = 0

    game.play(
        player_id="p1",
        cards=[real_card],
        declared_rank=Rank.KING,
    )

    result = game.check("p2")

    assert result == ChallengeResult.BLUFF_CAUGHT


def test_check_detects_truthful_play():
    players = create_players(3)

    game = Game(players)

    card = Card(Rank.KING, Suit.HEARTS)

    players[0].add_card(card)

    game.current_player_index = 0

    game.play(
        player_id="p1",
        cards=[card],
        declared_rank=Rank.KING,
    )

    result = game.check("p2")

    assert result == ChallengeResult.TRUTHFUL_PLAY


def test_bluff_caught_gives_pile_to_bluffer():
    players = create_players(3)

    game = Game(players)

    card = Card(Rank.QUEEN, Suit.HEARTS)

    players[0].add_card(card)

    game.current_player_index = 0

    game.play(
        player_id="p1",
        cards=[card],
        declared_rank=Rank.KING,
    )

    game.check("p2")

    assert card in players[0].hand
    assert game.center_pile == []


def test_truthful_challenge_gives_pile_to_challenger():
    players = create_players(3)

    game = Game(players)

    card = Card(Rank.KING, Suit.HEARTS)

    players[0].add_card(card)

    game.current_player_index = 0

    game.play(
        player_id="p1",
        cards=[card],
        declared_rank=Rank.KING,
    )

    game.check("p2")

    assert card in players[1].hand
    assert game.center_pile == []


def test_check_resets_current_rank():
    players = create_players(3)

    game = Game(players)

    card = Card(Rank.KING, Suit.HEARTS)

    players[0].add_card(card)
    game.current_player_index = 0

    game.play(
        player_id="p1",
        cards=[card],
        declared_rank=Rank.KING,
    )

    game.check("p2")

    assert game.current_rank is None


def test_check_resets_last_actual_play():
    players = create_players(3)

    game = Game(players)

    card = Card(Rank.KING, Suit.HEARTS)

    players[0].add_card(card)
    game.current_player_index = 0

    game.play(
        player_id="p1",
        cards=[card],
        declared_rank=Rank.KING,
    )

    game.check("p2")

    assert game.last_actual_play is None


# ============================================================
# FINISHING PLAYERS
# ============================================================

def test_player_becomes_pending_finisher_when_hand_is_empty():
    players = create_players(3)

    game = Game(players)

    card = Card(Rank.KING, Suit.HEARTS)
    players[0].add_card(card)

    game.current_player_index = 0

    game.play(
        player_id="p1",
        cards=[card],
        declared_rank=Rank.KING,
    )

    assert game.pending_finisher == players[0]


def test_truthful_empty_hand_player_finishes():
    players = create_players(3)

    game = Game(players)

    card = Card(Rank.KING, Suit.HEARTS)
    players[0].add_card(card)

    game.current_player_index = 0

    game.play(
        player_id="p1",
        cards=[card],
        declared_rank=Rank.KING,
    )

    game.check("p2")

    assert players[0].finished is True
    assert players[0] in game.finished_players


def test_bluffed_empty_hand_player_does_not_finish():
    players = create_players(3)

    game = Game(players)

    card = Card(Rank.QUEEN, Suit.HEARTS)
    players[0].add_card(card)

    game.current_player_index = 0

    game.play(
        player_id="p1",
        cards=[card],
        declared_rank=Rank.KING,
    )

    game.check("p2")

    assert players[0].finished is False
    assert players[0] not in game.finished_players
    assert game.pending_finisher is None


def test_is_over_is_false_before_finish_target():
    players = create_players(3)

    config = GameConfig(
        player_count=3,
        deck_count=1,
        finish_target=2,
    )

    game = Game(players, config)

    assert game.is_over is False


def test_is_over_becomes_true_when_finish_target_reached():
    players = create_players(3)

    config = GameConfig(
        player_count=3,
        deck_count=1,
        finish_target=2,
    )

    game = Game(players, config)

    game.finished_players = [players[0], players[1]]

    assert game.is_over is True


# ============================================================
# PLAYER LOOKUP
# ============================================================

def test_get_player_finds_player_by_id():
    players = create_players(3)

    game = Game(players)

    player = game._get_player("p2")

    assert player == players[1]


def test_get_player_raises_for_unknown_id():
    players = create_players(3)

    game = Game(players)

    with pytest.raises(ValueError):
        game._get_player("unknown")


# ============================================================
# TURN ADVANCEMENT
# ============================================================

def test_advance_turn_moves_to_next_player():
    players = create_players(3)

    game = Game(players)
    game.current_player_index = 0

    game._advance_turn()

    assert game.current_player == players[1]


def test_advance_turn_wraps_around():
    players = create_players(3)

    game = Game(players)
    game.current_player_index = 2

    game._advance_turn()

    assert game.current_player == players[0]


def test_advance_turn_skips_finished_players():
    players = create_players(3)

    game = Game(players)
    game.current_player_index = 0

    players[1].finished = True

    game._advance_turn()

    assert game.current_player == players[2]