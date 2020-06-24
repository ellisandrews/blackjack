import os

from pandas import read_csv

from blackjack.strategies.base_strategy import BaseStrategy


DIRECTORY = os.path.dirname(os.path.realpath(__file__))


class StaticStrategy(BaseStrategy):
    """Default predetermined Strategy for optimal odds."""

    def __init__(self,
                 split_csv=f"{DIRECTORY}/default_split.csv",
                 soft_csv=f"{DIRECTORY}/default_soft.csv",
                 hard_csv=f"{DIRECTORY}/default_hard.csv"
                 ):
        super().__init__()
        self.split_df = self._load_df(split_csv)
        self.soft_df = self._load_df(soft_csv)
        self.hard_df = self._load_df(hard_csv)

    # --- Helper Methods --- #

    @staticmethod
    def _load_df(csv_path):
        """Load a DataFrame from a CSV for determining actions."""
        return read_csv(csv_path, index_col=0)

    # --- Required Methods --- #

    def wants_to_change_wager(self):
        """Get a yes/no response (bool) for whether the gambler wants to change their auto-wager."""
        return False

    def get_new_auto_wager(self):
        """Get a new auto-wager amount (float)."""
        # Will not change the auto-wager in this strategy
        pass

    def get_hand_action(self, hand, options, dealer_upcard):
        """Get the action to take on the hand ('Hit', 'Stand', etc.)"""
        # Get the dealer value by which to look up the correct action
        column = dealer_upcard.csv_format()

        # If splitting is an option, check if that action should be taken first.
        if 'Split' in options.values():
            row = hand.cards[0].csv_format()
            if self.split_df.at[row, column] == 'Yes':
                return 'Split'

        # Use the appropriate 'soft' or 'hard' hand DataFrame to decide which action should be taken.
        row = hand.final_total()
        if hand.is_soft():
            return self.soft_df.at[row, column]
        else:
            return self.hard_df.at[row, column]

    def wants_even_money(self):
        """Get a yes/no response (bool) for whether a the gambler wants to take even money for a blackjack when facing an Ace."""
        return False

    def wants_insurance(self):
        """Get a yes/no response (bool) for whether a user wants to make an insurance bet when facing an Ace."""
        return False
