import os

from pandas import read_csv

from blackjack.strategies.base_strategy import BaseStrategy


DIRECTORY = os.path.dirname(os.path.realpath(__file__))


class BaseStaticStrategy(BaseStrategy):
    """
    Base predetermined Strategy from which other static Strategies can be derrived.
    Note that concrete static Strategies must implement the required BaseStrategy methods omitted here.
    """

    def __init__(self, strategy_name):
        super().__init__()
        self.split_df = self._load_df(strategy_name, 'split')
        self.soft_df = self._load_df(strategy_name, 'soft')
        self.hard_df = self._load_df(strategy_name, 'hard')

    @staticmethod
    def _load_df(strategy_name, csv_type):
        """Load a DataFrame from a CSV for determining actions."""
        csv_path = f"{DIRECTORY}/csv/{strategy_name}/{csv_type}.csv"
        return read_csv(csv_path, index_col=0)

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
            action = self.soft_df.at[row, column]
        else:
            action = self.hard_df.at[row, column]

        # Handle the edge case where doubling is the recommended action, but the user doesn't have enough money to do so.
        if action == 'Double' and 'Double' not in options.values():
            return 'Hit'
        
        return action
