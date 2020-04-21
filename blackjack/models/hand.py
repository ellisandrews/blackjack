from collections import OrderedDict
from functools import partial
from time import sleep

from blackjack.models.card import Card
from blackjack.user_input import choice_response, get_user_input


class Hand:

    all_ = []

    def __init__(self, player, cards=None, status='Pending'):
        self.player = player
        self.cards = cards or []  # Card order matters, so we'll store cards in a list
        self.status = status      # Hands are initialized as 'Pending' by default (will be updated as they are played)

        Hand.all_.append(self)

    def __str__(self):
        return ' | '.join(str(card) for card in self.cards)

    def __repr__(self):
        return self.__str__()

    def possible_totals(self):
        """Sum the cards in the hand. Return 2 totals, due to the dual value of Aces."""
        # Get the number of aces in the hand
        num_aces = self.get_num_aces_in_hand()
        
        # Get the total for all non-ace cards first, as this is constant
        non_ace_total = sum(card.value for card in self.cards if card.name != 'Ace')

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
        for card in self.cards:
            if card.is_ace():
                num_aces += 1
        return num_aces

    def format_possible_totals(self):
        # Get possible hand total(s) to display
        low_total, high_total = self.possible_totals()

        # Return string of total that makes sense
        if high_total == 21:
            return f"{high_total}"
        elif high_total:
            return f"{low_total} or {high_total}"
        else:
            return f"{low_total}"

    def final_total(self):
        """Get the singular hand total for determining the outcome (high total if it exists, otherwise low total)."""
        low_total, high_total = self.possible_totals()
        return high_total or low_total

    def get_total_to_display(self):
        # If hand is still active, allow for multiple totals to be displayed. Otherwise, display the single final total.
        if self.status in ('Pending', 'Playing'):
            return self.format_possible_totals()
        else:
            return self.final_total()

    def is_21(self):
        """Check if the hand totals to 21."""
        return self.final_total() == 21

    def is_blackjack(self):
        """Check whether the hand is blackjack."""
        return self.is_21() and len(self.cards) == 2

    def is_busted(self):
        """Check whether the hand is busted."""
        return self.final_total() > 21

    def is_soft(self):
        """Check whether a hand is 'soft', meaning has an Ace counted as 11."""
        _, high_total = self.possible_totals()
        return bool(high_total)

    def hit(self):
        """Add a card to the hand from the player's table's shoe."""
        card = self.player.table().shoe.deal_card()
        self.cards.append(card)


class GamblerHand(Hand):

    def __init__(self, player, cards=None, status='Pending', wager=0, insurance=0, hand_number=1):
        super().__init__(player, cards, status)
        self.wager = wager
        self.insurance = insurance
        self.hand_number = hand_number
        
        if self.is_blackjack():
            self.status = 'Blackjack'

    def print(self):
        # TODO: Print outcome of hand and/or insurance? (e.g. win/loss/push)?
        lines = [
            f"\nHand {self.hand_number}:",
            f"Cards: {self}",
            f"Total: {self.get_total_to_display()}",
            f"Wager: ${self.wager}",
            f"Status: {self.status}"
        ]

        print('\n\t'.join(lines))

    def is_splittable(self):
        """
        Check whether the hand is splittable. Requirements:
        
        1) Hand is made up of two cards.
        2) The name of the two cards matches (e.g. King-King, Five-Five, etc.)
        3) The Player has sufficient bankroll to split.
        """
        return len(self.cards) == 2 and self.cards[0].name == self.cards[1].name and self.player.bankroll >= self.wager

    def is_doubleable(self):
        """
        Check whether the hand is doubleable. Requirements:
        
        1) Hand is made up of two cards.
        2) The Player has sufficient bankroll to double.
        """
        return len(self.cards) == 2 and self.player.bankroll >= self.wager

    def get_user_action(self):
        """List action options for the user on the hand, and get their choice."""
        # Default turn options
        options = OrderedDict([('h', 'Hit'), ('s', 'Stand')])

        # Add the option to doulbe if applicable
        if self.is_doubleable():
            options['d'] = 'Double'

        # Add the option to split if applicable
        if self.is_splittable():
            options['x'] = 'Split'

        # Formatted options to display to the user
        display_options = [f"{option} ({abbreviation})" for abbreviation, option in options.items()]

        # Ask what the user would like to do, given their options
        response = get_user_input(
            f"\n[ Hand {self.hand_number} ] What would you like to do? [ {' , '.join(display_options)} ] => ",
            partial(choice_response, choices=options.keys())
        )

        # Return the user's selection ('hit', 'stand', etc.)
        return options[response]

    def play(self):
        """Play the hand."""

        self.status = 'Playing'

        while self.status == 'Playing':

            # If the hand resulted from splitting, hit it automatically.
            if len(self.cards) == 1:
                print('Adding second card to split hand...')
                self.hit()

                # Split Aces only get 1 more card.
                if self.cards[0].is_ace():
                    if self.is_blackjack():
                        self.status = 'Blackjack'
                    else:
                        self.status = 'Stood'
                    break

            # Print a fresh screen for ease of user decision making
            self.player.table().print()

            # Get the user's action from input
            action = self.get_user_action()

            if action == 'Hit':
                print('Hitting...')    # Deal another card and keep playing the hand.
                self.hit()

            elif action == 'Stand':
                print('Stood.')        # Do nothing, hand is played.
                self.status = 'Stood'

            elif action == 'Double':
                print('Doubling...')   # Deal another card and print. Hand is played.
                self.hit()
                self.status = 'Doubled'

            elif action == 'Split':
                print('Splitting...')  # Put second card into a new hand, keep playing this hand 
                self.split()
                continue

            else:
                raise Exception('Unhandled response.')

            # If the hand is 21 or busted, the hand is done being played.
            if self.is_21():
                print('21!')
                self.status = 'Stood'
            elif self.is_busted():
                print('Busted!')
                self.status = 'Busted'

    def split(self):
        """Split the current hand."""
        split_card = self.cards.pop(1)  # Pop the second card off the hand to make a new hand
        new_hand = GamblerHand(self.player, cards=[split_card], hand_number=len(self.player.hands())+1)
        self.player.place_hand_wager(self.wager, new_hand)  # Place the same wager on the new hand

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


class DealerHand(Hand):

    def up_card(self):
        return self.cards[0]

    def print(self, hide=False):
        if hide:
            up_card = self.up_card()
            cards = f"Upcard: {up_card}"
            total = f"Total: {up_card.value if up_card.name != 'Ace' else '1 or 11'}"
        else:
            cards = f"Cards: {self}"
            total = f"Total: {self.get_total_to_display()}"

        lines = [
            'Hand:',
            cards,
            total,
            f"Status: {self.status}"
        ]

        print('\n\t'.join(lines))

    def play(self):
        # At this point, we've already checked whether the dealer has blackjack (and they do not, otherwise we wouldn't be here)
        # Start playing the hand
        self.status = 'Playing'

        while self.status == 'Playing':

            # Print a fresh screen so the user can see the dealer's buried card
            self.player.table().print(hide_dealer=False)
            sleep(2)

            # Get the hand total
            total = self.final_total()

            if total < 17:
                print('Hitting...')    # Deal another card and keep playing the hand.
                self.hit()

            elif total == 17 and self.is_soft():
                    print('Hitting...')  # Dealer must hit a soft 17
                    self.hit() 
            
            else:
                print('Stood.')
                self.status = 'Stood'

            # If the hand is busted, it's over. Otherwise, sleep so the user can see the card progression
            if self.is_busted():
                print('Busted!')
                self.status = 'Busted'
