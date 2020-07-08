"""Script for analyzing how a strategy performs in repeated simulations of a set number of turns."""

from argparse import ArgumentParser

from blackjack.configuration import get_simulation_configuration
from blackjack.display_utils import clear
from blackjack.game_setup import setup_game
from blackjack.strategies.default_static_strategy import DefaultStaticStrategy


STRATEGY_MAP = {
    'default': DefaultStaticStrategy
}


if __name__ == '__main__':

    # Command line args
    parser = ArgumentParser()
    parser.add_argument('-a', '--auto-wager', help='Initial Gambler auto-wager', type=float, default=100.0)
    parser.add_argument('-b', '--bankroll', help='Initial Gambler bankroll', type=float, default=1000.0)
    parser.add_argument('-d', '--decks', help='Number of decks to play with', type=int, default=3)
    parser.add_argument('-g', '--games', help='Number of games to simulate', type=int, default=100)
    parser.add_argument('-s', '--strategy', help='Name of the gameplay strategy to use', default='default', choices=STRATEGY_MAP.keys())
    parser.add_argument('-t', '--turns', help='Max number of turns to play per game', type=int, default=100)
    args = parser.parse_args()

    # Clear the terminal screen.
    clear()

    # Get the requested gameplay strategy
    strategy = STRATEGY_MAP[args.strategy]

    # Load the game configuration (in this case, the 'simulation' configuration).
    configuration = get_simulation_configuration(args.bankroll, args.auto_wager, args.decks, strategy, args.turns)

    # TODO: Multiprocess the games?
    for _ in range(args.games):
        game = setup_game(configuration)
        game.play()
