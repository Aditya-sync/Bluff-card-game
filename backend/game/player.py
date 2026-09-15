class Player:
    def __init__(self, player_id: str, name: str):
        self.player_id = player_id
        self.name = name
        self.hand = []
        self.finished = False

    def add_card(self, card):
        self.hand.append(card)

    def remove_card(self, card):
        self.hand.remove(card)

    def card_count(self):
        return len(self.hand)
    @property
    def has_finished(self):
        return self.finished
