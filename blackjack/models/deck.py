from blackjack.models.card import Card


class Deck:

    def __init__(self):
        self.cards = self._build_deck()

    @staticmethod
    def _build_deck():
        """Create a full deck of all 52 cards."""
        cards = []
        for suit in Card.SUITS:
            for name, value in Card.RANKS:
                cards.append(Card(suit, name, value))
        return cards
