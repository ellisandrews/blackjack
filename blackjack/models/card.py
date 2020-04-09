class Card:

    all_ = []

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
        
        Card.all_.append(self)

    def __str__(self):
        # TODO: Use emojis for the suit!
        return f"{self.name} of {self.suit}"

    def __repr__(self):
        return self.__str__()

    def is_ace(self):
        return self.name == 'Ace'
    
    def is_facecard(self):
        return self.value == 10
