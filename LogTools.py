import config

class LogTools:
    def __init__(self):
        self.all_neighbour_addresses = set()
        self.neighbours_access_times = dict()
        self.latest_neighbours_infos = dict()
        self.unidirectional_sent_addresses = set()
        self.unidirectional_received_addresses = set()

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

    def add_unidirectional_sent_address_log(self, unidirectional_received_address):
        self.unidirectional_sent_addresses.add(unidirectional_received_address)

    def add_unidirectional_received_address_log(self, unidirectional_received_address):
        self.unidirectional_received_addresses.add(unidirectional_received_address)