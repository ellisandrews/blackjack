# GAMEPLAY SCRIPT

from blackjack.classes.players import Player
from blackjack.utils import create_new_shuffled_deck, deal

# TODO: Nice printing whitespace (so it's easily readable)

# ----- SETUP ----- #
print("\n$$$ WELCOME TO THE BLACKJACK TABLE! $$$\n")

# TODO: Add back in user input lines below and vet the input
# player_name = input("Please enter a player name: ")
# initial_bankroll = float(input("Please enter a starting bankroll amount: $"))
# player = Player(player_name, initial_bankroll)

player = Player('Ellis', 100)
dealer = Player('Dealer', 0)

# ----- TURN ----- #
# Start coding one turn, and then can put in a loop or something.

# TODO: Turn this into a GameManager class or something?

standing_wager = 0


def is_affirmative_response(response):
    """Check whether user's keyboard response is a 'yes'."""
    if response.lower() in ('y', 'yes'):
        return True
    else:
        return False


def place_wager():
    """Ask whether the player wants to change their standing bet"""
    global standing_wager
    change_wager = input(f"Change wager (Wager: ${standing_wager}, Bankroll: ${player.bankroll})? (y/n): ")
    if is_affirmative_response(change_wager):
        player.add_bankroll(standing_wager)  # Add the standing_wager back to the player's bankroll
        new_standing_wager = float(input(f"Enter new wager amount (Bankroll: ${player.bankroll}): $"))
        # TODO: Vet wager
        player.subtract_bankroll(new_standing_wager)
        standing_wager = new_standing_wager


def play_turn():

    print("\nNew turn.")
    global standing_wager
    
    # Create a brand new shuffled deck of cards
    deck = create_new_shuffled_deck()

    # Allow the player to place a wager on the hand
    place_wager()

    # Deal cards to the player and the dealer
    deal(deck, [player, dealer])

    # Assign the player's wager to the hand
    player.hands[0].wager = standing_wager

    # Display the dealer's first card to the player
    dealer_up_card = dealer.hands[0].cards[0]
    print(f"Dealer up card: {dealer_up_card} -- ({dealer_up_card.value if dealer_up_card.name != 'Ace' else '1 or 11'})")

    # Diplay both of the player's cards
    print("Player's hand(s):")
    player.print_hands()

    # Check whether the player or dealer has blackjack. Don't display whether dealer has it yet!
    player_has_black_jack = player.hands[0].is_blackjack()
    dealer_has_black_jack = dealer.hands[0].is_blackjack()
    if player_has_black_jack:
        print("Player has blackjack!")

    # Check whether the dealer is showing an ace. If so, offer insurance.
    #   1) If the player has blackjack, they can choose to take even money (pays 1:1)
    #   2) Otherwise, the player can place a separate insurance bet that the dealer has blackjack (pays 2:1).
    #      Insurance is typically half the player's original bet, so let's just enforce that.
    if dealer_up_card.name == 'Ace':
        
        if player_has_black_jack:
            take_even_money = input("Take even money? (y/n): ")
            if take_even_money.lower() in ('y', 'yes'):
                player.add_bankroll(standing_wager)  # Pay even money, turn is over.
                return
            else:
                if dealer_has_black_jack:
                    return  # Push
        else:
            insurance = input("Insurance? (y/n): ")
            if insurance.lower() in ('y', 'yes'):
                player.subtract_bankroll(standing_wager/2)
                if dealer_has_black_jack:
                    player.add_bankroll(standing_wager/2*3)  # Pays 2:1
                    return

    if dealer_has_black_jack:
        print("Dealer has blackjack!")
        player.subtract_bankroll(standing_wager)
        return

    # Check whether the player's hand is splittable, and ask if so.
    # TODO: Figure out splitting logic.
    # if player.hands[0].is_splittable():
    #     print("Player's hand is splittable.")

    # Figure out how to hit/split/double/stand
    
    # Reset the hands
    player.reset_hands()
    dealer.reset_hands()
    print()

# Play the first turn without asking the player.
play_turn()

# Then keep playing turns until the player wants to quit.
while is_affirmative_response(input('Play another turn? (y/n) ')):
    play_turn()
