import random

from blackjack.models.deck import Deck


class Shoe:

    def __init__(self, num_decks):
        # Create the decks of cards.
        self.decks = [Deck() for _ in range(num_decks)]

        # List to hold the cards to be dealt, in the order in which they'll be dealt.
        self.card_pile = []

        # Initialize with a shuffled card pile so the shoe is ready to be played.
        self.reset_card_pile()

    def cards(self):
        """Get all cards belonging to the shoe (through decks)."""
        cards = []
        for deck in self.decks:
            for card in deck.cards:
                cards.append(card)
        return cards

    def shuffled_cards(self):
        """Shuffle the shoe's cards."""
        cards = self.cards()
        random.shuffle(cards)
        return cards

    def reset_card_pile(self):
        """Reset the shoe's card pile."""
        self.card_pile = self.shuffled_cards()

    def deal_card(self):
        """Deal a card from the shoe (reshuffle if pile exhausted)."""
        if not self.card_pile:
            self.reset_card_pile()
        return self.card_pile.pop()

    def deal_n_cards(self, num_cards):
        """Deal a set number of cards from the shoe."""
        return [self.deal_card() for _ in range(num_cards)]
