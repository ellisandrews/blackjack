from blackjack.exc import InsufficientBankrollError, OverdraftError
from blackjack.models.hand import Hand
from blackjack.models.table import Table
from blackjack.user_input import float_response, get_user_input, max_retries_exit, yes_no_response


class Player:

    all_ = []

    # NOTE: If ever refactoring to allow many Players at a Table, this class should belong to a Table
    #       (i.e. many to one relationship Player to Table) and thus define a table attribute here.
    def __init__(self, name):
        self.name = name
        Player.all_.append(self)

    def __str__(self):
        return f"Player: {self.name}"

    def hands(self):
        return [hand for hand in Hand.all_ if hand.player == self]

    def discard_hands(self):
        # Delete the hand from the single source of truth
        for hand in self.hands():
            Hand.all_.remove(hand)


class Gambler(Player):
    
    def __init__(self, name, bankroll=0, auto_wager=0):
        super().__init__(name)
        self.bankroll = bankroll
        self.auto_wager = auto_wager

        # Player is finished if they have set their auto_wager to $0 or if they are out of money
        self.is_finished = lambda: self.auto_wager == 0 or self.bankroll == 0

    def __str__(self):
        return super().__str__() + f" | Bankroll: ${self.bankroll}"

    def table(self):
        """Get the Table to which the Gambler belongs."""
        return next((table for table in Table.all_ if table.gambler == self), None)

    def first_hand(self):
        # Helper method for action that happens on the initial hand dealt to the gambler
        return self.hands()[0]

    def _add_bankroll(self, amount):
        """Add an amount to the bankroll."""
        self.bankroll += amount

    def _subtract_bankroll(self, amount):
        """Subtract an amount from the bankroll."""
        if amount <= self.bankroll:
            self.bankroll -= amount
        else:
            raise OverdraftError('Bankroll cannot go negative')

    def payout(self, amount, message):
        self._add_bankroll(amount)
        print(message)

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
            print(f"${wager} wager placed on hand.")
        else:
            raise InsufficientBankrollError('Insufficient bankroll to place hand wager')    

    def place_auto_wager(self):
        """Place the auto-wager on the dealt hand."""
        try:
            self.place_hand_wager(self.auto_wager, self.first_hand())
        except InsufficientBankrollError:
            raise

    def place_insurance_wager(self):
        """Place an insurance wager on the first hand."""
        insurance_amount = self._insurance_wager_amount()
        if self.can_place_insurance_wager():
            self._subtract_bankroll(insurance_amount)
            self.first_hand().insurance = insurance_amount
            print(f"${insurance_amount} insurance wager placed.")
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

    def set_new_auto_wager_from_input(self, retries=3):
        """Set a new auto-wager amount from user input (with input vetting and retry logic)."""
        # Set their auto_wager to $0
        self.zero_auto_wager()

        # Ask them for a new auto wager and set it, with some validation
        attempts = 0
        success = False        
        while not success and attempts < retries:
            # This validates that they've entered a float
            new_auto_wager = get_user_input(f"Please enter an auto-wager amount (Bankroll: ${self.bankroll}; enter $0 to cash out): $", float_response)
            
            # This validates that they've entered a wager <= their bankroll
            try:
                self.set_new_auto_wager(new_auto_wager)
                success = True
            except InsufficientBankrollError as e:
                print(f"{e}. Please try again.")
                attempts += 1

        # If they've unsuccessfully tried to enter input the maximum number of times, exit the program
        if attempts == retries and not success:
            max_retries_exit()

    @staticmethod
    def wants_even_money():
        return get_user_input("Take even money? (y/n) => ", yes_no_response)

    @staticmethod
    def wants_insurance():
        return get_user_input("Insurance? (y/n) => ", yes_no_response)

    def check_wager(self):
        # Check if the gambler still has sufficient bankroll to place the auto-wager
        if self.can_place_auto_wager():

            # Ask if the gambler wants to cash out or change their auto-wager
            response = get_user_input(
                f"{self.name}, change your auto-wager or cash out? (Bankroll: ${self.bankroll}; Auto-Wager: ${self.auto_wager}) (y/n) => ", 
                yes_no_response
            )
            
            # If they want to make a change, make it
            if response == 'yes':
                self.set_new_auto_wager_from_input()

        # If they don't have sufficient bankroll to place auto-wager, force them to set a new one.
        else:
            print(f"Insufficient bankroll to place current auto-wager (Bankroll: ${self.bankroll}; Auto-Wager: ${self.auto_wager})")
            self.set_new_auto_wager_from_input()

    def play_turn(self, shoe):
        """Play the gambler's turn"""
        # Use a while loop due to the fact that self.hands can grow while iterating (via splitting)
        while any(hand.status == 'Pending' for hand in self.hands()):
            hand = next(hand for hand in self.hands() if hand.status == 'Pending')  # Grab the next unplayed hand
            hand.play(shoe)  # Play the hand
            self.table().print()

    def settle_up(self, dealer_hand):
        print('\nSetting up...')
        for hand in self.hands():
            hand.settle_up(dealer_hand)


class Dealer(Player):

    def __init__(self, name='Dealer'):
        super().__init__(name)

    def table(self):
        return next((table for table in Table.all_ if table.dealer == self), None)

    def hand(self):
        # The dealer will only ever have a single hand
        return self.hands()[0]

    def up_card(self):
        # Shortcut to the dealer's hand's up_card
        return self.hand().up_card()

    def is_showing_ace(self):
        return self.up_card().is_ace()

    def is_showing_face_card(self):
        return self.up_card().is_facecard()

    def play_turn(self, shoe):
        self.hand().play(shoe)
        self.table().print(hide_dealer=False)
