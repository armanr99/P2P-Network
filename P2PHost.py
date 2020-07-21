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
        self.bidirectional_host_addresses = set()
        self.hosts_last_receive_time = dict()
        self.init_hosts_last_receive_time()
        self.udp_tools = UDPTools(host_address)

    def init_hosts_last_receive_time(self):
        for host_address in config.HOST_ADDRESSES:
            self.hosts_last_receive_time[host_address] = config.UNDEFINED
            
    def start(self):
        threading.Thread(target=self.send_bidrectional_packets_run).start()
        threading.Thread(target=self.find_neighbours_run).start()
        threading.Thread(target=self.receive_packet_run).start()

    def send_bidrectional_packets_run(self):
        while not self.is_finished:
            for bidirectional_host_address in self.bidirectional_host_addresses:
                self.send_hello_packet(bidirectional_host_address)

            time.sleep(config.SEND_TIME)

    def find_neighbours_run(self):
        while not self.is_finished:
            if len(self.bidirectional_host_addresses) < config.NUMBER_OF_NEIGHBOURS:
                    random_host_address = random.choice(tuple(config.HOST_ADDRESSES - self.bidirectional_host_addresses))
                    self.send_hello_packet(random_host_address)

            time.sleep(config.CHECK_NEIGHBOUR_TIME)

    def receive_packet_run(self):
        while not self.is_finished:
            received_data = self.udp_tools.receive_udp_packet()
            p2p_packet = pickle.loads(received_data)
            
            if len(self.bidirectional_host_addresses) < config.NUMBER_OF_NEIGHBOURS:
                if p2p_packet.host_address in self.bidirectional_host_addresses:
                    break
                else:
                    self.bidirectional_host_addresses.add(p2p_packet.host)
                    if self.host_address not in p2p_packet.bidirectional_host_address:
                        self.send_hello_packet(p2p_packet.host)

    def get_hello_packet(self, host_address):
        return P2PPacket(self.host_address, config.HELLO_MESSAGE_TYPE, 
            self.bidirectional_host_addresses, time.time(), self.hosts_last_receive_time[host_address])

    def send_hello_packet(self, host_address):
        hello_packet = self.get_hello_packet(host_address)
        self.udp_tools.send_udp_packet(host_address, pickle.dumps(hello_packet))
                    