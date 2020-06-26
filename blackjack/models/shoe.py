import random

from blackjack.models.deck import Deck


class Shoe:

    all_ = []
    id_counter = 1

    def __init__(self):
        self.card_pile = []  # This will hold the cards that are eligible to be dealt

        # No database, so assign an ID and hold in memory
        self.id = Shoe.id_counter
        Shoe.id_counter += 1
        Shoe.all_.append(self)

    def __str__(self):
        return f"{self.__class__.__name__} {self.id}"

    def __repr__(self):
        return self.__str__()

    def decks(self):
        return [deck for deck in Deck.all_ if deck.shoe == self]

    def cards(self):
        cards = []
        for deck in self.decks():
            for card in deck.cards():
                cards.append(card)
        return cards

    def shuffled_cards(self):
        cards = self.cards()
        random.shuffle(cards)
        return cards

    def reset_card_pile(self):
        self.card_pile = self.shuffled_cards()

    def deal_card(self):
        dealt_card = self.card_pile.pop()
        if not self.card_pile:
            self.reset_card_pile()
        return dealt_card

    def deal_n_cards(self, num_cards):
        return [self.deal_card() for _ in range(num_cards)]
