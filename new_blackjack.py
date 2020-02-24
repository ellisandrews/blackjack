from blackjack.classes import CARDS, SUITS
from blackjack.classes.card import Card
from blackjack.classes.deck import Deck
from blackjack.classes.player import Player


# Create 2 players
player = Player('Ellis', 100)
dealer = Player('Dealer', 0)

# Create 2 decks (mostly just for proof of concept)
decks = [Deck(), Deck()]

def populate_deck(deck):
    """Populate a `Deck` object with 52 cards"""
    for suit in SUITS:
        for name, value in CARDS:
            Card(deck, suit, name, value)

for deck in decks:
    populate_deck(deck)

shoe = []
for deck in decks:
    shoe += deck.shuffle_cards()

print(shoe[:3])
print(len(shoe))


