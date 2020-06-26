from argparse import ArgumentParser

from blackjack.controllers.game_controller import GameController
from blackjack.models.dealer import Dealer
from blackjack.models.deck import Deck
from blackjack.models.gambler import Gambler
from blackjack.models.shoe import Shoe
from blackjack.strategies.default_static_strategy import DefaultStaticStrategy
from blackjack.strategies.user_input_strategy import UserInputStrategy
from blackjack.user_input import get_user_input, float_response, int_response
from blackjack.utils import clear, header


def get_setup_from_input(mode):
    """Get game setup data from user input at the command line."""
    # Header
    print(header('GAME SETUP'))

    # Gambler setup data
    name = input("Enter a player name => ")
    bankroll = get_user_input("Enter a bankroll amount => $", float_response)
    auto_wager = get_user_input("Enter an auto-wager amount => $", float_response)

    # Shoe setup data
    number_of_decks = get_user_input("Enter the number of decks to use => ", int_response)

    # Required data
    setup_data = {
        'gambler': {
            'name': name,
            'bankroll': bankroll,
            'auto_wager': auto_wager
        },
        'shoe': {
            'number_of_decks': number_of_decks
        }
    }
    
    # For non-interactive games, specify a maximum number of turns to simulate.
    if mode != 'interactive':
        setup_data['max_turns'] = get_user_input("Enter the maximum number of turns to play => ", int_response)
    
    # Return the data to be used to set up the game
    return setup_data


def get_default_setup(mode):
    """Get default game setup data."""
    # Required data
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

    # For non-interactive games, specifiy a maximum number of turns to simulate.
    if mode != 'interactive':
        setup_data['max_turns'] = 50

    return setup_data


def setup_shoe(number_of_decks):
    """Create the Shoe with specified number of decks of cards all shuffled together."""
    # Instantiate a new Shoe.
    shoe = Shoe()

    # Create the specified number of decks (populated with standard 52 Cards each).
    for _ in range(number_of_decks):
        deck = Deck(shoe=shoe)
        deck.populate()

    # Load the Shoe's card pile with Cards from all the Decks shuffled together.
    shoe.reset_card_pile()

    # Return the set up Shoe
    return shoe


def setup_game(mode, verbose, default_setup):
    """Set up the GameController class that runs the game."""
    # Use the default game setup or prompt the user to enter setup data 
    if default_setup:
        setup_data = get_default_setup(mode)
    else:
        setup_data = get_setup_from_input(mode)

    # Extract values from setup_data. Note that this dict could grow and be stored/loaded from a
    # different source, so doing this to keep configuration flexible.
    name = setup_data['gambler']['name']
    bankroll = setup_data['gambler']['bankroll']
    auto_wager = setup_data['gambler']['auto_wager']
    number_of_decks = setup_data['shoe']['number_of_decks']
    max_turns = setup_data.get('max_turns')

    # Create core components of the game: A Gambler, a Dealer, and a Shoe of cards.
    gambler = Gambler(name, bankroll=bankroll, auto_wager=auto_wager)
    dealer = Dealer()
    shoe = setup_shoe(number_of_decks)

    # Instantiate the appropriate strategy
    if mode == 'interactive':
        strategy = UserInputStrategy()
    elif mode == 'simulated':
        strategy = DefaultStaticStrategy()
    else:
        raise ValueError(f"Unsupported game mode: {mode}")

    # Create the central controller of the game.
    return GameController(gambler, dealer, shoe, strategy, verbose, max_turns)


if __name__ == '__main__':

    # Command line args
    parser = ArgumentParser()
    parser.add_argument('-m', '--mode', help='Game mode to play', required=True, choices=['interactive', 'simulated'])
    parser.add_argument('-v', '--verbose', help='Print game output (required for interactive mode)', action='store_true')
    parser.add_argument('-d', '--default', help='Use the default game setup instead of manually configuring', action='store_true')
    # parser.add_argument('-s', '--strategy', help='Game strategy to use (if not in interactive mode)')
    args = parser.parse_args()

    # Validate the command line args passed in
    if args.mode == 'interactive' and not args.verbose:
        raise parser.error('Must specify --verbose if running with --mode interactive')

    # Clear the terminal screen.
    clear()

    # Set up the game.
    game = setup_game(mode=args.mode, verbose=args.verbose, default_setup=args.default)

    # Run the game loop.
    game.play()
