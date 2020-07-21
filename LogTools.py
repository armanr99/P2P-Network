import config

class LogTools:
    def __init__(self):
        self.all_neighbour_addresses = set()
        self.last_neighbours_addresses = set()
        self.neighbours_access_times = dict()

    def log_neighbour(self, neighbour_address):
        self.all_neighbour_addresses.add(neighbour_address)

    def log_last_neighbours(self, last_neighbours_addresses):
        self.last_neighbours_addresses = last_neighbours_addresses

    def log_neighbours_access_times(self, current_neighbours_addresses):
        for neighbour_address in current_neighbours_addresses:
            if neighbour_address in self.neighbours_access_times:
                self.neighbours_access_times[neighbour_address] += config.LOG_NEIGHBOURS_TIME_PERIOD
            else:
                self.neighbours_access_times[neighbour_address] = config.LOG_NEIGHBOURS_TIME_PERIOD