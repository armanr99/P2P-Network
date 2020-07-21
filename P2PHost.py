import threading
import time
import config
import socket
import pickle

from P2PPacket import P2PPacket

class P2PHost:
    def __init__(self, host_port):
        self.host_port = host_port
        self.is_finished = False
        self.bidirectional_host_ports = set()
        self.unidirectional_received_host_ports = set()
        self.unidirectional_sent_host_ports = set()
        self.hosts_last_receive_time = dict()
        self.init_hosts_last_receive_time()

    def init_hosts_last_receive_time(self):
        for host_port in config.HOST_PORTS:
            self.hosts_last_receive_time[host_port] = config.UNDEFINED
            
    def start(self):
        threading.Thread(target=self.send_bidrectional_packets).start()

    def send_bidrectional_packets(self):
        while not self.is_finished:
            for bidirectional_host_port in self.bidirectional_host_ports:
                hello_packet = self.get_hello_packet(bidirectional_host_port)
                self.send_udp_packet(bidirectional_host_port, hello_packet)
            time.sleep(config.SEND_TIME)

    def get_hello_packet(self, host_port):
        return P2PPacket(config.HOST_IP, self.host_port, config.HELLO_MESSAGE_TYPE, 
            self.bidirectional_host_ports, time.time(), self.hosts_last_receive_time[host_port])

    def send_udp_packet(self, host_port, data):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(pickle.dumps(data), (config.HOST_IP, host_port))
        sock.close()