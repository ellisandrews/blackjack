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


class MultiGameAnalyzer:
    """Class for running basic analytics on tracked metrics for a multiple games."""

    def __init__(self, metric_trackers):
        # All games have the same initial bankroll. Grab it from the first game.
        self.initial_bankroll = metric_trackers[0].bankroll_progression[0]

        (self.wins, self.losses, self.pushes, self.insurance_wins, 
         self.gambler_blackjacks, self.dealer_blackjacks, self.final_bankrolls) = self._aggregate_metrics(metric_trackers)

    @staticmethod
    def _aggregate_metrics(metric_trackers):
        # Gross metric counts
        wins = 0
        losses = 0
        pushes = 0
        insurance_wins = 0
        gambler_blackjacks = 0
        dealer_blackjacks = 0

        # Final bankrolls
        final_bankrolls = []

        # Process each MetricTracker
        for mt in metric_trackers:
            wins += mt.wins
            losses += mt.losses
            pushes += mt.pushes
            insurance_wins += mt.insurance_wins
            gambler_blackjacks += mt.gambler_blackjacks
            dealer_blackjacks += mt.dealer_blackjacks
            final_bankrolls.append(mt.bankroll_progression[-1])

        return wins, losses, pushes, insurance_wins, gambler_blackjacks, dealer_blackjacks, final_bankrolls

    def print_summary(self):
        """Print a simple summary of analyzed results."""
        # Total number of hands
        hands = sum([self.wins, self.losses, self.pushes, self.insurance_wins])

        # Winnings
        avg_gross_winnings = mean(self.final_bankrolls) - self.initial_bankroll
        avg_pct_winnings = avg_gross_winnings / self.initial_bankroll * 100.0

        # Metric percentages
        win_pct = self.wins / hands * 100.0
        loss_pct = self.losses / hands * 100.0
        push_pct = self.pushes / hands * 100.0
        insurance_win_pct = self.insurance_wins / hands * 100.0

        # Return the formatted summary string
        print(dedent(f"""\
            Hands: {hands}
            
            Wins: {self.wins} ({pct_format(win_pct)})
            Losses: {self.losses} ({pct_format(loss_pct)})
            Pushes: {self.pushes} ({pct_format(push_pct)})
            Insurance Wins: {self.insurance_wins} ({pct_format(insurance_win_pct)})
            
            Player Blackjacks: {self.gambler_blackjacks}
            Dealer Blackjacks: {self.dealer_blackjacks}

            Max Bankroll: {money_format(max(self.final_bankrolls))}
            Min Bankroll: {money_format(min(self.final_bankrolls))}
            Avg Bankroll: {money_format(mean(self.final_bankrolls))}

            Avg Winnings: {money_format(avg_gross_winnings)} ({pct_format(avg_pct_winnings)})
            """)
        )

    def create_plots(self):
        """Create charts summarizing the tracked metric data."""
        # Create a figure to hold the plots (called "axes")
        fig, (ax1, ax2) = plt.subplots(2, 1)  # 2 rows 1 column of axes (i.e. stacked plots)

        # Axes 1: Final Bankroll Distribution (Histogram)
        ax1.hist(self.final_bankrolls)
        ax1.set_xlabel('Final Bankroll ($)')
        ax1.set_ylabel('Count')
        ax1.set_title('Final Bankrolls')

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
