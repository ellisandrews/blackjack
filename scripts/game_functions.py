
# TODO: Add Docstrings to these functions once they are finalized

def hit(deck, player):
    # Draw a card from the deck
    card = deck.select_card()
    # print card
    # Remove the card from the active deck and add it to the player's hand
    deck.remove_card(card)
    player.hand.append(card)


def deal_hands(deck, *args):
    # Deal 2 cards from the deck to each player object passed into *args
    for player in args:
        player.reset_hand()
        print "Dealing to {}...".format(player.name)
        hit(deck, player)
        hit(deck, player)
        player.print_hand()
        player.print_total()
        print ""


def hit_or_stand(deck, player):
    response = raw_input("Do you want to hit? (y/n) ").strip().lower()
    if response in ('y', 'yes'):
        hit(deck, player)
    else:
        print "Player stood."
        player.turn_over = True


def place_bet(player):
    # $5 minimum bet
    if player.bankroll < 5:
        print "You don't have enough money to play this hand."
        player.turn_over = True
        return

    while player.bet <= 5:
        try:
            bet = float(raw_input("How much would you like to bet ($5 minimum)? "))
            assert type(bet) == float, "Bet must be a numerical value, try again!"
            assert bet >= 5, "Must bet at least $5.00, try agian!"
            assert bet <= player.bankroll, "You don't have enough bankroll, try again!"
            player.bet = bet
        except AssertionError as e:
            print e
            continue
        except ValueError:
            print "Bet must be a numerical value, try again!"
            continue


def player_turn(deck, player):
    while not player.turn_over:
        hit_or_stand(deck, player)
        player.print_hand()
        player.print_total()
        print ""
