from blackjack.models.card import Card


class Deck:

    def __init__(self):
        self.cards = self._build_deck()

    @staticmethod
    def _build_deck():
        cards = []
        for suit in Card.SUITS:
            for name, value in Card.RANKS:
                cards.append(Card(suit, name, value))
        return cards
