from blackjack.display_utils import header
from blackjack.strategies.user_input_strategy import UserInputStrategy
from blackjack.user_input import float_response, get_user_input, int_response


def get_interactive_configuration(default):
    """Get game configuration data for the interactive game mode."""
    if default:
        # Default values
        name = 'Gambler'
        bankroll = 1000.0
        auto_wager = 100.0
        number_of_decks = 3
    else:
        # User-entered values
        print(header('GAME SETUP'))
        name = input("Enter a player name => ")
        bankroll = get_user_input("Enter a bankroll amount => $", float_response)
        auto_wager = get_user_input("Enter an auto-wager amount => $", float_response)
        number_of_decks = get_user_input("Enter the number of decks to use => ", int_response)

    # Serialize and return configuration
    return {
        'gambler': {
            'name': name,
            'bankroll': bankroll,
            'auto_wager': auto_wager
        },
        'shoe': {
            'number_of_decks': number_of_decks
        },
        'gameplay': {
            'strategy': UserInputStrategy,
            'verbose': True,
            'max_turns': None
        }
    }


def get_simulation_configuration(bankroll, auto_wager, number_of_decks, strategy, max_turns):
    """Get game configuration data for the simulation game mode."""
    return {
        'gambler': {
            'name': 'Gambler',
            'bankroll': bankroll,
            'auto_wager': auto_wager
        },
        'shoe': {
            'number_of_decks': number_of_decks
        },
        'gameplay': {
            'strategy': strategy,
            'verbose': False,
            'max_turns': max_turns
        }
    }
