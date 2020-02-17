SUITS = ['Spades', 'Hearts', 'Clubs', 'Diamonds']

CARDS = {
    'Ace': [1, 11],
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


class Card:
    def __init__(self, name, suit):
        self.name = name
        self.suit = suit
        self.value = CARDS[name]

    def __str__(self):
        return f"{self.name} of {self.suit}"

    def __repr__(self):
        return self.__str__()


class Hand:
    def __init__(self, cards, wager=0):
        self.cards = cards  # List of Card objects
        self.wager = wager  # Amount wagered on the hand

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
        # - However, only one ace per hand can logically be 11 in order to *possibly* stay under a total of 22.
        # - There will always be 2 *possible non-busting* hand totals if playing with a single deck.
        #   This is because only one ace can be high, and with the max possible 4 aces: 11 + 1 + 1 + 1 = 14, 
        #   which is *possibly non-busting* (depending on other cards in hand)
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
            if card.name == 'Ace':
                num_aces += 1
        return num_aces

    def is_blackjack(self):
        """Check whether the hand is blackjack."""
        _, high_total = self.possible_totals()
        if high_total == 21 and len(self.cards) == 2:
            return True
        else:
            return False

    def is_splittable(self):
        """Check whether the hand is splittable"""
        if len(self.cards) == 2 and self.cards[0].name == self.cards[1].name:
            return True
        else:
            return False
