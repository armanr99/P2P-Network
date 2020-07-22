import os
import shutil
import config
import json

class LogTools:
    def __init__(self, host_address):
        self.host_address = host_address
        self.all_neighbour_addresses = set()
        self.neighbours_access_times = dict()
        self.latest_neighbours_neighbours = dict()
        self.received_packets_count = dict()
        self.sent_packets_count = dict()
        self.unidirectional_sent_addresses = set()
        self.unidirectional_received_addresses = set()
        self.result_path = config.RESULTS_DIRECTORY + "/" + self.host_address[0] + ":" + str(self.host_address[1]) + ".json"

    def log_neighbours_access_times(self, current_neighbours_addresses):
        for neighbour_address in current_neighbours_addresses:
            self.log_host_info_count(neighbour_address, self.neighbours_access_times, config.LOG_NEIGHBOURS_TIME_PERIOD)

    def log_neighbour(self, neighbour_address, neighbour_neighbour_addresses):
        self.all_neighbour_addresses.add(neighbour_address)
        self.latest_neighbours_neighbours[neighbour_address] = neighbour_neighbour_addresses

    def log_remove_neighbour(self, neighbour_address):
        if neighbour_address in self.latest_neighbours_neighbours:
            del self.latest_neighbours_neighbours[neighbour_address]

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
        result_object = self.get_result_object()
        self.write_json(self.result_path, result_object)
        
    def write_json(self, path, data):
        with open(path, "w", encoding="utf-8") as result_file:
            json.dump(data, result_file, ensure_ascii=False, indent=4)

    def get_neighbours_result_object(self, neighbour_addresses):
        return [{"address": neighbour_address[0], 
                 "port": neighbour_address[1]}
                 for neighbour_address in neighbour_addresses]

    def get_all_neighbours_result_object(self):
        return [{"address": neighbour_address[0], 
                 "port": neighbour_address[1],
                 "packetsReceivedCount": self.received_packets_count[neighbour_address],
                 "packetsSentCount": self.sent_packets_count[neighbour_address]}
                 for neighbour_address in self.all_neighbour_addresses]

    def get_availabilities_result_object(self):
        return [{"address": address_tuple[0],
                 "port": address_tuple[1],
                 "availability": total_time / config.SIMULATION_TIME} 
                 for address_tuple, total_time in self.neighbours_access_times.items()]
    
    def get_neighbours_topology_result_object(self):
        return [{"address": neighbour_address[0],
                 "port": neighbour_address[1],
                 "neighbours": self.get_neighbours_result_object(neighbour_neighbours)}
                 for neighbour_address, neighbour_neighbours in self.latest_neighbours_neighbours.items()]

    def get_unidirectional_result_object(self, unidrectional_hosts):
        unidrectional_hosts = unidrectional_hosts - set(self.latest_neighbours_neighbours.keys())
        return self.get_neighbours_result_object(unidrectional_hosts)

    def get_result_object(self):
        result_object = dict()
        result_object["allNeighbours"] = self.get_all_neighbours_result_object()
        result_object["lastNeighbours"] = self.get_neighbours_result_object(self.latest_neighbours_neighbours.keys())
        result_object["availabilities"] = self.get_availabilities_result_object()
        result_object["neighboursTopology"] = self.get_neighbours_topology_result_object()
        result_object["unidirectionalSentHosts"] = self.get_unidirectional_result_object(self.unidirectional_sent_addresses)
        result_object["unidirectionalReceivedHosts"] = self.get_unidirectional_result_object(self.unidirectional_received_addresses)
        return result_object