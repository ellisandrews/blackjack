class Dealer:

    def __init__(self, hand=None):
        self.name = 'Dealer'
        self.hand = hand

    def up_card(self):
        """Shortcut to the dealer's hand's up_card."""
        return self.hand.up_card()

    def is_showing_ace(self):
        """Check whether the dealer is showing an ace."""
        return self.up_card().is_ace()

    def is_showing_face_card(self):
        """Check whether the dealer is showing a face card."""
        return self.up_card().is_facecard()

    def discard_hand(self):
        """Reset the dealer's hand."""
        self.hand = None
