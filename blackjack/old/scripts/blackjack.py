from game_classes import *
from game_functions import *


# =====================
#  GAMEPLAY EXECUTION
# =====================

# Initialize Player and Deck objects
Dealer = Player('Dealer', 0)
Player1 = Player('Ellis')

MyDeck = Deck()

# Make the player place their bet
place_bet(Player1)

print "{player}'s bet: {bet}".format(player=Player1.name, bet=Player1.bet)

# Deal out the first hand to the player and the dealer - can pass in more Player objects here if desired!
deal_hands(MyDeck, Player1, Dealer)

# Simulate a turn for Player1

player_turn(MyDeck, Player1)

# Next up, program the dealer to systematically hit or stand, then compare to see who wins!
