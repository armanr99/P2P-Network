import threading
import time
import config
import socket
import pickle

from P2PPacket import P2PPacket

class P2PHost:
    def __init__(self, host_address):
        self.host_address = host_address
        self.is_finished = False
        self.bidirectional_host_addresses = set()
        self.unidirectional_received_host_addresses = set()
        self.unidirectional_sent_host_addresses = set()
        self.hosts_last_receive_time = dict()
        self.init_hosts_last_receive_time()

    def init_hosts_last_receive_time(self):
        for host_address in config.HOST_ADDRESSES:
            self.hosts_last_receive_time[host_address] = config.UNDEFINED
            
    def start(self):
        threading.Thread(target=self.send_bidrectional_packets).start()

    def send_bidrectional_packets(self):
        while not self.is_finished:
            for bidirectional_host_address in self.bidirectional_host_addresses:
                hello_packet = self.get_hello_packet(bidirectional_host_address)
                self.send_udp_packet(bidirectional_host_address, hello_packet)
            time.sleep(config.SEND_TIME)

    def get_hello_packet(self, host_address):
        return P2PPacket(self.host_address, config.HELLO_MESSAGE_TYPE, 
            self.bidirectional_host_addresses, time.time(), self.hosts_last_receive_time[host_address])

    def send_udp_packet(self, host_address, data):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(pickle.dumps(data), (host_address[0], host_address[1]))
        sock.close()