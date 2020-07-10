from blackjack.strategies.default_static_strategy import DefaultStaticStrategy


class InsuranceStaticStrategy(DefaultStaticStrategy):
    """Same as the optimal DefaultStaticStrategy except insurance is bought when facing a dealer Ace."""

    def wants_insurance(self):
        """Get a yes/no response (bool) for whether a user wants to make an insurance bet when facing an Ace."""
        return True
