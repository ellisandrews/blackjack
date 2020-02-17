# GAMEPLAY SCRIPT

from blackjack.classes.players import Player
from blackjack.utils import create_new_shuffled_deck, deal

# TODO: Nice printing whitespace (so it's easily readable)

# SETUP
print("\n$$$ Welcome to the blackjack table! $$$\n")

# TODO: Add back in user input lines below and vet the input
# player_name = input("Please enter a player name: ")
# initial_bankroll = float(input("Please enter a starting bankroll amount: $"))
# player = Player(player_name, initial_bankroll)

player = Player('Ellis', 100)
dealer = Player('Dealer', 0)

# TURN: Start coding one turn, and then can put in a loop or something

# Create a brand new shuffled deck of cards
deck = create_new_shuffled_deck()

# TODO: Add back in the wagering step and vet the input
# Ask the player to place a wager on the hand
# wager = float(input(f"\nPlese enter a wager for the hand (bankroll: ${player.bankroll}): $"))

wager = 10

# Subtract the wager from the player's bankroll
player.subtract_bankroll(wager)

# Deal cards to the player and the dealer
deal(deck, player, dealer)

# Display the dealer's first card to the player
dealer_up_card = dealer.hands[0].cards[0]
print(f"Dealer up card: {dealer_up_card}")

# Diplay both of the player's cards
print(f"Your hand(s): {player.hands}")

# Check whether the dealer is showing an ace. If so, offer insurance.
# TODO: Offer insurance to player and handle that logic.
if dealer_up_card.name == 'Ace':
    pass

# Check whether the dealer has blackjack
if dealer.hands[0].is_blackjack():
    print("Dealer has blackjack!")

# Check whether the player has blackjack
if player.hands[0].is_blackjack():
    print("Player has blackjack!")

player_low_total, player_high_total = player.hands[0].possible_totals()
print(f"Player totals: {player_low_total}, {player_high_total}")

# Check whether the player's hand is splittable, and ask if so.
# TODO: Figure out splitting logic.
if player.hands[0].is_splittable():
    print("Player's hand is splittable.")

# Figure out how to hit/split/double/stand
