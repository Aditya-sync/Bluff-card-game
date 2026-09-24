from dataclasses import dataclass


@dataclass(frozen=True)
class GameConfig:
    deck_count: int = 1
    finish_target: int = 1

    def __post_init__(self):
        if self.deck_count < 1:
            raise ValueError("deck_count must be at least 1")

        if self.finish_target < 1:
            raise ValueError("finish_target must be at least 1")

    def validate(self, player_count: int):
        if player_count < 2 or player_count > 6:
            raise ValueError("player_count must be between 2 and 6")

        if self.finish_target > player_count:
            raise ValueError(
                "finish_target cannot exceed player_count"
            )