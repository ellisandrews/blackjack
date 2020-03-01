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
            
        # Return whether or not they cashed out
        return self.gambler.is_finished()

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

        # 1) Ask the Gambler if they would like to change their wager. If they cash out, don't play the turn.
        cashed_out = self.check_gambler_wager()
        if cashed_out:
            return

        # 2) Deal 2 Cards from the Shoe to each Player (Gambler and Dealer)
        self.deal()

        # 3) Display the Dealer's up card
        self.dealer.print_up_card()

        # 4) Play the Gambler's turn
        self.gambler.play_turn()

        # 5) Play the Dealer's turn

        # 6) Pay out wins / collect losses

        # 7) Reset all hands
        self.discard_hands()

