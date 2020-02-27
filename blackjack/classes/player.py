from blackjack.classes.hand import Hand
from blackjack.exc import InsufficientBankrollError
from blackjack.utils import float_response, get_user_input, max_retries_exit


# TODO: This could maybe be an abstract base class?
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
    
    def __init__(self, name, bankroll=0, table=None, wager=0):
        super().__init__(name, table)
        self.bankroll = bankroll
        self.wager = wager

    def __str__(self):
        return super().__str__(self) + f" | Bankroll: ${self.bankroll}"

    def add_bankroll(self, amount):
        self.bankroll += amount

    def subtract_bankroll(self, amount):
        if self.bankroll < amount:
            raise InsufficientBankrollError
        self.bankroll -= amount

    def move_wager_to_bankroll(self):
        self.add_bankroll(self.wager)
        self.wager = 0

    def set_new_wager(self, wager):
        # Make sure bankroll is large enough to place the wager
        try:
            self.subtract_bankroll(wager)
            self.wager = wager
        except InsufficientBankrollError:
            raise

    def set_new_wager_from_input(self, retries=3):
    
        # Move their current wager to their bankroll
        self.move_wager_to_bankroll()

        # Ask them for a new wager and set it, with some validation
        attempts = 0
        success = False        
        while not success and attempts < retries:
            # This validates that they've entered a float
            new_wager = get_user_input(f"Enter a new wager (Bankroll: ${self.bankroll}; enter $0 to cash out): $", float_response)
            
            # This validates that they've entered a wager <= their bankroll
            try:
                self.set_new_wager(new_wager)
                success = True
            except InsufficientBankrollError:
                print('Insufficient bankroll to place that wager. Please try again.')
                attempts += 1

        # If they've unsuccessfully tried to enter input the maximum number of times, exit the program
        if attempts == retries and not success:
            max_retries_exit()


class Dealer(Player):
    
    def __init__(self, name='Dealer', table=None):
        super().__init__(name, table)
