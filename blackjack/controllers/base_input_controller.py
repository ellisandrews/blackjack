from functools import partial

from blackjack.user_input import choice_response, float_response, get_user_input, yes_no_response


# TODO: Make this an abstract base class that forces methods to be implemented
class BaseInputController:

    @staticmethod
    def check_gambler_wager(gambler):
        # Ask if the gambler wants to cash out or change their auto-wager
        return get_user_input(
            f"Change your auto-wager or cash out? (Bankroll: ${gambler.bankroll}; Auto-Wager: ${gambler.auto_wager}) (y/n) => ", 
            yes_no_response
        )
   
    @staticmethod
    def get_new_auto_wager(gambler):
        """Get a new auto-wager amount."""
        return get_user_input(
            f"Please enter an auto-wager amount (Bankroll: ${gambler.bankroll}; enter $0 to cash out): $",
            float_response
        )

    # NOTE: Dealer up card only relevant for strategy input (a real user can just see it)
    @staticmethod
    def get_hand_action(hand, options, dealer_upcard):

        # Formatted options to display to the user
        display_options = [f"{option} ({abbreviation})" for abbreviation, option in options.items()]

        # Ask what the user would like to do, given their options
        response = get_user_input(
            f"[ Hand {hand.hand_number} ] What would you like to do? [ {' , '.join(display_options)} ] => ",
            partial(choice_response, choices=options.keys())
        )

        # Return the user's selection ('Hit', 'Stand', etc.)
        return options[response]

    @staticmethod
    def wants_even_money():
        """Get a yes/no response for whether a user wants to take even money for a blackjack when facing an Ace."""
        return get_user_input("Take even money? (y/n) => ", yes_no_response)

    @staticmethod
    def wants_insurance():
        """Get a yes/no response for whether a user wants to make an insurance bet when facing an Ace."""
        return get_user_input("Insurance? (y/n) => ", yes_no_response)
