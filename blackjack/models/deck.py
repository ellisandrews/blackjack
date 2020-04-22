import random

from blackjack.models.card import Card


class Deck:

    all_ = []
    counter = 1

    def __init__(self, shoe=None):
        self.shoe = shoe
        self.number = Deck.counter

        Deck.counter += 1
        Deck.all_.append(self)

    def __str__(self):
        return f"{self.__class__.__name__} {self.number}"

    def __repr__(self):
        return self.__str__()

    def cards(self):
        return [card for card in Card.all_ if card.deck == self]

    def populate(self):
        for suit in Card.SUITS:
            for name, value in Card.RANKS:
                Card(suit, name, value, deck=self)

    def shuffle(self):
        cards = self.cards()
        random.shuffle(cards)
        return cards
