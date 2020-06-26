from blackjack.strategies.base_static_strategy import BaseStaticStrategy


class DefaultStaticStrategy(BaseStaticStrategy):
    """Default StaticStrategy for optimal odds."""

    def __init__(self):
        super().__init__(strategy_name='default')

    def wants_to_change_wager(self):
        """Get a yes/no response (bool) for whether the gambler wants to change their auto-wager."""
        return False

    def get_new_auto_wager(self):
        """Get a new auto-wager amount (float)."""
        # Will not change the auto-wager in this strategy
        pass

    def wants_even_money(self):
        """Get a yes/no response (bool) for whether a the gambler wants to take even money for a blackjack when facing an Ace."""
        return False

    def wants_insurance(self):
        """Get a yes/no response (bool) for whether a user wants to make an insurance bet when facing an Ace."""
        return False
