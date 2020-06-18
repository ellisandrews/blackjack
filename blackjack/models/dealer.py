class Dealer:

    def __init__(self, hand=None):
        self.name = 'Dealer'
        self.hand = hand

    def up_card(self):
        # Shortcut to the dealer's hand's up_card
        return self.hand.up_card()

    def is_showing_ace(self):
        return self.up_card().is_ace()

    def is_showing_face_card(self):
        return self.up_card().is_facecard()

    def play_turn(self, shoe):
        self.hand.play(shoe)

    def discard_hand(self):
        self.hand = None
