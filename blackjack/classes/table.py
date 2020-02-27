from blackjack.classes.player import Gambler, Player
from blackjack.exc import InsufficientBankrollError
from blackjack.utils import get_user_input, float_response, yes_no_response


class Table:

    all_ = []
    counter = 1

    def __init__(self):
        self.number = Table.counter
        
        Table.counter += 1
        Table.all_.append(self)

    def players(self):
        return [player for player in Player.all_ if player.table == self]

    def gamblers(self):
        return [player for player in self.players() if isinstance(player, Gambler)]

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
                
                # If they've entered a wager of $0, that means they've cashed out.
                if gambler.wager == 0:
                    # TODO: Cash them out, remove them from Table?
                    pass

    def play_round(self):

        # 1) Ask each Gambler if they would like to change their wager
        self.check_gambler_wagers()
        
        # 2) Deal Cards from the Shoe to each Player (including the Dealer)
