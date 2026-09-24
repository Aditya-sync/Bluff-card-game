class GameConfig:
    def __init__(
        self,
        player_count: int = 2,
        deck_count: int = 1,
        finish_target: int = 1,
    ):
        self.player_count = player_count
        self.deck_count = deck_count
        self.finish_target = finish_target

    def validate(self):
        if self.player_count < 2 or self.player_count > 6:
            raise ValueError("Player count must be between 2 and 6")

        if self.deck_count < 1:
            raise ValueError("Deck count must be at least 1")

        if self.finish_target < 1:
            raise ValueError("Finish target must be at least 1")

        if self.finish_target >= self.player_count:
            raise ValueError("Finish target must be less than player count")