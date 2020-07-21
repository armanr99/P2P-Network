import threading
import time
import config

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
        pass