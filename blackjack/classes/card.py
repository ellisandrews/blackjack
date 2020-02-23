from typing import List, Optional, Union

from blackjack.classes.deck import Deck
from blackjack.classes.hand import Hand


class Card:

    all_ = []

    def __init__(self, deck: Deck, name: str, suit: str, value: Union[int, List[int]], hand: Optional[Hand] = None):
        self.deck = deck
        self.name = name
        self.suit = suit
        self.value = value
        self.hand = hand
        
        Card.all_.append(self)

    def __str__(self):
        return f"{self.name} of {self.suit}"

    def __repr__(self):
        return self.__str__()
