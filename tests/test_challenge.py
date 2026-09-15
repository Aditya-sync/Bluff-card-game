from backend.game.challenge import ChallengeResult


def test_challenge_results():
    assert ChallengeResult.BLUFF_CAUGHT.value == "bluff_caught"
    assert ChallengeResult.TRUTHFUL_PLAY.value == "truthful_play"