"""Script for playing an interactive Blackjack game with the command line."""

from argparse import ArgumentParser

from blackjack.configuration import get_interactive_configuration
from blackjack.display_utils import clear
from blackjack.game_setup import setup_game


if __name__ == '__main__':

    # Command line args
    parser = ArgumentParser()
    parser.add_argument('-d', '--default', help='Use the default game setup instead of manually configuring', action='store_true')
    args = parser.parse_args()

    # Clear the terminal screen.
    clear()

    # Load the game configuration (in this case, the 'interactive' configuration).
    configuration = get_interactive_configuration(args.default)

    # Set up the game using the loaded configuration.
    game = setup_game(configuration)

    # Play the game.
    game.play()
