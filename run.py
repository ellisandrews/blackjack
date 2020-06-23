from blackjack.controllers.game_controller import GameController
from blackjack.models.dealer import Dealer
from blackjack.models.deck import Deck
from blackjack.models.gambler import Gambler
from blackjack.models.shoe import Shoe
from blackjack.user_input import get_user_input, float_response, int_response
from blackjack.utils import clear, header


def get_setup_input():

    # Gambler setup data
    name = input("Please enter a player name => ")
    bankroll = get_user_input("Please enter a bankroll amount => $", float_response)

    # Shoe setup data
    number_of_decks = get_user_input("Please enter the number of decks to use => ", int_response)

    # Return the data to be used to set up the game
    return {
        'gambler': {
            'name': name,
            'bankroll': bankroll,
            'auto_wager': bankroll / 10  # Start them off with a 10% auto-wager
        },
        'shoe': {
            'number_of_decks': number_of_decks
        }
    }


def setup_shoe(number_of_decks):

    # Instantiate a new Shoe.
    shoe = Shoe()

    # Create the specified number of decks (populated with standard 52 Cards each)
    for _ in range(number_of_decks):
        deck = Deck(shoe=shoe)
        deck.populate()

    # Load the Shoe's card pile with Cards from all the Decks shuffled together.
    shoe.reset_card_pile()

    return shoe


def setup_game(from_user_input=True):

    # Ask the user for game setup data, or use a default schema
    if from_user_input:
        setup_data = get_setup_input()
    else:
        setup_data = {
            'gambler': {
                'name': 'Player 1',
                'bankroll': 100,
                'auto_wager': 10
            },
            'shoe': {
                'number_of_decks': 3
            }
        }

    # Extract values from setup_data. Note that this dict could grow and be stored/loaded from a
    # different source, so doing this to keep configuration flexible.
    name = setup_data['gambler']['name']
    bankroll = setup_data['gambler']['bankroll']
    auto_wager = setup_data['gambler']['auto_wager']
    number_of_decks = setup_data['shoe']['number_of_decks']

    # Create core components of the game: A Gambler, a Dealer, and a Shoe of cards.
    gambler = Gambler(name, bankroll=bankroll, auto_wager=auto_wager)
    dealer = Dealer()
    shoe = setup_shoe(number_of_decks)

    # Create the central controller of the game.
    return GameController(gambler, dealer, shoe)


if __name__ == '__main__':

    # Clear the terminal screen.
    clear()

    # Show welcome message
    print(header('WELCOME TO THE BLACKJACK TABLE'))

    # Set up the game.
    game = setup_game(from_user_input=False)  # Delete `from_user_input` arg for final version!

    # Run the game loop.
    game.play()

    # Show game over message
    print(header('GAME OVER'))

    # Print a final message after the gambler is finished
    if game.gambler.auto_wager == 0:    
        print(f"\n{game.gambler.name} cashed out with bankroll: ${game.gambler.bankroll}. Thanks for playing!")
    else:
        print(f"\n{game.gambler.name} is out of money. Better luck next time!")
