class Card:

    all_ = []
    id_counter = 1

    SUITS = ['Spades', 'Hearts', 'Clubs', 'Diamonds']
    RANKS = [
        ('Ace', [1, 11]),
        ('2', 2),
        ('3', 3),
        ('4', 4),
        ('5', 5),
        ('6', 6),
        ('7', 7),
        ('8', 8),
        ('9', 9),
        ('10', 10),
        ('Jack', 10),
        ('Queen', 10),
        ('King', 10)
    ]

    def __init__(self, suit, name, value, deck=None):
        self.suit = suit
        self.name = name
        self.value = value
        self.deck = deck

        # No database, so assign an ID and hold in memory
        self.id = Card.id_counter
        Card.id_counter += 1
        Card.all_.append(self)

    def __str__(self):
        return f"{self.name} of {self.suit}"

    def __repr__(self):
        return self.__str__()

    def is_ace(self):
        return self.name == 'Ace'

    def is_facecard(self):
        return self.value == 10

    def csv_format(self):
        """String representation of the card for Strategy CSVs."""
        return 'A' if self.is_ace() else str(self.value)
