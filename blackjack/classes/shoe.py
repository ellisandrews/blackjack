import random

from blackjack.classes.deck import Deck


class Shoe:

    all_ = []
    counter = 1

    def __init__(self, table=None):
        self.table = table
        self.number = Shoe.counter
        
        Shoe.counter += 1
        Shoe.all_.append(self)

    def __str__(self):
        return f"{self.__class__.__name__} {self.number}"

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
