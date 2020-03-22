# Base class for custom exceptions to inherit from (recommended by Python docs)
class Error(Exception):
    pass


class InsufficientBankrollError(Error):
    """Custom exception to raise when attempting to use more funds than are in player's bankroll."""
    pass


class OverdraftError(Error):
    """Custom exception to raise when a player's bankroll attempts to go below zero."""
    pass
