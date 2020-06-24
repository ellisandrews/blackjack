from abc import ABC, abstractstaticmethod


class BaseInputController(ABC):
    """
    This is an Abstract Base Class (ABC) that specifies which methods are expected to be implemented in order to
    work when used by the master GameController class.
    """

    @abstractstaticmethod
    def check_wager():
        """Get a yes/no response for whether the gambler wants to change their auto-wager."""

    @abstractstaticmethod
    def get_new_auto_wager():
        """Get a new auto-wager amount (float)."""

    @abstractstaticmethod
    def get_hand_action(hand, options, dealer_upcard):
        """Get the action to take on the hand ('Hit', 'Stand', etc.)"""

    @abstractstaticmethod
    def wants_even_money():
        """Get a yes/no response for whether a the gambler wants to take even money for a blackjack when facing an Ace."""

    @abstractstaticmethod
    def wants_insurance():
        """Get a yes/no response for whether a user wants to make an insurance bet when facing an Ace."""
