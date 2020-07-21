import threading
import time
import random
import config
import pickle

from P2PPacket import P2PPacket
from UDPTools import UDPTools
from LogTools import LogTools

class P2PHost:
    def __init__(self, host_id, host_address):
        self.host_id = host_id
        self.host_address = host_address
        self.is_finished = False
        self.is_paused = False
        self.neighbour_addresses = set()
        self.hosts_last_receive_time = dict()
        self.init_hosts_last_receive_time()
        self.udp_tools = UDPTools(host_address)
        self.lock = threading.Lock()
        self.log_tools = LogTools()

    def init_hosts_last_receive_time(self):
        for host_address in config.HOST_ADDRESSES:
            self.hosts_last_receive_time[host_address] = config.UNDEFINED
            
    def start(self):
        threading.Thread(target=self.send_neighbours_packets_run).start()
        threading.Thread(target=self.find_neighbours_run).start()
        threading.Thread(target=self.receive_packet_run).start()
        threading.Thread(target=self.remove_old_neighbours_run).start()

    def stop(self):
        self.is_finished = True
        self.udp_tools.stop()
        self.log_tools.log_last_neighbours(self.neighbour_addresses)

    def pause(self):
        self.is_paused = True

    def resume(self):
        self.is_paused = False

    def send_neighbours_packets_run(self):
        while not self.is_finished:
            if not self.is_paused:
                self.lock.acquire()

                for neighbour_address in self.neighbour_addresses:
                    self.send_hello_packet(neighbour_address)

                self.lock.release()

            time.sleep(config.SEND_PERIOD)

    def find_neighbours_run(self):
        while not self.is_finished:
            if not self.is_paused:
                self.lock.acquire()

                if len(self.neighbour_addresses) < config.MAX_NUMBER_OF_HOSTS:
                        random_host_address = random.choice(tuple(config.HOST_ADDRESSES - self.neighbour_addresses))
                        self.send_hello_packet(random_host_address)
                
                self.lock.release()

            time.sleep(config.FIND_NEIGHBOURS_PERIOD)

    def receive_packet_run(self):
        while not self.is_finished:
            if not self.is_paused:
                received_data = self.udp_tools.receive_udp_packet()
                p2p_packet = pickle.loads(received_data)
                self.hosts_last_receive_time[p2p_packet.host_address] = time.time()

                is_lost_packet = (random.randint(0, 100) <= config.PACKET_LOSS_PROBABILITY)
                if is_lost_packet:
                    continue
                
                self.lock.acquire()

                if len(self.neighbour_addresses) < config.MAX_NUMBER_OF_HOSTS:
                    if p2p_packet.host_address not in self.neighbour_addresses:
                        self.neighbour_addresses.add(p2p_packet.host_address)
                        self.log_tools.log_neighbour(p2p_packet.host_address)
                        if self.host_address not in p2p_packet.neighbour_addresses:
                            self.send_hello_packet(p2p_packet.host_address)

                self.lock.release()

    def remove_old_neighbours_run(self):
        while not self.is_finished:
            if not self.is_paused:
                self.lock.acquire()

                for neighbour_address in list(self.neighbour_addresses):
                    if (time.time() - self.hosts_last_receive_time[neighbour_address]) >= config.REMOVE_NEIGHBOUR_TIME:
                        self.neighbour_addresses.remove(neighbour_address)
                
                self.lock.release()
                
            time.sleep(config.REMOVE_OLD_NEIGHBOURS_PERIOD)
        

    def get_hello_packet(self, host_address):
        return P2PPacket(self.host_id, self.host_address, config.HELLO_MESSAGE_TYPE, 
            self.neighbour_addresses, time.time(), self.hosts_last_receive_time[host_address])

    def send_hello_packet(self, host_address):
        hello_packet = self.get_hello_packet(host_address)
        self.udp_tools.send_udp_packet(host_address, pickle.dumps(hello_packet))
                    