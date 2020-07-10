from collections import OrderedDict
from time import sleep

from blackjack.analytics.metric_tracker import MetricTracker
from blackjack.exc import InsufficientBankrollError
from blackjack.models.hand import DealerHand, GamblerHand
from blackjack.display_utils import clear, header, money_format, pct_format


def render_after(instance_method):
    """Decorator for calling the `render()` instance method after calling an instance method."""
    def wrapper(self, *args, **kwargs):
        instance_method(self, *args, **kwargs)
        if self.verbose:
            self.render()
    return wrapper


class GameController:

    def __init__(self, gambler, dealer, shoe, strategy, verbose=True, max_turns=None):
        # Configured models from game setup
        self.gambler = gambler
        self.dealer = dealer
        self.shoe = shoe

        # Strategy to employ for in-game decision making
        self.strategy = strategy

        # Turn activity log
        self.activity = []

        # Render options
        self.verbose = verbose       # Switch for printing/suppressing output
        self.hide_dealer = True      # Switch for showing/hiding the dealer's buried card during rendering
        self.dealer_playing = False  # Switch for when dealer is playing and no user actions available

        # Keep track of number of turns played (and the max number of turns to play if applicable)
        self.turn = 0
        self.max_turns = max_turns

        # Metric tracking (for analytics)
        self.metric_tracker = MetricTracker()

    def play(self):
        """Main game loop that controls entire game flow."""
        # Track the starting bankroll
        self.metric_tracker.append_bankroll(self.gambler.bankroll)

        # Play the game to completion
        while self.play_condition():

            # Increment the turn counter
            self.turn += 1

            # Initialize the activity log for the turn
            self.add_activity(f"Turn #{self.turn}")

            # Vet the gambler's auto-wager against their bankroll, and ask if they would like to change their wager or cash out.
            self.check_gambler_wager()
            if self.gambler.auto_wager == 0:  # If they cashed out, don't play the turn. The game is over.
                break

            # Deal 2 cards from the shoe to the gambler's and the dealer's hands. Place the gambler's auto-wager on the hand.
            self.deal()

            # Carry out pre-turn flow (for blackjacks, insurance, etc).
            self.play_pre_turn()
            
            # Play the gambler's turn (if necessary).
            self.play_gambler_turn()

            # Play the dealer's turn (if necessary).
            self.play_dealer_turn()

            # Settle gambler hand wins and losses.
            self.settle_up()

            # Track metrics and reset in order to proceed with the next turn.
            self.finalize_turn()

        # Render a game over message
        self.finalize_game()

    def play_condition(self):
        """Return True to play another turn, False otherwise."""
        # If the gambler is cashed out or out of money there is no turn to play.
        if self.gambler.is_finished():
            return False
        
        # If max number of turns imposed make sure we haven't hit it yet.
        if self.max_turns:
            return self.turn < self.max_turns
        
        # Checks have passed, play the turn.
        return True

    @render_after
    def add_activity(self, *messages):
        """Add message(s) to the activity log."""
        # Add all messages
        for message in messages:
            self.activity.append(message)

    def check_gambler_wager(self):
        """
        Pre-turn vetting of the gambler's wager.
        1. Check whether the gambler has enough bankroll to place their auto-wager. If not, set to remaining bankroll.
        2. Ask the gambler if they'd like to change their auto-wager or cash out. Allow them to do so.
        """
        # If the gambler doesn't have sufficient bankroll to place their auto-wager, set their auto-wager to their remaining bankroll.
        if not self.gambler.can_place_auto_wager():
            self.gambler.set_new_auto_wager(self.gambler.bankroll)
            self.add_activity(f"Insufficient bankroll to place current auto-wager. Setting auto-wager to remaining bankroll.")

        # Check whether the user wants to change their auto-wager or cash out.
        if self.strategy.wants_to_change_wager():
            self.set_new_auto_wager()

    def set_new_auto_wager(self):
        """Set a new auto-wager amount."""
        # Set the gambler's auto_wager to $0.00.
        self.gambler.zero_auto_wager()

        # Ask the gambler for a new auto wager and set it, with some validation.
        success = False
        while not success:
            # Get the new auto-wager from the strategy
            new_auto_wager = self.strategy.get_new_auto_wager()

            # This validates that they've entered a wager <= their bankroll
            try:
                self.gambler.set_new_auto_wager(new_auto_wager)
                success = True
            except InsufficientBankrollError as err:
                print(f"{err}. Please try again.")

    def deal(self):
        """Deal cards from the Shoe to both the gambler and the dealer to form their initial hands."""
        # Deal 4 cards from the shoe
        card_1, card_2, card_3, card_4 = self.shoe.deal_n_cards(4)

        # Create the Hands from the dealt cards.
        # Deal like they do a casinos --> one card to each player at a time, starting with the gambler.
        self.gambler.hands.append(GamblerHand(cards=[card_1, card_3]))
        self.dealer.hand = DealerHand(cards=[card_2, card_4])

        # Place the gambler's auto-wager on the hand. We've already vetted that they have sufficient bankroll.
        self.gambler.place_auto_wager()

        # Log it
        self.add_activity('Dealing hands.')

    def play_pre_turn(self):
        """Carry out pre-turn flow for blackjacks and insurance."""
        # --- BLACKJACK CHECKING FOR PRE-TURN FLOW --- #

        # Grab the gambler's dealt hand for pre-turn processing.
        gambler_hand = self.gambler.first_hand()

        # Check if the gambler has blackjack. Log it if so.
        gambler_has_blackjack = gambler_hand.is_blackjack()
        if gambler_has_blackjack:
            self.add_activity(f"{self.gambler.name} has blackjack.")

        # Check if the dealer has blackjack, but don't display it to the gambler yet.
        dealer_has_blackjack = self.dealer.hand.is_blackjack()

        # --- DEALER ACE PRE-TURN FLOW --- #

        # Insurance comes into play if the dealer's upcard is an ace
        if self.dealer.is_showing_ace():

            # Log it.
            self.add_activity('Dealer is showing an Ace.')

            # If the gambler has blackjack, they can either take even money or let it ride.
            if gambler_has_blackjack:

                if self.strategy.wants_even_money():
                    # Pay out even money (meaning 1:1 hand wager).
                    self.set_hand_outcome(gambler_hand, 'Even Money')
                    self.add_activity(f"{self.gambler.name} took even money.")
                else:
                    if dealer_has_blackjack:
                        # Both players have blackjack. Gambler reclaims their wager and that's all.
                        self.set_hand_outcome(gambler_hand, 'Push')
                        self.add_activity('Dealer has blackjack.', 'Hand is a push.')
                    else:
                        # Dealer does not have blackjack. Gambler has won a blackjack (which pays 3:2)
                        self.set_hand_outcome(gambler_hand, 'Win')
                        self.add_activity('Dealer does not have blackjack.', f"{self.gambler.name} wins 3:2.")

            # If the gambler does not have blackjack they can buy insurance.
            else:
                # Gambler must have sufficient bankroll to place an insurance bet.
                gambler_can_afford_insurance = self.gambler.can_place_insurance_wager()

                if gambler_can_afford_insurance and self.strategy.wants_insurance():

                    # Insurnace is a side bet that is half their wager, and pays 2:1 if dealer has blackjack.
                    self.gambler.place_insurance_wager()

                    # The turn is over if the dealer has blackjack. Otherwise, continue on to playing the hand.
                    if dealer_has_blackjack:
                        self.hide_dealer = False  # Show the dealer's blackjack.
                        self.set_hand_outcome(gambler_hand, 'Insurance Win')
                        self.add_activity('Dealer has blackjack.', f"{self.gambler.name}'s insurnace wager wins 2:1 (hand wager loses).")
                    else:
                        gambler_hand.lost_insurance = True
                        self.add_activity('Dealer does not have blackjack.', f"{self.gambler.name}'s insurance wager loses.")

                # If the gambler does not (or cannot) place an insurance bet, they lose if the dealer has blackjack. Otherwise, hand continues.
                else:
                    # Message for players who were not offered the option to place an insurance bet to due insufficient bankroll.
                    if not gambler_can_afford_insurance:
                        self.add_activity('Insufficient bankroll to place insurance wager.')

                    # The turn is over if the dealer has blackjack. Otherwise, continue on to playing the hand.
                    if dealer_has_blackjack:
                        self.hide_dealer = False
                        self.add_activity('Dealer has blackjack.', f"{self.gambler.name} loses the hand.")
                        self.set_hand_outcome(gambler_hand, 'Loss')
                    else:
                        self.add_activity('Dealer does not have blackjack.')

        # --- DEALER FACE CARD PRE-TURN FLOW --- #

        # If the dealer's upcard is a face card, insurance is not in play but need to check if the dealer has blackjack.
        elif self.dealer.is_showing_face_card():

            # Log the blackjack check.
            self.add_activity('Checking if the dealer has blackjack.')

            # If the dealer has blackjack, it's a push if the player also has blackjack. Otherwise, the player loses.
            if dealer_has_blackjack:

                self.hide_dealer = False
                self.add_activity('Dealer has blackjack.')

                if gambler_has_blackjack:
                    self.add_activity('Hand is a push.')
                    self.set_hand_outcome(gambler_hand, 'Push')
                else:
                    self.add_activity(f"{self.gambler.name} loses the hand.")
                    self.set_hand_outcome(gambler_hand, 'Loss')

            # If dealer doesn't have blackjack, the player wins if they have blackjack. Otherwise, play the turn.
            else:
                self.add_activity('Dealer does not have blackjack.')
                
                if gambler_has_blackjack:
                    self.add_activity(f"{self.gambler.name} wins 3:2.")
                    self.set_hand_outcome(gambler_hand, 'Win')

        # --- REGULAR PRE-TURN FLOW --- #

        # If the dealer's upcard is not an ace or a face card, they cannot have blackjack.
        # If the player has blackjack here, payout 3:2 and the hand is over. Otherwise, continue with playing the hand.
        else:
            if gambler_has_blackjack:
                self.add_activity(f"{self.gambler.name} wins 3:2.")
                self.set_hand_outcome(gambler_hand, 'Win')

    def play_gambler_turn(self):
        """Play the gambler's turn, meaning play all of the gambler's hands to completion."""
        # Log a message that the turn is being played, or there's no need to play it.
        if any(hand.status == 'Pending' for hand in self.gambler.hands):
            message = f"Playing {self.gambler.name}'s turn."
        else:
            message = f"No turn to play for {self.gambler.name}."
        self.add_activity(message)
        
        # Use a while loop due to the fact that self.hands can grow while iterating (via splitting)
        while any(hand.status == 'Pending' for hand in self.gambler.hands):
            hand = next(hand for hand in self.gambler.hands if hand.status == 'Pending')  # Grab the next unplayed hand
            self.play_gambler_hand(hand)

    def play_gambler_hand(self, hand):
        """Play a gambler hand."""
        # Set the hand's status to 'Playing', and loop until this status changes.
        self.set_hand_status(hand, 'Playing')

        while hand.status == 'Playing':

            # Handle single-card hands that result from splitting
            if len(hand.cards) == 1:
                
                # Hit the hand automatically to make it complete.
                self.hit_hand(hand)

                # Check if the hand is blackjack. If it is, it's an automatic win (we know dealer doesn't have blackjack)
                if hand.is_blackjack():
                    self.set_hand_status(hand, 'Blackjack')
                    self.set_hand_outcome(hand, 'Win')
                    break

                # Split Aces only get 1 more card by rule. If they're not a blackjack mark them as stood.
                if hand.cards[0].is_ace():
                    if hand.status != 'Blackjack':
                        self.set_hand_status(hand, 'Stood')
                    break

            # Get the possible options for hand action to take.
            options = self.get_hand_options(hand)

            # Get the gambler's action (e.g. 'Hit', 'Stand', etc.)
            action = self.strategy.get_hand_action(hand, options, self.dealer.up_card())

            if action == 'Hit':
                self.hit_hand(hand)  # Deal another card and keep playing the hand.

            elif action == 'Stand':
                self.set_hand_status(hand, 'Stood')  # Do nothing, hand is played.

            elif action == 'Double':
                self.double_hand(hand)  # Double the wager and deal another card. Hand is played.

            elif action == 'Split':
                self.split_hand(hand)  # Put the second card into a new hand and keep playing this hand.

            else:
                raise Exception('Unhandled response.')  # Should never get here

            # If the hand is 21 or busted, the hand is done being played.
            if hand.is_21():
                self.set_hand_status(hand, 'Stood')
            elif hand.is_busted():
                self.set_hand_status(hand, 'Busted')
                self.set_hand_outcome(hand, 'Loss')

    def get_hand_options(self, hand):
        """Get the options (available actions) that can be taken on a hand."""
        # Default options that are always available
        options = OrderedDict([('h', 'Hit'), ('s', 'Stand')])

        # Add the option to double if applicable
        if hand.is_doubleable() and self.gambler.can_place_wager(hand.wager):
            options['d'] = 'Double'

        # Add the option to split if applicable
        if hand.is_splittable() and self.gambler.can_place_wager(hand.wager):
            options['x'] = 'Split'

        return options

    @render_after
    def hit_hand(self, hand):
        """Add a card to a hand from the shoe."""
        card = self.shoe.deal_card()  # Deal a card
        hand.cards.append(card)  # Add the card to the hand

    @render_after
    def split_hand(self, hand):
        """Split a hand."""
        split_card = hand.cards.pop(1)  # Pop the second card off the hand to make a new hand
        new_hand = GamblerHand(cards=[split_card], hand_number=len(self.gambler.hands) + 1)  # TODO: Do away with hand_number
        self.gambler.place_hand_wager(hand.wager, new_hand)  # Place the same wager on the new hand
        self.gambler.hands.append(new_hand)  # Add the hand to the gambler's list of hands

    def double_hand(self, hand):
        """Double a hand, meaning double the wager on it and hit it with one more card."""
        self.gambler.place_hand_wager(hand.wager, hand)  # Double the wager on the hand
        self.hit_hand(hand)  # Add another card to the hand from the shoe
        self.set_hand_status(hand, 'Doubled')  # Set the status to Doubled

    @render_after
    def set_hand_status(self, hand, status):
        """Set a new status for a hand."""
        hand.status = status

    @render_after
    def set_hand_outcome(self, hand, outcome):
        """Set the outcome of the hand, and change the status if applicable."""
        hand.outcome = outcome        
        if hand.status == 'Pending':
            hand.status = 'Played'

    def play_dealer_turn(self):
        """Play the dealer's turn (if necessary)."""
        # Toggle dealer display options
        self.hide_dealer = False
        self.dealer_playing = True

        # The dealer's turn need only be played if there are gambler hands that are still active
        if not any(hand.status in ('Doubled', 'Stood') for hand in self.gambler.hands):
            self.dealer_playing = False
            return

        self.add_activity("Playing the Dealer's turn.")

        # Grab the dealer's lone hand to be played
        hand = self.dealer.hand

        # Set the hand's status to 'Playing', and loop until this status changes.
        self.set_hand_status(hand, 'Playing')
        
        while hand.status == 'Playing':

            # Pause for user to follow along if applicable
            if self.verbose:
                sleep(1)

            # Get the hand total.
            total = hand.final_total()

            # Dealer hits under 17 and must hit a soft 17.
            if total < 17 or (total == 17 and hand.is_soft()):
                self.hit_hand(hand)
            
            # Dealer stands at 17 and above.
            else:
                self.set_hand_status(hand, 'Stood')

            # If the hand is busted dealer is done playing.
            if hand.is_busted():
                self.set_hand_status(hand, 'Busted')

        # Mark the dealer's turn as finished.
        self.dealer_playing = False

    def pay_out_hand(self, hand, payout_type):
        """Pay out hand winnings, including wager reclaim."""
        # Pay out winning hand wagers 1:1 and reclaim the wager
        if payout_type == 'wager':
            self.perform_hand_payout(hand, 'winning_wager', '1:1')
            self.perform_hand_payout(hand, 'wager_reclaim')
        
        # Pay out winning blackjack hands 3:2 and reclaim the wager
        elif payout_type == 'blackjack':
            self.perform_hand_payout(hand, 'winning_wager', '3:2')
            self.perform_hand_payout(hand, 'wager_reclaim')

        # Pay out winning insurance wagers 2:1 and reclaim the insurance wager
        elif payout_type == 'insurance':
            self.perform_hand_payout(hand, 'winning_insurance', '2:1')
            self.perform_hand_payout(hand, 'insurance_reclaim')
        
        # Reclaim wager in case of a push
        elif payout_type == 'push':
            self.perform_hand_payout(hand, 'wager_reclaim')
        
        # Should not get here
        else:
            raise ValueError(f"Invalid payout type: '{payout_type}'")

    def perform_hand_payout(self, hand, payout_type, odds=None):
        """Determine hand winnings and execute the payout."""
        # Validate args passed in
        if payout_type in ('winning_wager', 'winning_insurance'):
            assert odds, 'Must specify odds for wager and insurance payouts!'
            antecedent, consequent = map(int, odds.split(':'))
        
        # Determine the payout amount by the payout_type (and odds if applicable)
        if payout_type == 'winning_wager':
            amount = hand.wager * antecedent / consequent
            message = f"Adding winning hand payout of {money_format(amount)} to bankroll."
        
        elif payout_type == 'wager_reclaim':
            amount = hand.wager
            message = f"Reclaiming hand wager of {money_format(amount)}."
        
        elif payout_type == 'winning_insurance':
            amount = hand.insurance * antecedent / consequent
            message = f"Adding winning insurance payout of {money_format(amount)} to bankroll."
        
        elif payout_type == 'insurance_reclaim':
            amount = hand.insurance
            message = f"Reclaiming insurance wager of {money_format(amount)}."

        else:
            raise ValueError(f"Invalid payout type: '{payout_type}'")

        hand.earnings += amount
        self.gambler.payout(amount)
        self.add_activity(f"Hand {hand.hand_number}: {message}")

    def determine_hand_outcome(self, hand, dealer_hand):
        """Determine a hand's outcome against a dealer hand if it is not yet known."""
        # If the hand is busted it's a loss
        if hand.status == 'Busted':
            self.set_hand_outcome(hand, 'Loss')

        # If the hand is not busted and the dealer's hand is busted it's a win
        elif dealer_hand.status == 'Busted':
            self.set_hand_outcome(hand, 'Win')

        # If neither gambler nor dealer hand is busted, compare totals to determine wins and losses.
        else:
            hand_total = hand.final_total()
            dealer_hand_total = dealer_hand.final_total()

            if hand_total > dealer_hand_total:
                self.set_hand_outcome(hand, 'Win')
            elif hand_total == dealer_hand_total:
                self.set_hand_outcome(hand, 'Push')
            else:
                self.set_hand_outcome(hand, 'Loss')

    def settle_hand(self, hand):
        """Settle any outstanding wagers on a hand (relative to the dealer's hand)."""
        # Determine the outcome of the hand against the dealer's if the outcome is unknown
        if not hand.outcome:
            self.determine_hand_outcome(hand, self.dealer.hand)

        # Perform payout based on the hand outcome
        if hand.outcome == 'Win':
            if hand.status == 'Blackjack':
                self.pay_out_hand(hand, 'blackjack')
            else:
                self.pay_out_hand(hand, 'wager')

        elif hand.outcome == 'Push':
            self.pay_out_hand(hand, 'push')

        elif hand.outcome == 'Even Money':
            self.pay_out_hand(hand, 'wager')

        elif hand.outcome == 'Insurance Win':
            self.pay_out_hand(hand, 'insurance')

        elif hand.outcome == 'Loss':
            self.add_activity(f"Hand {hand.hand_number}: Forfeiting hand wager of {money_format(hand.wager)}.")

        else:
            raise ValueError(f"Unhandled hand outcome: {hand.outcome}")

    def settle_up(self):
        """For each of the gambler's hands, settle wagers against the dealer's hand."""
        for hand in self.gambler.hands:
            self.settle_hand(hand)

    def track_metrics(self):
        """Update the tracked metrics with the current turn's data."""
        # Track gambler hand metrics
        for hand in self.gambler.hands:
            self.metric_tracker.process_gambler_hand(hand)
        
        # Track dealer hand metrics
        self.metric_tracker.process_dealer_hand(self.dealer.hand)

        # Track gambler's bankroll through time
        self.metric_tracker.append_bankroll(self.gambler.bankroll)

    def finalize_turn(self):
        """Clean up the current turn in preparation for the next turn."""
        # Render the final status of the turn if applicable.
        if self.verbose:
            self.render()
        
        # Update tracked metrics
        self.track_metrics()

        # Reset the activity log for the next turn.
        self.activity = []

        # Discard both the gambler and the dealer's hands.
        self.gambler.discard_hands()
        self.dealer.discard_hand()
        
        # Reset hide_dealer for the next turn.
        self.hide_dealer = True

        # Pause exectution until the user wants to proceed if applicable.
        if self.verbose:
            input('Push ENTER to proceed => ')

    def finalize_game(self):
        """Wrap up the game, rendering analytics and creating graphs if necessary."""
        # Render game over message if applicable
        if self.verbose:
            self.render_game_over()
        
    def render(self):
        """Print out the entire game (comprised of table, activity log, and user action) to the console."""
        clear()  # Clear previous rendering
        self.render_table()
        self.render_activity()
        self.render_action()

    def render_table(self):
        """Print out the players and the hands of cards (if they've been dealt)."""
        print(header('TABLE'))
        
        # Print the dealer's hand. If `hide_dealer` is True, don't factor in the dealer's buried card.
        num_dashes = len(self.dealer.name) + 6
        print(f"{'-'*num_dashes}\n   {self.dealer.name.upper()}   \n{'-'*num_dashes}\n")
        if self.dealer.hand:
            print(self.dealer.hand.pretty_format(hide=self.hide_dealer))
        else:
            print('No hand.')

        # Print the gambler's hand(s)
        num_dashes = len(self.gambler.name) + 6
        print(f"\n{'-'*num_dashes}\n   {self.gambler.name.upper()}   \n{'-'*num_dashes}\n\nBankroll: {money_format(self.gambler.bankroll)}  |  Auto-Wager: {money_format(self.gambler.auto_wager)}\n")
        if self.gambler.hands:
            for hand in self.gambler.hands:
                print(hand.pretty_format())
                print()
        else:
            print('No hands.')

    def render_activity(self):
        """Print out the activity log for the current turn."""
        print(header('ACTIVITY'))
        for message in self.activity:
            print(message)

    def render_action(self):
        """Print out the action section that the user interacts with."""
        print(header('ACTION'))
        if self.dealer_playing:
            print('Dealer playing turn...')

    def render_game_over(self):
        """Print out a final summary message once the game has ended."""
        # Show game over message
        print(header('GAME OVER'))

        # Print a final message after the gambler is finished
        if self.gambler.auto_wager == 0 or self.turn == self.max_turns:
            action = f"{self.gambler.name} cashed out with bankroll: {money_format(self.gambler.bankroll)}."
            message = 'Thanks for playing!'
        else:
            action = f"{self.gambler.name} is out of money."
            message = 'Better luck next time!'

        print(f"{action}\n\n{message}")
