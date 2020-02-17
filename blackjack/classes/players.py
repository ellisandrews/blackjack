
class Player:

    def __init__(self, name, bankroll):
        self.name = name
        self.bankroll = bankroll
        self.hands = []

    def __str__(self):
        return f"Player: {self.name} | Bankroll: ${self.bankroll}"

    def resest_hands(self):
        self.hands = []

    def add_bankroll(self, amount):
        self.bankroll += amount

    def subtract_bankroll(self, amount):
        self.bankroll -= amount
        if self.bankroll < 0:  # The player cannot have a negative bankroll
            self.bankroll = 0
