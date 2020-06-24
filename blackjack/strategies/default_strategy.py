from blackjack.strategies.base_strategy import BaseStrategy


class DefaultStrategy(BaseStrategy):
    """Default predetermined Strategy for optimal odds."""

    def __init__(self):
        super().__init__()
        


    def wants_to_change_wager(self):
        """Get a yes/no response (bool) for whether the gambler wants to change their auto-wager."""
        return False

    def get_new_auto_wager(self):
        """Get a new auto-wager amount (float)."""
        # Will not change the auto-wager in this strategy
        pass

    def get_hand_action(self, hand, options, dealer_upcard):
        """Get the action to take on the hand ('Hit', 'Stand', etc.)"""

    def wants_even_money(self):
        """Get a yes/no response (bool) for whether a the gambler wants to take even money for a blackjack when facing an Ace."""
        return False

    def wants_insurance(self):
        """Get a yes/no response (bool) for whether a user wants to make an insurance bet when facing an Ace."""
        return False
