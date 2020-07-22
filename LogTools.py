import os
import shutil
import config
import json

class LogTools:
    def __init__(self, host_address):
        self.host_address = host_address
        self.all_neighbour_addresses = set()
        self.neighbours_access_times = dict()
        self.latest_neighbours_infos = dict()
        self.received_packets_count = dict()
        self.sent_packets_count = dict()
        self.unidirectional_sent_addresses = set()
        self.unidirectional_received_addresses = set()

    def log_neighbours_access_times(self, current_neighbours_addresses):
        for neighbour_address in current_neighbours_addresses:
            self.log_host_info_count(neighbour_address, self.neighbours_access_times, config.LOG_NEIGHBOURS_TIME_PERIOD)

    def log_neighbour(self, neighbour_address, neighbour_neighbour_addresses):
        self.all_neighbour_addresses.add(neighbour_address)
        self.latest_neighbours_infos[neighbour_address] = list(neighbour_neighbour_addresses)

    def log_remove_neighbour(self, neighbour_address):
        if neighbour_address in self.latest_neighbours_infos:
            del self.latest_neighbours_infos[neighbour_address]

    def log_send_packet(self, neighbour_address):
        self.log_host_info_count(neighbour_address, self.sent_packets_count, 1)

    def log_receive_packet(self, neighbour_address):
        self.log_host_info_count(neighbour_address, self.received_packets_count, 1)

    def log_host_info_count(self, neighbour_address, count_list, amount):
        if neighbour_address not in count_list:
            count_list[neighbour_address] = amount
        else:
            count_list[neighbour_address] += amount

    def log_sent_packet(self, received_packet_address, neighbour_addresses):
        self.log_host_info_count(received_packet_address, self.sent_packets_count, 1)
        self.unidirectional_sent_addresses.add(received_packet_address)

    def log_received_packet(self, sent_packet_address, neighbour_addresses):
        self.log_host_info_count(sent_packet_address, self.received_packets_count, 1)
        self.unidirectional_received_addresses.add(sent_packet_address)

    def write_results(self):
        self.create_host_directory()
        self.write_all_neighbours()
        self.write_last_neighbours()
        self.write_hosts_availability()
        self.write_last_neighbours_neighbours()
        self.write_unidirectional_sent_packets()
        self.write_unidirectional_received_packets()

    def create_host_directory(self):
        host_directory_path = self.get_host_directory_path()

        if os.path.isdir(host_directory_path):
            shutil.rmtree(host_directory_path)

        os.mkdir(host_directory_path)
        
    def get_host_directory_path(self):
        return (config.RESULTS_DIRECTORY + "/" + self.host_address[0] + ":" + str(self.host_address[1]))

    def write_json(self, path, data):
        with open(path, "w", encoding="utf-8") as result_file:
            json.dump(data, result_file, ensure_ascii=False, indent=4)

    def write_all_neighbours(self):
        all_neighbours_result_path = self.get_host_directory_path() + "/" + "1-AllNeighbours.json"
        self.write_json(all_neighbours_result_path, list(self.all_neighbour_addresses))

    def write_last_neighbours(self):
        last_neighbours_result_path = self.get_host_directory_path() + "/" + "2-LastNeighbours.json"
        self.write_json(last_neighbours_result_path, list(self.latest_neighbours_infos.keys()))
    
    def write_hosts_availability(self):
        neighbour_availabilities_result_path = self.get_host_directory_path() + "/" + "3-Availabilities.json"
        neighbour_availabilities = {key: value / config.SIMULATION_TIME for key, value in self.neighbours_access_times.items()}
        neighbour_availabilities = self.get_remaped_dict(neighbour_availabilities, "host", "availability")
        self.write_json(neighbour_availabilities_result_path, neighbour_availabilities)

    def write_last_neighbours_neighbours(self):
        last_neighbours_neighbours_result_path = self.get_host_directory_path() + "/" + "4-LastNeighbourNeighbours.json"
        last_neighbours_neighbours = self.get_remaped_dict(self.latest_neighbours_infos, "host", "neighbours")
        self.write_json(last_neighbours_neighbours_result_path, last_neighbours_neighbours)

    def write_unidirectional_sent_packets(self):
        self.unidirectional_sent_addresses = self.unidirectional_sent_addresses - set(self.latest_neighbours_infos.keys())
        unidirectional_sent_neighbours_result_path = self.get_host_directory_path() + "/" + "4-UnidirectionalSentNeighbours.json"
        self.write_json(unidirectional_sent_neighbours_result_path, list(self.unidirectional_sent_addresses))

    def write_unidirectional_received_packets(self):
        self.unidirectional_received_addresses = self.unidirectional_received_addresses - set(self.latest_neighbours_infos.keys())
        unidirectional_received_neighbours_result_path = self.get_host_directory_path() + "/" + "4-UnidirectionalReceivedNeighbours.json"
        self.write_json(unidirectional_received_neighbours_result_path, list(self.unidirectional_received_addresses))

    def get_remaped_dict(self, mapping, key, value):
        return [{str(key):k, str(value): v} for k, v in mapping.items()]
