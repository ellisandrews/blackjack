from blackjack.classes.hand import Hand
from blackjack.classes.player import Dealer, Gambler, Player
from blackjack.classes.shoe import Shoe
from blackjack.exc import InsufficientBankrollError
from blackjack.utils import get_user_input, float_response, yes_no_response


# TODO: Implement caching (at least per turn)
class Table:

    all_ = []
    counter = 1

    def __init__(self, shoe=None):
        self.shoe = shoe or Shoe()  # A Table is always associated with a single Shoe
        self.number = Table.counter

        Table.counter += 1
        Table.all_.append(self)

    def players(self):
        return [player for player in Player.all_ if player.table == self]

    def gamblers(self):
        return [player for player in self.players() if isinstance(player, Gambler)]

    def dealer(self):
        return next(player for player in self.players() if isinstance(player, Dealer))

    def check_gambler_wagers(self):
        
        for gambler in self.gamblers():
            
            print()

            # Ask if they want to cash out or change wager
            response = get_user_input(
                f"{gambler.name}, change your wager or cash out (Bankroll: ${gambler.bankroll}; current wager: ${gambler.wager})? (y/n) => ", 
                yes_no_response
            )
            
            # If they want to make a change, make it
            if response == 'yes':

                # Ask them to enter a new wager, validate the input, and set the new wager
                gambler.set_new_wager_from_input()
                
                # If they've entered a wager of $0, that means they've cashed out
                if gambler.wager == 0:
                    print(f"{gambler.name} cashed out with bankroll: ${gambler.bankroll}. Thanks for playing!")
                    gambler.table = None

    def deal(self):

        print()
        print("Dealing...")

        # Deal to all Players (the Dealer and all the Gamblers)
        for player in self.players():

            # Make a new Hand for the player. If it's a Gambler, their wager is applied to the Hand.
            if isinstance(player, Gambler):
                hand = Hand(player, player.wager)  
            else:
                hand = Hand(player)
            
            dealt_card_1, dealt_card_2 = self.shoe.deal_two_cards()  # Deal 2 Cards from the Shoe.
            dealt_card_1.hand, dealt_card_2.hand = hand, hand  # Assign the 2 Cards to the Player's Hand. 

    def gambler_turns(self):
        for gambler in self.gamblers():
            print()
            print(gambler)
            gambler.print_hands()

    def discard_hands(self):
        for player in self.players():
            player.discard_hands()

    def play_round(self):

        # 1) Ask each Gambler if they would like to change their wager
        self.check_gambler_wagers()
        
        # 2) Deal 2 Cards from the Shoe to each Player (including the Dealer)
        self.deal()

        # 3) Display the Dealer's up card
        self.dealer().print_up_card()

        # 4) Play each Gambler turn
        self.gambler_turns()
        print()

        # 5) Play the Dealer's turn

        # 6) Pay out wins / collect losses

        # 7) Reset all hands
        self.discard_hands()

