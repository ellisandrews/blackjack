from blackjack.classes.player import Gambler, Player
from blackjack.utils import get_user_input, parse_float_response, parse_yes_no_response


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
            response = get_user_input(f"{gambler.name}, change your wager or cash out (Bankroll: ${gambler.bankroll}; current wager: ${gambler.wager})? (y/n) => ", parse_yes_no_response)
            
            # If they want to make a change, make it
            if response == 'yes':

                # Move their current standing wager to their bankroll
                gambler.move_wager_to_bankroll()

                # Ask them to enter a new wager
                new_wager = get_user_input(f"Enter a new wager (Bankroll: ${gambler.bankroll}; enter $0 to cash out): $", parse_float_response)
                
                # TODO: Validate that they have sufficient bankroll to place the wager!!

                # If they entered a wager of $0, cash them out of the game. Otherwise update their wager
                if new_wager == 0:
                    # TODO!!!!!!!!!!
                    pass
                else:
                    gambler.set_new_wager(new_wager)

    def play_round(self):

        # 1) Ask each Gambler if they would like to change their wager
        self.check_gambler_wagers()
        
        # 2) Deal Cards from the Shoe to each Player (including the Dealer)


