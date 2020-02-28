from collections import OrderedDict

from blackjack.classes.deck import Deck
from blackjack.classes.player import Dealer, Gambler
from blackjack.classes.shoe import Shoe
from blackjack.classes.table import Table
from blackjack.utils import get_user_input, float_response, int_response


def setup_table(num_decks):

    # Create a Table. It will autotmatically create a Shoe for itself.
    table = Table()

    # Create `num_decks` decks associated with the Table's Shoe
    for _ in range(num_decks):
        deck = Deck(shoe=table.shoe)  # Create the Deck, associate with the Shoe
        deck.populate()               # Populate the Deck with cards

    # Setup the Dealer
    Dealer(table=table)

    # Pre-pop the shoe with shuffled cards from the created decks
    table.shoe.reset_card_pile()

    return table


def get_player_information(num_players):

    player_information = []

    counter = 1
    for _ in range(num_players):

        print(f"Player {counter}")

        # Get the player's name
        name = input("  Please enter a player name => ")
        
        # TODO: Should they always start with a default amount? Or allow to enter here?
        # Get the player's bankroll
        bankroll = get_user_input("  Please enter a bankroll amount => $", float_response)

        player_information.append({'name': name, 'bankroll': bankroll})
        counter += 1
        print()

    return player_information


def setup_players(player_information, game_table):

    # Setup the game players (aka Gamblers)
    for data in player_information:
        name = data['name']
        bankroll = data['bankroll']
        Gambler(name, bankroll=bankroll, table=game_table)


if __name__ == '__main__':

    print('♠️  ♥️  ♣️  ♦️   WELCOME TO THE BLACKJACK TABLE!  ♦️  ♣️  ♥️  ♠️')
    
    print()
    print('----------- Game Setup  -----------')
    print()

    # Ask the user for the number of players and decks
    number_of_players = get_user_input("Please enter the number of players (integer) => ", int_response)
    number_of_decks = get_user_input("Please enter the number of decks to use (integer) => ", int_response)
    
    print()
    print("Setting up the table...")
    table = setup_table(number_of_decks)

    print()
    print('---------- Player Setup  ----------')
    print()

    player_info = get_player_information(number_of_players)

    print("Setting up players...")
    setup_players(player_info, table)

    print()
    print('---------- Setup Complete! ----------')

    while table.gamblers():
        table.play_round()
    
    print()
    print('------------- Game Over -------------')
