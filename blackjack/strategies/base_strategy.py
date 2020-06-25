from abc import ABC, abstractmethod


class BaseStrategy(ABC):
    """Abstract base class that lays out the methods that must be implemented by all Strategies for in-game decisions."""

    @abstractmethod
    def wants_to_change_wager(self):
        """Get a yes/no response (bool) for whether the gambler wants to change their auto-wager."""

    @abstractmethod
    def get_new_auto_wager(self):
        """Get a new auto-wager amount (float)."""

    @abstractmethod
    def get_hand_action(self, hand, options, dealer_upcard):
        """Get the action to take on the hand ('Hit', 'Stand', etc.)"""

    @abstractmethod
    def wants_even_money(self):
        """Get a yes/no response (bool) for whether a the gambler wants to take even money for a blackjack when facing an Ace."""

    @abstractmethod
    def wants_insurance(self):
        """Get a yes/no response (bool) for whether a user wants to make an insurance bet when facing an Ace."""
