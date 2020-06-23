from collections import OrderedDict
from functools import partial
from time import sleep

from blackjack.exc import InsufficientBankrollError
from blackjack.models.hand import DealerHand, GamblerHand
from blackjack.user_input import choice_response, float_response, get_user_input, max_retries_exit, yes_no_response
from blackjack.utils import clear, header


class GameController:

    def __init__(self, gambler, dealer, shoe):
        # Configured models from game setup
        self.gambler = gambler
        self.dealer = dealer
        self.shoe = shoe

        # Turn-by-turn activity log
        self.activity = []

        # Switch for showing/hiding the dealer's buried card during rendering
        self.hide_dealer = True

    def play(self):
        """Main game loop that controls entire game flow."""
        
        while not self.gambler.is_finished():

            # Initialize the activity log for the turn
            self.add_activity('--- New Turn ---')

            # Vet the gambler's auto-wager against their bankroll, and ask if they would like to change their wager or cash out.
            self.check_gambler_wager()
            if self.gambler.bankroll == 0:  # If they cashed out, don't play the turn. The game is over.
                break

            # Deal 2 cards from the shoe to the gambler's and the dealer's hands. Place the gambler's auto-wager on the hand.
            self.deal()

            # Carry out pre-turn flow (for blackjacks, insurance, etc). If either player had blackjack, there is no turn to play.
            turn_over = self.play_pre_turn()
            if turn_over:
                self.finalize_turn()
                continue
            
            # Play the gambler's turn.
            play_dealer_turn = self.play_gambler_turn()
            
            # Toggle the dealer display option to show the dealer's hand
            self.hide_dealer = False

            # Play the dealer's turn if necessary.
            if play_dealer_turn:
                self.play_dealer_turn()

            # Settle gambler hand wins and losses.
            self.settle_up()

            # Discard hands and pause execution until the user elects to proceed with the next turn.
            self.finalize_turn()

        # Print a game over message
        self.game_over()

    def check_gambler_wager(self):
        """
        Pre-turn vetting of the gambler's wager.
        1. Check whether the gambler has enough bankroll to place their auto-wager. If not, make them enter a new one.
        2. Ask the gambler if they'd like to change their auto-wager or cash out. Allow them to do so.
        """
        # Check if the gambler still has sufficient bankroll to place the auto-wager
        if self.gambler.can_place_auto_wager():

            # Ask if the gambler wants to cash out or change their auto-wager
            response = get_user_input(
                f"{self.gambler.name}, change your auto-wager or cash out? (Bankroll: ${self.gambler.bankroll}; Auto-Wager: ${self.gambler.auto_wager}) (y/n) => ", 
                yes_no_response
            )
            
            # If they want to make a change, make it
            if response == 'yes':
                self.set_new_auto_wager_from_input()

        # If they don't have sufficient bankroll to place auto-wager, force them to set a new one.
        else:
            print(f"Insufficient bankroll to place current auto-wager (Bankroll: ${self.gambler.bankroll}; Auto-Wager: ${self.gambler.auto_wager})")
            self.set_new_auto_wager_from_input()

    def set_new_auto_wager_from_input(self, retries=3):
        """Set a new auto-wager amount from user input (with input vetting and retry logic)."""
        # Set their auto_wager to $0
        self.gambler.zero_auto_wager()

        # Ask them for a new auto wager and set it, with some validation
        attempts = 0
        success = False        
        while not success and attempts < retries:
            # This validates that they've entered a float
            new_auto_wager = get_user_input(f"Please enter an auto-wager amount (Bankroll: ${self.gambler.bankroll}; enter $0 to cash out): $", float_response)
            
            # This validates that they've entered a wager <= their bankroll
            try:
                self.gambler.set_new_auto_wager(new_auto_wager)
                success = True
            except InsufficientBankrollError as e:
                print(f"{e}. Please try again.")
                attempts += 1

        # If they've unsuccessfully tried to enter input the maximum number of times, exit the program
        if attempts == retries and not success:
            max_retries_exit()

    def deal(self):
        """Deal cards from the Shoe to both the gambler and the dealer to form their initial hands."""
        # Deal 4 cards from the shoe
        card_1, card_2, card_3, card_4 = self.shoe.deal_n_cards(4)

        # Create the Hands from the dealt cards.
        # Deal like they do a casinos --> one card to each player at a time, starting with the gambler.
        gambler_hand = GamblerHand(cards=[card_1, card_3])
        dealer_hand = DealerHand(cards=[card_2, card_4])
        
        # Assign the dealt hands appropriately
        self.gambler.hands.append(gambler_hand)
        self.dealer.hand = dealer_hand

        # Place the gambler's auto-wager on the hand. We've already vetted that they have sufficient bankroll.
        self.gambler.place_auto_wager()

        # Log it
        self.add_activity('\nDealing hands.')

    def play_gambler_turn(self):
        """Play the gambler's turn, meaning play all of the gambler's hands to completion."""
        
        self.add_activity(f"Playing {self.gambler.name}'s turn.")
        
        # Use a while loop due to the fact that self.hands can grow while iterating (via splitting)
        while any(hand.status == 'Pending' for hand in self.gambler.hands):
            hand = next(hand for hand in self.gambler.hands if hand.status == 'Pending')  # Grab the next unplayed hand
            self.play_gambler_hand(hand)
        
        # Return True if the dealer's hand needs to be played, False otherwise
        return any(hand.status in ('Doubled', 'Stood') for hand in self.gambler.hands)

    def play_gambler_hand(self, hand):
        """Play a gambler hand."""
        # Set the hand's status to 'Playing', and loop until this status changes.
        hand.status = 'Playing'

        # Print the table to show which hand is being played
        self.render()

        while hand.status == 'Playing':

            # If the hand resulted from splitting, hit it automatically.
            if len(hand.cards) == 1:
                
                self.hit_hand(hand)
                self.render()

                # Split Aces only get 1 more card.
                if hand.cards[0].is_ace():
                    if hand.is_blackjack():
                        hand.status = 'Blackjack'
                    else:
                        hand.status = 'Stood'
                    self.render()
                    break

            # Get the gambler's action from input
            action = self.get_gambler_hand_action(hand)

            if action == 'Hit':
                self.hit_hand(hand)     # Deal another card and keep playing the hand.

            elif action == 'Stand':
                hand.status = 'Stood'   # Do nothing, hand is played.

            elif action == 'Double':
                self.double_hand(hand)  # Deal another card and print. Hand is played.
                hand.status = 'Doubled'

            elif action == 'Split':
                self.split_hand(hand)   # Put the second card into a new hand and keep playing this hand

            else:
                raise Exception('Unhandled response.')  # Should never get here

            # If the hand is 21 or busted, the hand is done being played.
            if hand.is_21():
                hand.status = 'Stood'
            elif hand.is_busted():
                hand.status = 'Busted'

            # Re-render to show the outcome of the action taken
            self.render()

    def get_gambler_hand_action(self, hand):
        """List action options for the user on the hand, and get their choice."""
        # Default options that are always available
        options = OrderedDict([('h', 'Hit'), ('s', 'Stand')])

        # Add the option to double if applicable
        if hand.is_doubleable() and self.gambler.can_place_wager(hand.wager):
            options['d'] = 'Double'

        # Add the option to split if applicable
        if hand.is_splittable() and self.gambler.can_place_wager(hand.wager):
            options['x'] = 'Split'

        # Formatted options to display to the user
        display_options = [f"{option} ({abbreviation})" for abbreviation, option in options.items()]

        # Ask what the user would like to do, given their options
        response = get_user_input(
            f"[ Hand {hand.hand_number} ] What would you like to do? [ {' , '.join(display_options)} ] => ",
            partial(choice_response, choices=options.keys())
        )

        # Return the user's selection ('hit', 'stand', etc.)
        return options[response]

    def hit_hand(self, hand):
        """Add a card to a hand from the shoe."""
        card = self.shoe.deal_card()  # Deal a card
        hand.cards.append(card)  # Add the card to the hand

    def split_hand(self, hand):
        """Split a hand."""
        split_card = hand.cards.pop(1)  # Pop the second card off the hand to make a new hand
        new_hand = GamblerHand(cards=[split_card], hand_number=len(self.gambler.hands) + 1)  # TODO: Do away with hand_number
        self.gambler.place_hand_wager(hand.wager, new_hand)  # Place the same wager on the new hand
        self.gambler.hands.append(new_hand)  # Add the hand to the gambler's list of hands

    def double_hand(self, hand):
        self.gambler.place_hand_wager(hand.wager, hand)  # Double the wager on the hand
        self.hit_hand(hand)  # Add another card to the hand from the shoe

    def play_dealer_turn(self):
        
        # Toggle dealer display options
        self.hide_dealer = False
        
        self.add_activity("Playing the Dealer's turn.")

        # Grab the dealer's lone hand to be played
        hand = self.dealer.hand

        # Set the hand's status to 'Playing', and loop until this status changes.
        hand.status = 'Playing'

        self.render()
        sleep(1)

        while hand.status == 'Playing':

            # Get the hand total
            total = hand.final_total()

            # Dealer hits under 17 and must hit a soft 17.
            if total < 17 or (total == 17 and hand.is_soft()):
                self.hit_hand(hand)
            
            # Dealer stands at 17 and above
            else:
                hand.status = 'Stood'

            # If the hand is busted, it's over. Otherwise, sleep so the user can see the card progression
            if hand.is_busted():
                hand.status = 'Busted'
            
            self.render()
            sleep(1)

    @staticmethod
    def wants_even_money():
        return get_user_input("Take even money? (y/n) => ", yes_no_response)

    @staticmethod
    def wants_insurance():
        return get_user_input("Insurance? (y/n) => ", yes_no_response)

    def discard_hands(self):
        self.gambler.discard_hands()
        self.dealer.discard_hand()

    def play_pre_turn(self):
        """
        Carry out pre-turn flow for blackjacks and insurance.
        Return:
            turn_over (bool) - True if the player's turn is over, False if it needs to be played.
        """
        # --- BLACKJACK CHECKING FOR PRE-TURN FLOW --- #

        # Grab the gambler's dealt hand for pre-turn processing.
        gambler_hand = self.gambler.first_hand()

        # Check if the gambler has blackjack. Log it if so.
        gambler_has_blackjack = gambler_hand.is_blackjack()
        if gambler_has_blackjack:
            self.add_activity(f"{self.gambler.name} has blackjack.")

        # Check if the dealer has blackjack, but don't display it to the gambler yet.
        dealer_has_blackjack = self.dealer.hand.is_blackjack()
        if dealer_has_blackjack:
            self.dealer.hand.status = 'Blackjack'

        # If either player has blackjack, no further turn will be played.
        turn_over = gambler_has_blackjack or dealer_has_blackjack

        # --- DEALER ACE PRE-TURN FLOW --- #

        # Insurance comes into play if the dealer's upcard is an ace
        if self.dealer.is_showing_ace():

            # Log it.
            self.add_activity('Dealer is showing an Ace.')

            # If the gambler has blackjack, they can either take even money or let it ride.
            if gambler_has_blackjack:

                if self.wants_even_money() == 'yes':
                    # Pay out even money (meaning 1:1 hand wager) and show what the dealer had.
                    self.add_activity(f"{self.gambler.name} took even money.")
                    self.pay_out_hand(gambler_hand, 'wager')
                else:
                    if dealer_has_blackjack:
                        # Both players have blackjack. Gambler reclaims their wager and that's all.
                        self.add_activity('Dealer has blackjack.', 'Hand is a push.')
                        self.pay_out_hand(gambler_hand, 'push')
                    else:
                        # Dealer does not have blackjack. Gambler has won a blackjack (which pays 3:2)
                        self.add_activity('Dealer does not have blackjack.', f"{self.gambler.name} wins 3:2.")
                        self.pay_out_hand(gambler_hand, 'blackjack')

            # If the gambler does not have blackjack they can buy insurance.
            else:
                # Gambler must have sufficient bankroll to place an insurance bet.
                gambler_can_afford_insurance = self.gambler.can_place_insurance_wager()

                if gambler_can_afford_insurance and self.wants_insurance() == 'yes':

                    # Insurnace is a side bet that is half their wager, and pays 2:1 if dealer has blackjack.
                    self.gambler.place_insurance_wager()

                    # The turn is over if the dealer has blackjack. Otherwise, continue on to playing the hand.
                    if dealer_has_blackjack:
                        self.hide_dealer = False  # Show the dealer's blackjack.
                        self.add_activity('Dealer has blackjack.', f"{self.gambler.name}'s insurnace wager wins 2:1 (hand wager loses).")
                        self.pay_out_hand(gambler_hand, 'insurance')
                    else:
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
                    self.pay_out_hand(gambler_hand, 'push')
                else:
                    self.add_activity(f"{self.gambler.name} loses the hand.")

            # If dealer doesn't have blackjack, the player wins if they have blackjack. Otherwise, play the turn.
            else:
                self.add_activity('Dealer does not have blackjack.')
                
                if gambler_has_blackjack:
                    self.add_activity(f"{self.gambler.name} wins 3:2.")
                    self.pay_out_hand(gambler_hand, 'blackjack')

        # --- REGULAR PRE-TURN FLOW --- #

        # If the dealer's upcard is not an ace or a face card, they cannot have blackjack.
        # If the player has blackjack here, payout 3:2 and the hand is over. Otherwise, continue with playing the hand.
        else:
            if gambler_has_blackjack:
                self.add_activity(f"{self.gambler.name} wins 3:2.")
                self.pay_out_hand(gambler_hand, 'blackjack')

        return turn_over

    def pay_out_hand(self, hand, payout_type):
        
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

        # Validate args passed in
        if payout_type in ('winning_wager', 'winning_insurance'):
            assert odds, 'Must specify odds for wager and insurance payouts!'
            antecedent, consequent = map(int, odds.split(':'))
        
        # Determine the payout amount by the payout_type (and odds if applicable)
        if payout_type == 'winning_wager':
            amount = hand.wager * antecedent / consequent
            message = f"Adding winning hand payout of ${amount} to bankroll."
        
        elif payout_type == 'wager_reclaim':
            amount = hand.wager
            message = f"Reclaiming hand wager of ${amount}."
        
        elif payout_type == 'winning_insurance':
            amount = hand.insurance * antecedent / consequent
            message = f"Adding winning insurance payout of ${amount} to bankroll."
        
        elif payout_type == 'insurance_reclaim':
            amount = hand.insurance
            message = f"Reclaiming insurance wager of ${amount}."

        else:
            raise ValueError(f"Invalid payout type: '{payout_type}'")

        self.gambler.payout(amount)
        self.add_activity(message)

    def settle_hand(self, hand):
        """Settle any outstanding wagers on a hand (relative to the dealer's hand)."""
        self.add_activity(f"\n[ Hand {hand.hand_number} ]")

        # If the gambler's hand is busted, it's a loss regardless
        if hand.status == 'Busted':
            self.add_activity('Outcome: LOSS', f"${hand.wager} hand wager lost.")

        # If the dealer's hand is busted, it's a win (given that we've already checked for gambler hand bust)
        elif self.dealer.hand.status == 'Busted':
            self.add_activity('Outcome: WIN')
            self.pay_out_hand(hand, 'wager')
        
        # If neither gambler nor dealer hand is busted, compare totals to determine wins and losses.
        else:
            hand_total = hand.final_total()
            dealer_hand_total = self.dealer.hand.final_total()

            if hand_total > dealer_hand_total:
                self.add_activity('Outcome: WIN')
                self.pay_out_hand(hand, 'wager')
            elif hand_total == dealer_hand_total:
                self.add_activity('Outcome: PUSH')
                self.pay_out_hand(hand, 'push')
            else:
                self.add_activity('Outcome: LOSS', f"${hand.wager} hand wager lost.")

    def settle_up(self):
        """For each of the gambler's hands, settle wagers against the dealer's hand."""
        self.add_activity('\n--- Outcomes ---')
        for hand in self.gambler.hands:
            self.settle_hand(hand)

    def render_table(self):
        """Print out the hands of cards, if they've been dealt."""
        print(header('TABLE'))
        if self.dealer.hand:
            # Print the dealer's hand. If `hide_dealer` is True, don't factor in the dealer's buried card.
            num_dashes = len(self.dealer.name) + 6
            print(f"{'-'*num_dashes}\n   {self.dealer.name.upper()}   \n{'-'*num_dashes}\n")
            print(self.dealer.hand.pretty_format(hide=self.hide_dealer))

            # Print the gambler's hand(s)
            num_dashes = len(self.gambler.name) + 6
            print(f"\n{'-'*num_dashes}\n   {self.gambler.name.upper()}   \n{'-'*num_dashes}\n\nBankroll: ${self.gambler.bankroll}")
            for hand in self.gambler.hands:
                print(hand.pretty_format())
            print()
        else:
            print('No hands dealt yet.')

    def render_activity(self):
        """Print out the activity log for the current turn."""
        print(header('ACTIVITY'))
        for message in self.activity:
            print(message)

    def render_action(self):
        """Print out the action section that the user interacts with."""
        print(header('ACTION'))

    def render(self):
        """Print out the entire game (comprised of table, activity log, and user action) to the console."""
        clear()  # Clear previous rendering
        self.render_table()
        self.render_activity()
        self.render_action()

    def finalize_turn(self):
        # Print the outcome of the turn, showing the dealer.
        self.hide_dealer = False
        self.render()
        
        # Pause exectution until the user wants to proceed.
        input('Push ENTER to proceed => ')

        # Reset the activity log for the next turn
        self.activity = []

        # Discard both the gambler and the dealer's hands.
        self.discard_hands()

        # Reset hide_dealer
        self.hide_dealer = True

    def add_activity(self, *messages):
        """Add message(s) to the activity log. This triggers a re-render of the game."""
        # Add all messages
        for message in messages:
            self.activity.append(message)

        # Re-render the game
        self.render()

    def game_over(self):
        # Show game over message
        print(header('GAME OVER'))

        # Print a final message after the gambler is finished
        if self.gambler.auto_wager == 0:    
            action = f"{self.gambler.name} cashed out with bankroll: ${self.gambler.bankroll}."
            message = 'Thanks for playing!'
        else:
            action = f"{self.gambler.name} is out of money."
            message = 'Better luck next time!'

        # Calculate the gambler's winnings in total and as a percent change
        gross_winnings = self.gambler.gross_winnings()
        pct_winnings = self.gambler.pct_winnings()
        print(f"{action}\nWinnings: ${gross_winnings} ({pct_winnings}%)\n\n{message}\n")
