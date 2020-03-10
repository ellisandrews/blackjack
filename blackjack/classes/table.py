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

        # Ask if the gambler wants to cash out or change their auto-wager
        response = get_user_input(
            f"\n{self.gambler.name}, change your auto-wager or cash out (Bankroll: ${self.gambler.bankroll}; Auto-Wager: ${self.gambler.auto_wager})? (y/n) => ", 
            yes_no_response
        )
        
        # If they want to make a change, make it
        if response == 'yes':
            self.gambler.set_new_auto_wager_from_input()

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

    @staticmethod
    def gambler_wants_even_money():
        return get_user_input("Take even money? (y/n) => ", yes_no_response)

    @staticmethod
    def gambler_wants_insurance():
        return get_user_input("Insurance? (y/n) => ", yes_no_response)

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

        # Display the Gambler's hand
        self.gambler.print_hands()

        print()

        # Check if the gambler has blackjack
        gambler_has_blackjack = self.gambler.first_hand().is_blackjack()
        if gambler_has_blackjack:
            print(f"{self.gambler.name} has BLACKJACK!")

        # Dealer can only have blackjack (which ends the turn) if they are showing a face card (value=10) or an ace.
        if self.dealer.is_showing_ace() or self.dealer.is_showing_face_card():
            
            # Check if the dealer has blackjack, but don't display it to the gambler yet.
            dealer_has_blackjack = self.dealer.hand().is_blackjack()

            # Insurance comes into play if the dealer's upcard is an ace
            if self.dealer.is_showing_ace():

                print('Dealer is showing an Ace.')

                # If the gambler has blackjack, they can either take even money or let it ride.
                if gambler_has_blackjack:

                    if self.gambler_wants_even_money() == 'yes':
                        print(f"{self.gambler.name} wins even money.")
                        self.gambler.first_hand().payout('wager', '1:1') 
                        print('TURN OVER')  # TURN OVER
                    else:
                        if dealer_has_blackjack:
                            print('Dealer has BLACKJACK. Hand is a push.')
                            self.gambler.first_hand().payout('push')
                        else:
                            print(f"Dealer does not have BLACKJACK. {self.gambler.name} wins 3:2.")
                            self.gambler.first_hand().payout('wager', '3:2') 
                            print('TURN OVER')  # TURN OVER
                
                # If the gambler does not have blackjack, they can buy insurance.
                else:
                    if self.gambler_wants_insurance() == 'yes':
                        
                        # Insurnace is a side bet that is half their wager, and pays 2:1 if dealer has blackjack.
                        self.gambler.place_insurance_bet()
                        
                        if dealer_has_blackjack:
                            print(f"Dealer has BLACKJACK. {self.gambler.name}'s insurnace wager wins 2:1 but hand wager loses.")
                            self.gambler.first_hand().payout('insurance', '2:1')
                            print('TURN OVER')  # TURN OVER
                        else:
                            print(f"Dealer does not have BLACKJACK. {self.gambler.name}'s insurance wager loses.")
                            # TODO:!!! Play out the hand
                            # play_hand()
                            print('playing hand...')

                    # If they do not place an insurance bet, they lose if the dealer has blackjack. Otherwise, hand continues.
                    else:
                        if dealer_has_blackjack:
                            print(f"Dealer has BLACKJACK. {self.gambler.name} loses the hand.")
                            print('TURN OVER')  # TURN OVER
                        else:
                            print('Dealer does not have BLACKJACK.')
                            # TODO:!!! Play out the hand
                            # play_hand()
                            print('playing hand...')

            # If the dealer's upcard is a face card, insurance is not in play but need to check if the dealer has blackjack.
            else:
                
                print('Checking if the dealer has BLACKJACK...')

                # If the dealer has blackjack, it's a push if the player also has blackjack. Otherwise, the player loses.
                if dealer_has_blackjack:

                    if gambler_has_blackjack:
                        print('Dealer has BLACKJACK. Hand is a push.')
                        self.gambler.first_hand().payout('push')  
                        print('TURN OVER')  # TURN OVER
                    else:
                        print(f"Dealer has BLACKJACK. {self.gambler.name} loses the hand.")
                        print('TURN OVER')  # TURN OVER

                # If dealer doesn't have blackjack, continue with playing the hand.
                else:
                    print('Dealer does not have BLACKJACK.')
                    # TODO:!!! Play out the hand
                    # play_hand()
                    print('playing hand...')

        # If the dealer's upcard is not an ace or a face card, they cannot have blackjack.
        # If the player has blackjack here, payout 3:2 and the hand is over. Otherwise, continue with playing the hand.
        else:
            if gambler_has_blackjack:
                print(f"{self.gambler.name} wins 3:2.")
                self.gambler.first_hand().payout('wager', '3:2') 
                print('TURN OVER')  # TURN OVER
            else:
                # TODO:!!! Play out the hand
                # play_hand()
                print('playing hand...')

        # Play the Gambler's turn
        # self.gambler.play_turn()

        # Play the Dealer's turn

        # Pay out wins / collect losses

        # Reset all hands
        self.discard_hands()

