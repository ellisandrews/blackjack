# Base class for custom exceptions to inherit from (recommended by Python docs)
class Error(Exception):
    pass


class InsufficientBankrollError(Error):
    """Custom exception to raise when attempting to withdraw more than a player's bankroll."""
    pass
