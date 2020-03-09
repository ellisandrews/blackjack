from collections import OrderedDict

from blackjack.classes.deck import Deck
from blackjack.classes.player import Dealer, Gambler
from blackjack.classes.shoe import Shoe
from blackjack.classes.table import Table
from blackjack.utils import get_user_input, float_response, int_response


def setup_table():

    # TODO: Should they always start with a default amount? Or allow to enter here?
    name = input("Please enter a player name => ")
    bankroll = get_user_input("Please enter a bankroll amount => $", float_response)

    # Create the Gambler, and ask them to set an initial wager
    gambler = Gambler(name, bankroll=bankroll)
    gambler.set_new_auto_wager_from_input()

    # Create the Table for the Gambler. It will autotmatically create a Dealer and a Shoe for itself.
    table = Table(gambler)

    # Create decks associated with the Table's Shoe
    number_of_decks = get_user_input("Please enter the number of decks to use (integer) => ", int_response)
    for _ in range(number_of_decks):
        deck = Deck(shoe=table.shoe)  # Create the Deck, associate with the Shoe
        deck.populate()               # Populate the Deck with cards

    # Pre-pop the shoe with shuffled cards from the created decks
    table.shoe.reset_card_pile()

    # Return the fully set up table
    return table


if __name__ == '__main__':

    print('♠️  ♥️  ♣️  ♦️   WELCOME TO THE BLACKJACK TABLE!  ♦️  ♣️  ♥️  ♠️')
    
    print()
    print('------------ Game Setup  ------------')
    print()

    table = setup_table()

    print()
    print('---------- Setup Complete! ----------')
    print()
    print()
    print('-------- Beginning Gameplay ---------')
    print()

    # Play rounds until the gambler has cashed out or is out of money
    while not table.gambler.is_finished():
        table.play()

    # Print a final message after the gambler is finished
    if table.gambler.wager == 0:    
        print(f"{table.gambler.name} cashed out with bankroll: ${table.gambler.bankroll}. Thanks for playing!")
    else:
        print(f"{table.gambler.name} is out of money. Better luck next time!")

    print()
    print('------------- Game Over -------------')
