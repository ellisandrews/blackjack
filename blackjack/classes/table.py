class Table:

    all_ = []
    counter = 1

    def __init__(self):
        self.number = Table.counter
        
        Table.counter += 1
        Table.all_.append(self)

    def players(self):
        pass

    def shoe(self):
        pass
