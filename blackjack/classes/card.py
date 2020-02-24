class Card:

    all_ = []

    def __init__(self, deck, suit, name, value, hand=None):
        self.deck = deck
        self.suit = suit
        self.name = name
        self.value = value
        self.hand = hand
        
        Card.all_.append(self)

    def __str__(self):
        return f"{self.name} of {self.suit}"

    def __repr__(self):
        return self.__str__()

    @classmethod
    def clear_all(cls):
        cls.all_ = []
