class MetricTracker:
    """Class for tracking game metrics for analytics purposes."""
    
    def __init__(self):
        # Metrics
        self.wins = 0
        self.losses = 0
        self.pushes = 0
        self.insurance_wins = 0
        self.gambler_blackjacks = 0
        self.dealer_blackjacks = 0
        
        # Bankroll over time
        self.bankroll_progression = []

    def _increment_metric(self, metric):
        """Increment the desired metric (privately)."""
        if metric == 'turns':
            self.turns += 1
        elif metric == 'wins':
            self.wins += 1
        elif metric == 'losses':
            self.losses += 1
        elif metric == 'pushes':
            self.pushes += 1
        elif metric == 'insurance wins':
            self.insurance_wins += 1
        elif metric == 'gambler blackjacks':
            self.gambler_blackjacks += 1
        elif metric == 'dealer blackjacks':
            self.dealer_blackjacks += 1
        else:
            raise ValueError(f"Unsupported metric: {metric}")

    def process_gambler_hand(self, hand):
        """Track metrics for a played GamblerHand"""
        # Blackjacks
        if hand.status == 'Blackjack':
            self._increment_metric('gambler blackjacks')

        # Outcomes
        if hand.outcome in ('Win', 'Even Money'):
            self._increment_metric('wins')
        elif hand.outcome == 'Loss':
            self._increment_metric('losses')
        elif hand.outcome == 'Push':
            self._increment_metric('pushes')
        elif hand.outcome == 'Insurance Win':
            self._increment_metric('insurance wins')
        else:
            raise ValueError(f"Unsupported hand outcome: {hand.outcome}")

    def process_dealer_hand(self, hand):
        """Track metrics for a played DealerHand."""
        if hand.status == 'Blackjack':
            self._increment_metric('dealer blackjacks')

    def append_bankroll(self, bankroll):
        """Append a bankroll amount to the list of bankrolls tracked."""
        self.bankroll_progression.append(bankroll)
