from statistics import mean
from textwrap import dedent

import matplotlib.pyplot as plt

from blackjack.display_utils import money_format, pct_format, zero_division_pct


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

        (self.wins, self.losses, self.pushes, self.insurance_wins, self.insurance_losses,
         self.gambler_blackjacks, self.dealer_blackjacks, self.final_bankrolls) = self._aggregate_metrics(metric_trackers)

    @staticmethod
    def _aggregate_metrics(metric_trackers):
        # Gross metric counts
        wins = 0
        losses = 0
        pushes = 0
        insurance_wins = 0
        insurance_losses = 0
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
            insurance_losses += mt.insurance_losses
            gambler_blackjacks += mt.gambler_blackjacks
            dealer_blackjacks += mt.dealer_blackjacks
            final_bankrolls.append(mt.bankroll_progression[-1])

        return wins, losses, pushes, insurance_wins, insurance_losses, gambler_blackjacks, dealer_blackjacks, final_bankrolls

    def print_summary(self):
        """Print a simple summary of analyzed results."""
        # --- Hand Outcomes ---
        total_hands = sum([self.wins, self.losses, self.pushes, self.insurance_wins])  # Note that insurance losses are not a final outcome of a hand!
        hand_win_pct = zero_division_pct(self.wins, total_hands)
        hand_loss_pct = zero_division_pct(self.losses, total_hands)
        hand_push_pct = zero_division_pct(self.pushes, total_hands)
        hand_insurance_win_pct = zero_division_pct(self.insurance_wins, total_hands)

        # --- Blackjacks ---
        total_blackjacks = self.gambler_blackjacks + self.dealer_blackjacks
        bj_gambler_pct = zero_division_pct(self.gambler_blackjacks, total_blackjacks)
        bj_dealer_pct = zero_division_pct(self.dealer_blackjacks, total_blackjacks)

        # --- Insurance ---
        total_insurance = self.insurance_wins + self.insurance_losses
        ins_win_pct = zero_division_pct(self.insurance_wins, total_insurance)
        ins_loss_pct = zero_division_pct(self.insurance_losses, total_insurance)

        # --- Bankroll ---
        winnings_gross_avg = mean(self.final_bankrolls) - self.initial_bankroll
        winnings_pct_avg = zero_division_pct(winnings_gross_avg, self.initial_bankroll)

        # Return the formatted summary string
        print(dedent(f"""\
            --- Hand Outcomes ---
            
            Total Hands: {total_hands}
            
            Wins: {self.wins} ({pct_format(hand_win_pct)})
            Losses: {self.losses} ({pct_format(hand_loss_pct)})
            Pushes: {self.pushes} ({pct_format(hand_push_pct)})
            Insurance Wins: {self.insurance_wins} ({pct_format(hand_insurance_win_pct)})

            --- Blackjacks ---

            Total Blackjacks: {total_blackjacks}

            Player Blackjacks: {self.gambler_blackjacks} ({pct_format(bj_gambler_pct)})
            Dealer Blackjacks: {self.dealer_blackjacks} ({pct_format(bj_dealer_pct)})

            --- Insurance ---
            
            Total Bets: {total_insurance}
            
            Wins: {self.insurance_wins} ({pct_format(ins_win_pct)}) 
            Losses: {self.insurance_losses} ({pct_format(ins_loss_pct)})

            --- Bankroll ---
            
            Avg Winnings: {money_format(winnings_gross_avg)} ({pct_format(winnings_pct_avg)})

            Max Bankroll: {money_format(max(self.final_bankrolls))}
            Min Bankroll: {money_format(min(self.final_bankrolls))}
            Avg Bankroll: {money_format(mean(self.final_bankrolls))}
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
