from blackjack.classes.hand import Hand
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
            f"\n{self.gambler.name}, change your wager or cash out (Bankroll: ${self.gambler.bankroll}; current wager: ${self.gambler.wager})? (y/n) => ", 
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
                hand = Hand(player, player.wager)  
            else:
                hand = Hand(player)
            
            dealt_card_1, dealt_card_2 = self.shoe.deal_two_cards()  # Deal 2 Cards from the Shoe.
            dealt_card_1.hand, dealt_card_2.hand = hand, hand  # Assign the 2 Cards to the Player's Hand. 

    def discard_hands(self):
        for player in self.players:
            player.discard_hands()

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
        dealer_has_black_jack = self.dealer.hand().is_blackjack()
        gambler_has_black_jack = self.gambler.first_hand().is_blackjack()

        # Print if the gambler has blackjack. Don't reveal whether the dealer does yet.
        if gambler_has_black_jack:
            print(f"{self.gambler.name} has blackjack!")

        # If the Dealer is showing an ace, ask the Gambler if they want insurance.
        if self.dealer.up_card_is_ace():
            
            base_prompt = "Dealer up card is an Ace."

            # If the gambler has blackjack, give them the option to take even money.
            if gambler_has_black_jack:
                take_even_money = get_user_input(f"{base_prompt} Take even money? (y/n) => ", yes_no_response)
                # If they took even money, payout 1:1 and end their turn
                if take_even_money == 'yes':
                    self.gambler.payout(self.gambler.first_hand().wager)  # TODO: Better way to payout a winning hand?
                    return

            # If the gambler does not have blackjack, give them the option to take insurance equal to half their wager.
            else:
                wants_insurance = get_user_input(f"{base_prompt} Insurance? (y/n) => ", yes_no_response)
                if wants_insurance == 'yes':
                    try:
                        # Take an additional bet out of the player's bankroll that is 1/2 of their wager.
                        self.gambler.buy_insurance_for_first_hand()
                    except InsufficientBankrollError:
                        print("Insufficient bankroll to buy insurance!")
            
        # If the dealer has blackjack,


        # If the dealer has blackjack, assess insurancea and other wagers. The turn is over.
        if dealer_has_black_jack:
            
            # Payout successful insurance bet (if applicable)
            insurance_amount = self.gambler.first_hand().insurance
            if insurance_amount > 0:
                print("Insurance bet won! Paying out 2:1 and reclaiming wagered amount.")
                self.gambler.payout(insurance_amount * 3)

            # If the player has blackjack, it's a push and turn is over


            # If the player does not have blackjack, take their money, and the turn is over.

        else:
            print("Dealer does NOT have blackjack. Insurance wagers lost.")

        # If we've gotten here, the player has won a legitmate blackjack. Pay 3:2, and the turn is over.
        if gambler_has_black_jack:
            pass

        # Play the Gambler's turn
        self.gambler.play_turn()

        # Play the Dealer's turn

        # Pay out wins / collect losses

        # Reset all hands
        self.discard_hands()

