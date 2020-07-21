import threading
import time
import random
import config
import pickle

from P2PPacket import P2PPacket
from UDPTools import UDPTools

class P2PHost:
    def __init__(self, host_address):
        self.host_address = host_address
        self.is_finished = False
        self.neighbour_addresses = set()
        self.hosts_last_receive_time = dict()
        self.init_hosts_last_receive_time()
        self.udp_tools = UDPTools(host_address)

    def init_hosts_last_receive_time(self):
        for host_address in config.HOST_ADDRESSES:
            self.hosts_last_receive_time[host_address] = config.UNDEFINED
            
    def start(self):
        threading.Thread(target=self.send_neighbours_packets_run).start()
        threading.Thread(target=self.find_neighbours_run).start()
        threading.Thread(target=self.receive_packet_run).start()
        threading.Thread(target=self.remove_old_neighbours_run).start()

    def send_neighbours_packets_run(self):
        while not self.is_finished:
            for neighbour_address in self.neighbour_addresses:
                self.send_hello_packet(neighbour_address)

            time.sleep(config.SEND_PERIOD)

    def find_neighbours_run(self):
        while not self.is_finished:
            if len(self.neighbour_addresses) < len(config.HOST_ADDRESSES):
                    random_host_address = random.choice(tuple(config.HOST_ADDRESSES - self.neighbour_addresses))
                    self.send_hello_packet(random_host_address)

            time.sleep(config.FIND_NEIGHBOURS_PERIOD)

    def receive_packet_run(self):
        while not self.is_finished:
            received_data = self.udp_tools.receive_udp_packet()
            p2p_packet = pickle.loads(received_data)
            self.hosts_last_receive_time[p2p_packet.host_address] = time.time()
            
            if len(self.neighbour_addresses) < len(config.HOST_ADDRESSES):
                if p2p_packet.host_address not in self.neighbour_addresses:
                    self.neighbour_addresses.add(p2p_packet.host_address)
                    if self.host_address not in p2p_packet.neighbour_addresses:
                        self.send_hello_packet(p2p_packet.host_address)

    def remove_old_neighbours_run(self):
        while not self.is_finished:
            for neighbour_address in self.neighbour_addresses:
                if (time.time() - self.hosts_last_receive_time[neighbour_address]) >= config.REMOVE_NEIGHBOUR_TIME:
                    self.neighbour_addresses.remove(neighbour_address)
        
        time.sleep(config.REMOVE_OLD_NEIGHBOURS_PERIOD)

    def get_hello_packet(self, host_address):
        return P2PPacket(self.host_address, config.HELLO_MESSAGE_TYPE, 
            self.neighbour_addresses, time.time(), self.hosts_last_receive_time[host_address])

    def send_hello_packet(self, host_address):
        hello_packet = self.get_hello_packet(host_address)
        self.udp_tools.send_udp_packet(host_address, pickle.dumps(hello_packet))
                    