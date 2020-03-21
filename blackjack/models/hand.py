from collections import OrderedDict
from functools import partial

from blackjack.models.card import Card
from blackjack.user_input import choice_response, get_user_input


class Hand:

    all_ = []

    def __init__(self, player):
        self.player = player
        Hand.all_.append(self)

    def __str__(self):
        return ' | '.join(str(card) for card in self.cards())

    def __repr__(self):
        return self.__str__()

    def cards(self):
        return [card for card in Card.all_ if card.hand == self]

    def possible_totals(self):
        """Sum the cards in the hand. Return 2 totals, due to the dual value of Aces."""
        # Get the number of aces in the hand
        num_aces = self.get_num_aces_in_hand()
        
        # Get the total for all non-ace cards first, as this is constant
        non_ace_total = sum(card.value for card in self.cards() if card.name != 'Ace')

        # If there are no aces in the hand, there is only one possible total. Return it.
        if num_aces == 0:
            return non_ace_total, None

        # If there are aces in the hand, extra logic is needed:
        # - Each ace can have 2 possible values (1 or 11). 
        # - However, only one ace *per hand* can logically be 11 in order to *possibly* stay under a total of 22.
        # - Thus, there will always be 2 *possibly non-busting* hand totals if there is at least one ace in the hand.
        high_total = non_ace_total + 11 + num_aces - 1
        low_total = non_ace_total + num_aces

        # If the high_total is already busting, only return the low_total (to be vetted for busting later)
        if high_total > 21:
            return low_total, None
        # Otherwise, return both totals
        else:
            return low_total, high_total

    def get_num_aces_in_hand(self):
        """Get the number of Aces in the hand."""
        num_aces = 0
        for card in self.cards():
            if card.is_ace():
                num_aces += 1
        return num_aces

    def format_total(self):
        # Get possible hand total(s) to display
        low_total, high_total = self.possible_totals()

        # Return string of total that makes sense
        if high_total == 21:
            return f"{high_total}"
        elif high_total:
            return f"{low_total} or {high_total}"
        else:
            return f"{low_total}"

    def is_21(self):
        """Check if the hand totals to 21."""
        low_total, high_total = self.possible_totals()
        return low_total == 21 or high_total == 21

    def is_blackjack(self):
        """Check whether the hand is blackjack."""
        _, high_total = self.possible_totals()
        return high_total == 21 and len(self.cards()) == 2

    def is_splittable(self):
        """Check whether the hand is splittable."""
        cards = self.cards()
        return len(cards) == 2 and cards[0].name == cards[1].name

    def is_busted(self):
        """Check whether the hand is busted."""
        low_total, _ = self.possible_totals()
        return low_total > 21

    def hit(self):
        """Add a card to the hand from the player's table's shoe."""
        card = self.player.table().shoe.deal_card()
        card.hand = self


class DealerHand(Hand):

    def up_card(self):
        return self.cards()[0]

    def print(self, hide=False):
        print(f"Hand:")
        if hide:
            up_card = self.up_card()
            print(f"\tUpcard: {up_card}")
            print(f"\tTotal: {up_card.value if up_card.name != 'Ace' else '1 or 11'}")
        else:
            print(f"\tCards: {self}")
            print(f"\tTotal: {self.format_total()}")


class GamblerHand(Hand):

    def __init__(self, player, wager=0, insurance=0):
        super().__init__(player)
        self.wager = wager
        self.insurance = insurance

    def print(self, hand_number=1):
        # TODO: Print outcome of hand and/or insurance? (e.g. win/loss/push)?
        print(f"\nHand {hand_number}:")
        print(f"\tCards: {self}")
        print(f"\tTotal: {self.format_total()}")
        print(f"\tWager: ${self.wager}")
        if self.insurance != 0:
            print(f"\tInsurance: ${self.insurance}")

    def play(self):
        """Play the hand."""
        while not (self.is_21() or self.is_busted()):

            # Default turn options
            options = OrderedDict([('h', 'hit'), ('s', 'stand'), ('d', 'double')])

            # Add the option to split if applicable
            if self.is_splittable():
                options['x'] = 'split'

            # Formatted options to display to the user
            display_options = [f"{option} ({abbreviation})" for abbreviation, option in options.items()]

            # Ask what the user would like to do, given their options
            response = get_user_input(
                f"What would you like to do?\n[ {' , '.join(display_options)} ] => ",
                partial(choice_response, choices=options.keys())
            )

            action = options[response]

            if action == 'hit':
                # Deal another card and re-run loop
                print('Hitting...')
                self.hit()
            elif action == 'stand':
                print('Stood.')
                break
            elif action == 'double':
                # TODO: Check if the user has enough bankroll to double
                print('Doubling...')
                self.hit()
                break
            elif action == 'split':
                # TODO: Check if the user has enough bankroll to split
                # Split cards into their own hands
                # Add another wager equal to the first
                # If the card is an Ace, they only get 1 more card on each hand
                # If not, run loop for each hand
                # TODO!
                print('Splitting...')
                pass
            else:
                raise Exception('Unhandled response.')

    def payout(self, kind, odds=None):
        
        # Validate args passed in
        if kind in ('wager', 'insurance'):
            assert odds, 'Must specify odds for wager payouts!'

        if kind == 'wager':
            self._perform_payout('winning_wager', odds)
            self._perform_payout('wager_reclaim')
        
        elif kind == 'insurance':
            self._perform_payout('winning_insurance', odds)
            self._perform_payout('insurance_reclaim')
        
        elif kind == 'push':
            self._perform_payout('wager_reclaim')
        
        else:
            raise ValueError(f"Invalid payout kind: '{kind}'")

    def _perform_payout(self, kind, odds=None):

        # Validate args passed in
        if kind in ('winning_wager', 'winning_insurance'):
            assert odds, 'Must specify odds for wager payouts!'
            antecedent, consequent = map(int, odds.split(':'))
        
        # Really wish python had case statements...
        if kind == 'winning_wager':
            amount = self.wager * antecedent / consequent
            message = f"Adding winning hand payout of ${amount} to bankroll."
        
        elif kind == 'wager_reclaim':
            amount = self.wager
            message = f"Reclaiming hand wager of ${amount}."
        
        elif kind == 'winning_insurance':
            amount = self.insurance * antecedent / consequent
            message = f"Adding winning insurance payout of ${amount} to bankroll."
        
        elif kind == 'insurance_reclaim':
            amount = self.insurance
            message = f"Reclaiming insurance wager of ${amount}."

        else:
            raise ValueError(f"Invalid payout kind: '{kind}'")

        self.player.payout(amount, message)
