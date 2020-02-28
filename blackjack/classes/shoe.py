import random

from blackjack.classes.deck import Deck


# NOTE: Shoe is 1-to-1 with Table
class Shoe:

    all_ = []
    counter = 1

    def __init__(self):
        self.number = Shoe.counter
        self.card_pile = []  # This will hold the cards that are eligible to be dealt

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

    def reset_card_pile(self):
        self.card_pile = self.shuffled_cards()

    def deal_card(self):
        dealt_card = self.card_pile.pop()
        if not self.card_pile:
            print('Shoe exhausted. Reshuffling cards...')
            self.reset_card_pile()
        return dealt_card

    def deal_two_cards(self):
        return self.deal_card(), self.deal_card()
