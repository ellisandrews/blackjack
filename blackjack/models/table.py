from blackjack.exc import InsufficientBankrollError
from blackjack.models.hand import DealerHand, GamblerHand
from blackjack.user_input import get_user_input, float_response, yes_no_response
from blackjack.utils import clear


class Table:

    all_ = []
    counter = 1

    def __init__(self, gambler, dealer, shoe):
        self.gambler = gambler
        self.dealer = dealer
        self.shoe = shoe
        self.number = Table.counter

        Table.counter += 1
        Table.all_.append(self)

    def check_gambler_wager(self):

        # Check if the gambler still has sufficient bankroll to place the auto-wager
        if self.gambler.can_place_auto_wager():

            # Ask if the gambler wants to cash out or change their auto-wager
            response = get_user_input(
                f"{self.gambler.name}, change your auto-wager or cash out? (Bankroll: ${self.gambler.bankroll}; Auto-Wager: ${self.gambler.auto_wager}) (y/n) => ", 
                yes_no_response
            )
            
            # If they want to make a change, make it
            if response == 'yes':
                self.gambler.set_new_auto_wager_from_input()

        # If they don't have sufficient bankroll to place auto-wager, force them to set a new one.
        else:
            print(f"Insufficient bankroll to place current auto-wager (Bankroll: ${self.gambler.bankroll}; Auto-Wager: ${self.gambler.auto_wager})")
            self.gambler.set_new_auto_wager_from_input()

    def deal(self):
        # Create the two hands to be dealt to
        gambler_hand = GamblerHand(self.gambler)
        dealer_hand = DealerHand(self.dealer)

        # Place the gambler's auto-wager on the hand. We've already vetted that they have sufficient bankroll.
        self.gambler.place_auto_wager()

        # Deal like they do a casinos -- one card to each player at a time, starting with the gambler.
        print()
        print("Dealing...")
        print()
        dealt_card_1, dealt_card_2, dealt_card_3, dealt_card_4 = self.shoe.deal_n_cards(4)
        dealt_card_1.hand, dealt_card_3.hand = gambler_hand, gambler_hand
        dealt_card_2.hand, dealt_card_4.hand = dealer_hand, dealer_hand
 
    def discard_hands(self):
        self.gambler.discard_hands()
        self.dealer.discard_hands()

    def play_pre_turn(self):
        """
        Carry out pre-turn flow for blackjacks, insurance, etc.
        TODO: Refactor into smaller pieces!
        """
        # Check if the gambler has blackjack
        gambler_has_blackjack = self.gambler.first_hand().is_blackjack()
        if gambler_has_blackjack:
            print(f"{self.gambler.name} HAS BLACKJACK!")

        # Dealer can only have blackjack (which ends the turn) if they are showing a face card (value=10) or an ace.
        if self.dealer.is_showing_ace() or self.dealer.is_showing_face_card():
            
            # Check if the dealer has blackjack, but don't display it to the gambler yet.
            dealer_has_blackjack = self.dealer.hand().is_blackjack()

            # Insurance comes into play if the dealer's upcard is an ace
            if self.dealer.is_showing_ace():

                print('Dealer is showing an Ace.')

                # If the gambler has blackjack, they can either take even money or let it ride.
                if gambler_has_blackjack:

                    if self.gambler.wants_even_money() == 'yes':
                        print(f"{self.gambler.name} wins even money.")
                        self.gambler.first_hand().payout('wager', '1:1') 
                    else:
                        if dealer_has_blackjack:
                            print('Dealer HAS BLACKJACK. Hand is a push.')
                            self.gambler.first_hand().payout('push')
                        else:
                            print(f"Dealer DOES NOT HAVE BLACKJACK. {self.gambler.name} wins 3:2.")
                            self.gambler.first_hand().payout('wager', '3:2') 

                    # The turn is over no matter what if the gambler has blackjack
                    return 'turn over'

                # If the gambler does not have blackjack they can buy insurance.
                else:
                    # Gambler must have sufficient bankroll to place an insurance bet.
                    gambler_can_afford_insurance = self.gambler.can_place_insurance_wager()

                    if gambler_can_afford_insurance and self.gambler.wants_insurance() == 'yes':

                        # Insurnace is a side bet that is half their wager, and pays 2:1 if dealer has blackjack.
                        self.gambler.place_insurance_wager()            

                        # The turn is over if the dealer has blackjack. Otherwise, continue on to playing the hand.
                        if dealer_has_blackjack:
                            print(f"Dealer HAS BLACKJACK. {self.gambler.name}'s insurnace wager wins 2:1 but hand wager loses.")
                            self.gambler.first_hand().payout('insurance', '2:1')
                            return 'turn over'
                        else:
                            print(f"Dealer DOES NOT HAVE BLACKJACK. {self.gambler.name}'s insurance wager loses.")
                            return 'play turn'

                    # If the gambler does not (or cannot) place an insurance bet, they lose if the dealer has blackjack. Otherwise, hand continues.
                    else:
                        if not gambler_can_afford_insurance:
                            print('Insufficient bankroll to place insurance wager.')

                        if dealer_has_blackjack:
                            print(f"Dealer HAS BLACKJACK. {self.gambler.name} loses the hand.")
                            return 'turn over'
                        else:
                            print('Dealer DOES NOT HAVE BLACKJACK.')
                            return 'play turn'

            # If the dealer's upcard is a face card, insurance is not in play but need to check if the dealer has blackjack.
            else:
                
                print('Checking if the dealer HAS BLACKJACK...')

                # If the dealer has blackjack, it's a push if the player also has blackjack. Otherwise, the player loses.
                if dealer_has_blackjack:

                    if gambler_has_blackjack:
                        print('Dealer HAS BLACKJACK. Hand is a push.')
                        self.gambler.first_hand().payout('push')  
                    else:
                        print(f"Dealer HAS BLACKJACK. {self.gambler.name} loses the hand.")
                        
                    # The turn is over no matter what if the dealer has blackjack
                    return 'turn over'

                # If dealer doesn't have blackjack, continue with playing the hand.
                else:
                    print('Dealer DOES NOT HAVE BLACKJACK.')
                    return 'play turn'

        # If the dealer's upcard is not an ace or a face card, they cannot have blackjack.
        # If the player has blackjack here, payout 3:2 and the hand is over. Otherwise, continue with playing the hand.
        else:
            if gambler_has_blackjack:
                print(f"{self.gambler.name} wins 3:2.")
                self.gambler.first_hand().payout('wager', '3:2') 
                return 'turn over'
            else:
                return 'play turn'

    def print(self, hide_dealer=False):
        
        # Print the dealer. If `hide_dealer` is True, don't factor in the dealer's buried card.
        num_dashes = len(self.dealer.name) + 6
        print(f"\n{'-'*12}\n   {self.dealer.name.upper()}   \n{'-'*12}\n")
        self.dealer.hand().print(hide=hide_dealer)

        # Print the gambler
        num_dashes = len(self.gambler.name) + 6
        print(f"\n{'-'*num_dashes}\n   {self.gambler.name.upper()}   \n{'-'*num_dashes}")
        for i, hand in enumerate(self.gambler.hands()):
            hand.print(hand_number=i+1)

    def play(self):

        try:
            clear()
            print('\n--- New Turn ---\n')

            # Vet the gambler's auto-wager against their bankroll, and ask if they would like to change their wager or cash out.
            self.check_gambler_wager()
            
            # If they cash out, don't play the turn.
            if self.gambler.is_finished():
                return

            # Deal 2 cards from the shoe to the gambler's and the dealer's hands. Place the gambler's auto-wager on the hand.
            self.deal()

            # Print the table, hiding the dealer's buried card from the gambler
            self.print(hide_dealer=True)

            print()

            # Carry out pre-turn flow (for blackjacks, insurance, etc). If either player had blackjack, there is no turn to play.
            result = self.play_pre_turn()

            print()

            if result == 'turn over':
                return

            # Play the Gambler's turn
            self.gambler.play_turn()

            print()

            # Play the Dealer's turn

            # Pay out wins / collect losses

        finally:
            # Always reset all hands
            self.discard_hands()
