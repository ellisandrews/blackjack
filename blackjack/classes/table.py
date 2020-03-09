from blackjack.classes.hand import GamblerHand, Hand
from blackjack.classes.player import Dealer, Gambler, Player
from blackjack.classes.shoe import Shoe
from blackjack.exc import InsufficientBankrollError
from blackjack.utils import get_user_input, float_response, yes_no_response


class Table:

    all_ = []
    counter = 1

    def __init__(self, gambler, dealer=None, shoe=None):
        self.gambler = gambler
        self.dealer = dealer or Dealer()
        self.shoe = shoe or Shoe()
        self.number = Table.counter

        # Derived attribute for ease of gameplay
        self.players = [self.gambler, self.dealer]

        Table.counter += 1
        Table.all_.append(self)

    def check_gambler_wager(self):

        # Ask if the gambler wants to cash out or change their wager
        response = get_user_input(
            f"\n{self.gambler.name}, change your auto-wager or cash out (Bankroll: ${self.gambler.bankroll}; Auto-Wager: ${self.gambler.auto_wager})? (y/n) => ", 
            yes_no_response
        )
        
        # If they want to make a change, make it
        if response == 'yes':
            self.gambler.set_new_wager_from_input()

    def deal(self):

        print("\nDealing...\n")

        # Deal to the gambler and the dealer
        for player in self.players:

            # Make a new Hand for the player. If it's a Gambler, their wager is applied to the Hand.
            if isinstance(player, Gambler):
                hand = GamblerHand(player, player.auto_wager)  
            else:
                hand = Hand(player)
            
            dealt_card_1, dealt_card_2 = self.shoe.deal_two_cards()  # Deal 2 Cards from the Shoe.
            dealt_card_1.hand, dealt_card_2.hand = hand, hand  # Assign the 2 Cards to the Player's Hand. 

    def discard_hands(self):
        for player in self.players:
            player.discard_hands()

    def gambler_wants_even_money(self):
        return get_user_input("Take even money? (y/n) => ", yes_no_response)

    def play(self):

        print('\n--- New Turn ---')

        # Ask the Gambler if they would like to change their wager (or cash out).
        self.check_gambler_wager()
        
        # If they cash out, don't play the turn.
        # TODO: Print a message?
        if self.gambler.is_finished():
            return

        # Deal 2 Cards from the Shoe to each Player (the Gambler and Dealer).
        self.deal()

        # Display the Dealer's up card.
        self.dealer.print_up_card()

        # Check for blackjacks
        dealer_has_blackjack = self.dealer.hand().is_blackjack()
        gambler_has_blackjack = self.gambler.first_hand().is_blackjack()

        # Print if the gambler has blackjack. Don't reveal whether the dealer does yet.
        if gambler_has_blackjack:
            print(f"{self.gambler.name} has blackjack!")

        ### NEW CODE ###
        
        # Dealer can have blackjack (which would end the turn straight away) if they are showing a facecard or an ace.
        if self.dealer.is_showing_ace_or_face_card():
            
            # Insurance comes into play if the dealer's upcard is an ace
            if self.dealer.is_showing_ace():

                print('Dealer is showing an Ace.')

                # If the gambler has blackjack, they can either take even money or let it ride.
                if gambler_has_blackjack:

                    if self.gambler_wants_even_money() == 'yes':
                        self.gambler.first_hand().payout('wager', '1:1')  # gambler wins hand 1 to 1  
                        # TURN OVER
                    else:
                        if dealer_has_blackjack:
                            push
                        else:
                            gambler_wins_hand_3_to_2  
                            # TURN OVER
                else:
                    if gambler_wants_insurance:
                        
                        place_insurance_wager
                        
                        if dealear_has_blackjack:
                            gambler_wins_insurance_wager_2_to_1
                            gambler_loses_hand  
                            # TURN OVER
                        else:
                            gambler_loses_insurance_wager
                            play_hand

                    else:
                        if dealear_has_blackjack:
                            gambler_loses_hand
                            # TURN OVER
                        else:
                            play_hand

            # If the dealer's upcard is a 10, no insurance in play but need to check if the dealer has blackjack.
            else:
                if dealear_has_blackjack:

                    if gambler_has_blackjack:
                        push  # TURN OVER
                    else:
                        gambler_loses_hand
                        # TURN OVER

                # If dealer doesn't have blackjack
                else:
                    play_hand

        else:
            if gambler_has_blackjack:
                gambler_wins_hand_3_to_2
                # TURN OVER
            else:
                play_hand





        ### ORIGINAL CODE ###

        # # If the Dealer is showing an ace, ask the Gambler if they want insurance.
        # if self.dealer.up_card_is_ace():
            
        #     base_prompt = "Dealer up card is an Ace."

        #     # If the gambler has blackjack, give them the option to take even money.
        #     if gambler_has_black_jack:
        #         take_even_money = get_user_input(f"{base_prompt} Take even money? (y/n) => ", yes_no_response)
        #         # If they took even money, payout 1:1 and end their turn
        #         if take_even_money == 'yes':
        #             self.gambler.payout(self.gambler.first_hand().wager)  # TODO: Better way to payout a winning hand?
        #             return

        #     # If the gambler does not have blackjack, give them the option to take insurance equal to half their wager.
        #     else:
        #         wants_insurance = get_user_input(f"{base_prompt} Insurance? (y/n) => ", yes_no_response)
        #         if wants_insurance == 'yes':
        #             try:
        #                 # Take an additional bet out of the player's bankroll that is 1/2 of their wager.
        #                 self.gambler.buy_insurance_for_first_hand()
        #             except InsufficientBankrollError:
        #                 print("Insufficient bankroll to buy insurance!")


        #     if not dealer_has_black_jack:
        #         print("Dealer does NOT have blackjack. Any insurance wagers lost.")
        #         # TODO: Collect insurance wagers!

        # # If the dealer has blackjack, assess insurance and other wagers. The turn is over.
        # if dealer_has_black_jack:
        #     print("Dealer has blackjack.")

        #     # Payout successful insurance bet (if applicable)
        #     insurance_amount = self.gambler.first_hand().insurance
        #     if insurance_amount > 0:
        #         print("Insurance bet won! Paying out 2:1 and reclaiming wagered amount.")
        #         self.gambler.payout(insurance_amount * 3)

        #     # If the player has blackjack, it's a push and turn is over
        #     if gambler_has_black_jack:
        #         print("Hand is a push.")
        #         return
        #     # If the player does not have blackjack, take their money, and the turn is over.
        #     else:
        #         print(f"{self.gambler.name} lost the hand.")
        # else:
        #     # If the player has won a blackjack (i.e. dealer doesn't have blackjack and the didn't take even money) Pay 3:2, and the turn is over.
        #     if gambler_has_black_jack:
        #         print(f"{self.gambler.name} won hand with blackjack! Paying 3:2.")
        #         self.gambler.payout(self.gambler.first_hand().wager)

        # Play the Gambler's turn
        self.gambler.play_turn()

        # Play the Dealer's turn

        # Pay out wins / collect losses

        # Reset all hands
        self.discard_hands()

