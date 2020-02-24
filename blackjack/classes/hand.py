from blackjack.classes.card import Card


class Hand:

    all_ = []

    def __init__(self, player, wager=0):
        self.player = player
        self.wager = wager

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
        for card in self.cards():
            if card.name == 'Ace':
                num_aces += 1
        return num_aces

    def is_blackjack(self):
        """Check whether the hand is blackjack."""
        _, high_total = self.possible_totals()
        if high_total == 21 and len(self.cards()) == 2:
            return True
        else:
            return False

    def is_splittable(self):
        """Check whether the hand is splittable"""
        cards = self.cards()
        if len(cards) == 2 and cards[0].name == cards[1].name:
            return True
        else:
            return False
