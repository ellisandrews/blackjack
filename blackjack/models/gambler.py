from blackjack.exc import InsufficientBankrollError, OverdraftError
from blackjack.display_utils import money_format


class Gambler:

    def __init__(self, name, bankroll=0, auto_wager=0, hands=None):
        self.name = name
        self.bankroll = bankroll
        self.auto_wager = auto_wager
        self.hands = hands or []

    def __str__(self):
        return f"Player: {self.name} | Bankroll: {money_format(self.bankroll)}"

    def discard_hands(self):
        """Reset hands list."""
        self.hands = []

    def is_finished(self):
        """Check if the gambler is finished playhing."""
        # Player is finished if they've set their wager to $0.00, or they're out of money
        return self.auto_wager == 0 or self.bankroll == 0

    def first_hand(self):
        """Helper method for action that happens on the initial hand dealt to the gambler."""
        return self.hands[0]

    def _add_bankroll(self, amount):
        """Add an amount to the bankroll."""
        self.bankroll += amount

    def _subtract_bankroll(self, amount):
        """Subtract an amount from the bankroll."""
        if amount <= self.bankroll:
            self.bankroll -= amount
        else:
            raise OverdraftError('Bankroll cannot go negative')

    def payout(self, amount):
        """Public facing method for adding bankroll."""
        self._add_bankroll(amount)

    def can_place_wager(self, amount):
        """Check whether the gambler has sufficient bankroll to place a wager."""
        return amount <= self.bankroll

    def can_place_auto_wager(self):
        """Check whether the gambler has sufficient bankroll to place the auto-wager."""
        return self.can_place_wager(self.auto_wager) 

    def _insurance_wager_amount(self):
        """Calculate insurance wager amount in a single place for ease of maintenance."""
        return self.first_hand().wager / 2

    def can_place_insurance_wager(self):
        """Check whether the gambler has sufficient bankroll to place an insurance wager."""
        return self.can_place_wager(self._insurance_wager_amount())

    def place_hand_wager(self, wager, hand):
        """Place a wager on a hand. Additive so can be used to double down."""
        if self.can_place_wager(wager):
            self._subtract_bankroll(wager)  
            hand.wager += wager
        else:
            raise InsufficientBankrollError('Insufficient bankroll to place hand wager')    

    def place_auto_wager(self):
        """Place the auto-wager on the dealt hand."""
        self.place_hand_wager(self.auto_wager, self.first_hand())

    def place_insurance_wager(self):
        """Place an insurance wager on the first hand."""
        insurance_amount = self._insurance_wager_amount()
        if self.can_place_insurance_wager():
            self._subtract_bankroll(insurance_amount)
            self.first_hand().insurance = insurance_amount
        else:
            raise InsufficientBankrollError('Insufficient bankroll to place insurance wager')

    def zero_auto_wager(self):
        """Set the auto_wager to 0."""
        self.auto_wager = 0

    def set_new_auto_wager(self, auto_wager):
        """Set a new auto-wager."""
        # Make sure bankroll is large enough
        if self.can_place_wager(auto_wager):
            self.auto_wager = auto_wager
        else:
            raise InsufficientBankrollError('Insufficient bankroll to set auto-wager')

    def settle_up(self, dealer_hand):
        """Compare Gambler hands to a given Dealer hand."""
        for hand in self.hands:
            hand.settle_up(dealer_hand)
