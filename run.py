from blackjack.models.deck import Deck
from blackjack.models.player import Dealer, Gambler
from blackjack.models.shoe import Shoe
from blackjack.models.table import Table
from blackjack.user_input import get_user_input, float_response, int_response
from blackjack.utils import header


def setup_gambler():

    # Gambler setup data
    name = input("Please enter a player name => ")
    bankroll = get_user_input("Please enter a bankroll amount => $", float_response)

    # Create the Gambler, and ask them to set an initial auto-wager amount.
    gambler = Gambler(name, bankroll=bankroll)
    gambler.set_new_auto_wager_from_input()

    return gambler


def setup_shoe():

    # Instantiate a new Shoe.
    shoe = Shoe()

    # Ask user how many Decks of Cards they want to play with.
    number_of_decks = get_user_input("Please enter the number of decks to use => ", int_response)

    # Create the specified number of decks (populated with standard 52 Cards each)
    for _ in range(number_of_decks):
        deck = Deck(shoe=shoe)
        deck.populate()

    # Load the Shoe's card pile with Cards from all the Decks shuffled together.
    shoe.reset_card_pile()

    return shoe


def setup_table():

    # Create core components of the game: A Gambler, a Dealer, and a Shoe of cards.
    gambler = setup_gambler()
    dealer = Dealer()
    shoe = setup_shoe()

    # Create the blackjack Table. This is the central controller of the game.
    return Table(gambler, dealer, shoe)


if __name__ == '__main__':

    print(header('WELCOME TO THE BLACKJACK TABLE'))

    # Set up the game.
    table = setup_table()

    # Play the game until the Gambler has cashed out or is out of money.
    table.play()

    # Print a final message after the gambler is finished
    if table.gambler.auto_wager == 0:    
        print(f"\n{table.gambler.name} cashed out with bankroll: ${table.gambler.bankroll}. Thanks for playing!")
    else:
        print(f"\n{table.gambler.name} is out of money. Better luck next time!")

    print(header('GAME OVER'))
