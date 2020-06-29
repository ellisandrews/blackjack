from textwrap import dedent

from blackjack.utils import money_format, pct_format


class Analyzer:
    """Class for running basic analytics on tracked game metrics."""

    def __init__(self,
                 wins=0,
                 losses=0,
                 pushes=0,
                 insurance_wins=0,
                 gambler_blackjacks=0,
                 dealer_blackjacks=0,
                 bankroll_progression=None
                ):
        self.wins = wins
        self.losses = losses
        self.pushes = pushes
        self.insurance_wins = insurance_wins
        self.gambler_blackjacks = gambler_blackjacks
        self.dealer_blackjacks = dealer_blackjacks
        self.bankroll_progression = bankroll_progression or []

    def format_summary(self):
        """Get simple analytics summmary and format it to be rendered for the user."""
        # Total number of hands
        hands = sum([self.wins, self.losses, self.pushes, self.insurance_wins])

        # Metric percentages
        win_pct = self.wins / hands * 100.0
        loss_pct = self.losses / hands * 100.0
        push_pct = self.pushes / hands * 100.0
        insurance_win_pct = self.insurance_wins / hands * 100.0

        # Returnt the formatted summary string
        return dedent(f"""\
            Hands: {hands}
            
            Wins: {self.wins} ({pct_format(win_pct)})
            Losses: {self.losses} ({pct_format(loss_pct)})
            Pushes: {self.pushes} ({pct_format(push_pct)})
            Insurance Wins: {self.insurance_wins} ({pct_format(insurance_win_pct)})
            
            Player Blackjacks: {self.gambler_blackjacks}
            Dealer Blackjacks: {self.dealer_blackjacks}

            Max Bankroll: {money_format(max(self.bankroll_progression))}
            Min Bankroll: {money_format(min(self.bankroll_progression))}
            """
        )
