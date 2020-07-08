"""Script to analyze how a strategy performs in repeated simulations of a set number of turns."""

from argparse import ArgumentParser

from blackjack.controllers.game_controller import GameController
from blackjack.models.dealer import Dealer
from blackjack.models.deck import Deck
from blackjack.models.gambler import Gambler
from blackjack.models.shoe import Shoe
from blackjack.strategies.default_static_strategy import DefaultStaticStrategy
from blackjack.utils import clear, header


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


def setup_new_game(bankroll, auto_wager, decks, turns):
    """Set up a new GameController instance to run a simulation of the game."""
    # Create core components of the game: A Gambler, a Dealer, and a Shoe of cards.
    gambler = Gambler('Gambler', bankroll=bankroll, auto_wager=auto_wager)
    dealer = Dealer()
    shoe = setup_shoe(decks)

    # Instantiate the appropriate strategy
    strategy = DefaultStaticStrategy()

    # Create the central controller of the game.
    return GameController(gambler, dealer, shoe, strategy, verbose=False, max_turns=turns)


if __name__ == '__main__':

    # TODO: Make these real CLI args
    bankroll = 10000
    auto_wager = 1
    decks = 6
    turns = 100
    games = 1000

    # TODO: Multiprocess the games?
    for _ in range(games):
        game = setup_new_game(bankroll, auto_wager, decks, turns)
        game.play()
        