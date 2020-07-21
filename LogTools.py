class LogTools:
    def __init__(self):
        self.all_neighbour_addresses = set()
        self.last_neighbours_addresses = set()

    def log_neighbour(self, neighbour_address):
        self.all_neighbour_addresses.add(neighbour_address)

    def log_last_neighbours(self, last_neighbours_addresses):
        self.last_neighbours_addresses = last_neighbours_addresses