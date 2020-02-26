from blackjack.classes.hand import Hand


# TODO: This could probably be an abstract base class
class Player:

    all_ = []

    def __init__(self, name, table=None):
        self.name = name
        self.table = table

        Player.all_.append(self)

    def __str__(self):
        return f"Player: {self.name}"
    
    def hands(self):
        return [hand for hand in Hand.all_ if hand.player == self]

    def print_hands(self):
        for i, hand in enumerate(self.hands()):
            # Get possible hand total(s) to display
            low_total, high_total = hand.possible_totals()

            # There will always be a low total. If there is a high total, display that too.
            if high_total:
                print(f"Hand {i+1} (${hand.wager}): {hand} -- ({low_total} or {high_total})")
            else:
                print(f"Hand {i+1} (${hand.wager}): {hand} -- ({low_total})")


class Gambler(Player):
    
    def __init__(self, name, bankroll=0, table=None, standing_wager=0):
        super().__init__(name, table)
        self.bankroll = bankroll
        self.standing_wager = standing_wager

    def __str__(self):
        return super().__str__(self) + f" | Bankroll: ${self.bankroll}"

    def add_bankroll(self, amount):
        self.bankroll += amount

    def subtract_bankroll(self, amount):
        self.bankroll -= amount
        if self.bankroll < 0:  # The player cannot have a negative bankroll
            self.bankroll = 0


class Dealer(Player):
    
    def __init__(self, name='Dealer', table=None):
        super().__init__(name, table)
