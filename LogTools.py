import config

class LogTools:
    def __init__(self):
        self.all_neighbour_addresses = set()
        self.neighbours_access_times = dict()
        self.latest_neighbours_infos = dict()

    def log_neighbours_access_times(self, current_neighbours_addresses):
        for neighbour_address in current_neighbours_addresses:
            if neighbour_address in self.neighbours_access_times:
                self.neighbours_access_times[neighbour_address] += config.LOG_NEIGHBOURS_TIME_PERIOD
            else:
                self.neighbours_access_times[neighbour_address] = config.LOG_NEIGHBOURS_TIME_PERIOD

    def log_neighbour(self, neighbour_address, neighbour_neighbour_addresses):
        self.all_neighbour_addresses.add(neighbour_address)
        self.latest_neighbours_infos[neighbour_address] = config.LOG_NEIGHBOURS_TIME_PERIOD

    def log_remove_neighbour(self, neighbour_address):
        if neighbour_address in self.latest_neighbours_infos:
            del self.latest_neighbours_infos[neighbour_address]