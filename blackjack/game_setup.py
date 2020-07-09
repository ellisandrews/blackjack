
from blackjack.controllers.game_controller import GameController
from blackjack.models.dealer import Dealer
from blackjack.models.gambler import Gambler
from blackjack.models.shoe import Shoe


def setup_game(config):
    """Set up the GameController class that runs the game from a configuration dictionary."""
    # Extract values from configuration. Note that this dict could grow and be stored/loaded from a
    # different source, so doing this to keep configuration flexible.
    name = config['gambler']['name']
    bankroll = config['gambler']['bankroll']
    auto_wager = config['gambler']['auto_wager']
    number_of_decks = config['shoe']['number_of_decks']
    strategy = config['gameplay']['strategy']
    verbose = config['gameplay']['verbose']
    max_turns = config['gameplay']['max_turns']

    # Create core components of the game: A Gambler, a Dealer, and a Shoe of cards.
    gambler = Gambler(name, bankroll=bankroll, auto_wager=auto_wager)
    dealer = Dealer()
    shoe = Shoe(number_of_decks)

    # Instantiate and return the central controller of the game.
    return GameController(gambler, dealer, shoe, strategy(), verbose=verbose, max_turns=max_turns)
