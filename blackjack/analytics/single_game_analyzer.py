from statistics import mean
from textwrap import dedent

import matplotlib.pyplot as plt

from blackjack.display_utils import money_format, pct_format


def slice_label(percent, all_vals):
    """
    Create a pie chart slice label of the form `x% (absolute count)` (e.g. --> 45.3% (153) ).
    Note that this function was ripped from the matplotlib documentation on the subject.
    """
    absolute = int(percent/100.0*sum(all_vals))
    return "{:.1f}%\n({:d})".format(percent, absolute)


class SingleGameAnalyzer:
    """Class for running basic analytics on tracked metrics for a single game."""

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

        # Winnings
        gross_winnings = self.bankroll_progression[-1] - self.bankroll_progression[0]
        pct_winnings = gross_winnings / self.bankroll_progression[0] * 100.0

        # Metric percentages
        win_pct = self.wins / hands * 100.0
        loss_pct = self.losses / hands * 100.0
        push_pct = self.pushes / hands * 100.0
        insurance_win_pct = self.insurance_wins / hands * 100.0

        # Return the formatted summary string
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
            Avg Bankroll: {money_format(mean(self.bankroll_progression))}

            Winnings: {money_format(gross_winnings)} ({pct_format(pct_winnings)})
            """
        )

    def create_plots(self):
        """Create charts summarizing the tracked metric data."""
        # Create a figure to hold the plots (called "axes")
        fig, (ax1, ax2) = plt.subplots(2, 1)  # 2 rows 1 column of axes (i.e. stacked plots)

        # Axes 1: Bankroll vs. Turn Number (line chart)
        ax1.plot(self.bankroll_progression)
        ax1.set_xlabel('Turn Number')
        ax1.set_ylabel('Bankroll ($)')
        ax1.set_title('Bankroll vs. Turn Number')

        # Axes 2: Hand Outcome Breakdown (pie chart)
        data = []
        labels = []
        for metric, label in [
            (self.wins, 'Wins'), (self.losses, 'Losses'), (self.pushes, 'Pushes'), (self.insurance_wins, 'Insurance Wins')
        ]:
            if metric > 0:
                data.append(metric)
                labels.append(label)

        wedges, _, _ = ax2.pie(data, autopct=lambda pct: slice_label(pct, data), textprops=dict(color="w")) 
        ax2.legend(wedges, labels, title="Outcomes")
        ax2.set_title('Hand Outcomes')
        ax2.axis('equal')

        # Avoid plot label overlap
        plt.tight_layout()
        plt.show()
