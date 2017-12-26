import random

from copy import deepcopy
# TODO: Add Docstrings all around once things are more finalized

# TODO: Is this __all__ necessary?
# __all__ = [
#     'SUITS',
#     'CARDS',
#     'Player',
#     'Card',
#     'Deck'
# ]

# ===================
#  GLOBAL VARIABLES
# ===================

SUITS = ['Spades', 'Hearts', 'Clubs', 'Diamonds']

CARDS = {
    # how to handle Aces?? - Currently all the logic is in Player.sum_hand() method
    'Ace': None,
    '2': 2,
    '3': 3,
    '4': 4,
    '5': 5,
    '6': 6,
    '7': 7,
    '8': 8,
    '9': 9,
    '10': 10,
    'Jack': 10,
    'Queen': 10,
    'King': 10
}


# ===============
#  GAME CLASSES
# ===============

class Player(object):
    """
    Class representing a blackjack player
    """

    def __init__(self, name, bankroll=100, hand=[]):
        self.name = name
        self.bankroll = bankroll
        self.hand = hand
        self.hand_totals = None
        self.turn_over = False
        self.bet = 0

    def __str__(self):
        return 'Player: {name}, Bankroll: ${bankroll}'.format(name=self.name, bankroll=self.bankroll)

    def __del__(self):
        return "Deleted '{}' Player object".format(self.name)

    def add_bankroll(self, amount):
        self.bankroll += amount

    def subtract_bankroll(self, amount):
        self.bankroll -= amount
        # The player cannot have a negative bankroll
        if self.bankroll < 0:
            self.bankroll = 0

    def reset_hand(self):
        self.hand = []

    def print_hand(self):
        print self.hand

    def sum_hand(self):
        # NOTE: The result of this function is just updating the self.hand_totals attribute (dict)

        # self.hand is a list of Card objects in the Player's hand
        card_names = [card.name for card in self.hand]
        # Get the number of Aces in the hand as they can be high or low in value
        num_aces = card_names.count('Ace')

        # total_dict will have 2 values {'low': <low_val>, 'high': <high_val>}
        totals = {'low': None, 'high': None}

        # If no Aces in the hand, just sum it based on the values in the CARDS dictionary
        if num_aces == 0:
            totals['low'] = sum(card.value for card in self.hand)

        # Otherwise, Handle the variable value of Aces
        # Note: This logic is based on the fact that only 1 Ace can be 'high' in a hand,
        #       as 2 'high' Aces equals 22 which is a bust.
        else:
            # aceless_total is sum of the value of all non-Ace cards in the Player's hand
            aceless_total = sum(card.value for card in self.hand if card.name != 'Ace')
            # low_total is the hand total if all Aces are counted as 'low' (i.e. value == 1)
            totals['low'] = aceless_total + num_aces
            # high_total is the hand total if one Ace is counted as 'high' (i.e. value == 11)
            totals['high'] = aceless_total + 11 + (num_aces - 1)

        self.hand_totals = totals

    def print_total(self):
        # Updates self.turn_over attribute (bool) depending on the sum of the hand

        self.sum_hand()

        low_total = self.hand_totals['low']
        high_total = self.hand_totals['high']

        # First, check for a blackjack
        if len(self.hand) == 2 and high_total == 21:
            print 'Hand total: 21 - BLACKJACK!'
            self.turn_over = True

        # Second, check whether either total is 21
        elif low_total == 21 or high_total == 21:
            print 'Hand total: 21'
            self.turn_over = True

        # Third, check whether the player busted or not and handle accordingly

        # If the lower total is over 21, print that the player busted
        elif low_total > 21:
            print 'Hand total: {low} - Busted!'.format(low=low_total)
            self.turn_over = True

        # If the higher total is under 21, print both low and high totals as viable options
        elif high_total and high_total < 21:
            print 'Hand total: {low} or {high}'.format(low=low_total, high=high_total)

        # If the higher total is over 21, only print the low total as a viable option
        else:
            print 'Hand total: {low}'.format(low=low_total)


class Card(object):
    """
    Class representing a card
    """

    def __init__(self, name, suit):
        assert name in CARDS
        self.name = name

        assert suit in SUITS
        self.suit = suit

        self.value = CARDS[self.name]

    def __str__(self):
        return '{name} of {suit}'.format(name=self.name, suit=self.suit)

    # Allows you to print the custom card name from __str__ above on a list, etc.
    def __repr__(self):
        return self.__str__()


class Deck(object):
    """
    Class representing the deck of cards
    """

    def __init__(self):
        # self.cached_deck should not be mutated
        # Just stores the full deck so doesn't need to be created every time
        self.cached_deck = self.create_deck()

        # Initialize the self.deck as the full deck off the bat (deepcopy of object)
        self.deck = deepcopy(self.cached_deck)

        # Should this all be moved into __init__? Never would call this method otherwise...

    def create_deck(self):
        deck = []
        for suit in SUITS:
            for card in CARDS:
                deck.append(Card(card, suit))
        return deck

    def reset_deck(self):
        self.deck = deepcopy(self.cached_deck)
        print 'Deck reset.'

    def select_card(self):
        return random.choice(self.deck)

    def remove_card(self, card):
        self.deck.remove(card)
