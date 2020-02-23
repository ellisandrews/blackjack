class Deck:

    all_ = []
    counter = 1

    def __init__(self):
        self.number = Deck.counter
        
        Deck.counter += 1
        Deck.all_.append(self)

    def __str__(self):
        return f"{self.__class__.__name__} {self.number}"

    def __repr__(self):
        return self.__str__()
