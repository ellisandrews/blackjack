import random

from blackjack.classes.cards import Card, CARDS, Hand, SUITS


def create_new_shuffled_deck():
    """Create a new shuffled deck of all 52 cards."""
    deck = []
    for suit in SUITS:
        for card_name in CARDS.keys():
            deck.append(Card(card_name, suit))
    random.shuffle(deck)
    return deck


def deal(deck, *args):
    """Deal 2 cards from the deck to each player passed in."""
    for player in args:
        player.hands.append(Hand(deck.pop(), deck.pop()))
