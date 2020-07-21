class LogTools:
    def __init__(self):
        self.all_neighbour_addresses = set()

    def log_neighbour(self, neighbour_address):
        self.all_neighbour_addresses.add(neighbour_address)