from collections import OrderedDict
from functools import partial

from blackjack.exc import InsufficientBankrollError
from blackjack.models.hand import Hand
from blackjack.models.table import Table
from blackjack.utils import choice_response, float_response, get_user_input, max_retries_exit, yes_no_response


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
        return next((table for table in Table.all_ if table.gambler == self), None)

    def first_hand(self):
        # Helper method for action that happens on the initial hand dealt to the gambler
        return self.hands()[0]

    def payout(self, amount, message):
        self._add_bankroll(amount)
        print(message)

    def _add_bankroll(self, amount):
        self.bankroll += amount

    def _subtract_bankroll(self, amount):
        if self.bankroll < amount:
            raise InsufficientBankrollError
        self.bankroll -= amount

    def can_place_auto_wager(self):
        """Check whether the gambler has sufficient bankroll to place the auto-wager."""
        return self.auto_wager <= self.bankroll

    def can_place_insurance_wager(self):
        """Check whether a gambler has sufficient bankroll to place an insurance wager."""
        # Insurance only applies to the dealt hand. Insurance is half the hand's wager.
        return self.first_hand().wager / 2 <= self.bankroll

    def place_auto_wager(self):
        hand = self.first_hand()  # Auto-wager only comes into play for the dealt hand
        if self.can_place_auto_wager():      
            self._subtract_bankroll(self.auto_wager)  
            hand.wager = self.auto_wager
            print(f"${self.auto_wager} wager placed on hand.")
        else:
            raise InsufficientBankrollError('Insufficient bankroll to place auto-wager.')

    def place_insurance_wager(self):
        hand = self.first_hand()  # Insurance only comes into play for the dealt hand
        insurance_amount = hand.wager / 2  # Insurance is 1/2 the amount wagered on the hand
        if self.can_place_insurance_wager():
            self._subtract_bankroll(insurance_amount)  
            hand.insurance = insurance_amount
            print(f"${insurance_amount} insurance wager placed.")
        else:
            raise InsufficientBankrollError('Insufficient bankroll to place insurance wager.')

    def zero_auto_wager(self):
        self.auto_wager = 0

    def set_new_auto_wager(self, auto_wager):
        # Make sure bankroll is large enough
        if auto_wager > self.bankroll:
            raise InsufficientBankrollError('Insufficient bankroll to set auto-wager.')
        else:
            self.auto_wager = auto_wager

    def set_new_auto_wager_from_input(self, retries=3):
    
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
            except InsufficientBankrollError:
                print('Insufficient bankroll to place that wager. Please try again.')
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

    def play_hand(self, hand):
        """Play a hand."""

        while not (hand.is_21() or hand.is_busted()):

            # Default turn options
            options = OrderedDict([('h', 'hit'), ('s', 'stand'), ('d', 'double')])

            # Add the option to split if applicable
            if hand.is_splittable():
                options['x'] = 'split'

            display_options = [f"{option} ({abbreviation})" for abbreviation, option in options.items()]

            response = get_user_input(
                f"What would you like to do?\n[ {' , '.join(display_options)} ] => ",
                partial(choice_response, choices=options.keys())
            )

            action = options[response]

            if action == 'hit':
                # Deal another card and re-run loop
                print('Hitting...')
                hand.hit()
            elif action == 'stand':
                print('Stood.')
                break
            elif action == 'double':
                print('Doubling...')
                hand.hit()
                break
            elif action == 'split':
                # Check if the user has enough bankroll to split
                # Split cards into their own hands
                # Add another wager equal to the first
                # If the card is an Ace, they only get 1 more card on each hand
                # If not, run loop for each hand
                # TODO!
                print('Splitting...')
                pass
            else:
                raise Exception('Unhandled response.')

    def play_turn(self):
        """Play the gambler's turn"""
        for hand in self.hands():
            self.play_hand(hand)


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
