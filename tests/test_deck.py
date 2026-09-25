import pytest

from backend.game.deck import Deck


def test_one_deck_has_52_cards():
    deck = Deck(1)

    assert len(deck) == 52


def test_two_decks_have_104_cards():
    deck = Deck(2)

    assert len(deck) == 104


def test_four_decks_have_208_cards():
    deck = Deck(4)

    assert len(deck) == 208


def test_invalid_deck_count():
    with pytest.raises(ValueError):
        Deck(0)
        