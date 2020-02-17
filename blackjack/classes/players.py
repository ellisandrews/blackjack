
class Player:

    def __init__(self, name, bankroll):
        self.name = name
        self.bankroll = bankroll
        self.hands = []

    def __str__(self):
        return f"Player: {self.name} | Bankroll: ${self.bankroll}"

    def reset_hands(self):
        self.hands = []

    def add_bankroll(self, amount):
        self.bankroll += amount

    def subtract_bankroll(self, amount):
        self.bankroll -= amount
        if self.bankroll < 0:  # The player cannot have a negative bankroll
            self.bankroll = 0

    def print_hands(self):
        for i, hand in enumerate(self.hands):
            # Get possible hand total(s) to display
            low_total, high_total = hand.possible_totals()

            # There will always be a low total. If there is a high total, display that too.
            if high_total:
                print(f"Hand {i+1} (${hand.wager}): {hand} -- ({low_total} or {high_total})")
            else:
                print(f"Hand {i+1} (${hand.wager}): {hand} -- ({low_total})")
