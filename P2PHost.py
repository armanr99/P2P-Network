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
        self.is_paused = False
        self.neighbour_addresses = set()
        self.hosts_last_receive_time = dict()
        self.init_hosts_last_receive_time()
        self.udp_tools = UDPTools(host_address)
        self.neighbour_addresses_lock = threading.Lock()

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

    def pause(self):
        self.is_paused = True

    def resume(self):
        self.is_paused = False

    def get_neighbour_addresses(self):
        self.neighbour_addresses_lock.acquire()
        return self.neighbour_addresses

    def send_neighbours_packets_run(self):
        while not self.is_finished:
            if not self.is_paused:
                neighbour_addresses = self.get_neighbour_addresses()
                print(len(neighbour_addresses))
                for neighbour_address in neighbour_addresses:
                    self.send_hello_packet(neighbour_address)

                self.neighbour_addresses_lock.release()

            time.sleep(config.SEND_PERIOD)

    def find_neighbours_run(self):
        while not self.is_finished:
            if not self.is_paused:
                neighbour_addresses = self.get_neighbour_addresses()

                if len(neighbour_addresses) < config.MAX_NUMBER_OF_HOSTS:
                        random_host_address = random.choice(tuple(config.HOST_ADDRESSES - neighbour_addresses))
                        self.send_hello_packet(random_host_address)
                
                self.neighbour_addresses_lock.release()

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
                
                neighbour_addresses = self.get_neighbour_addresses()

                if len(neighbour_addresses) < config.MAX_NUMBER_OF_HOSTS:
                    if p2p_packet.host_address not in neighbour_addresses:
                        neighbour_addresses.add(p2p_packet.host_address)
                        if self.host_address not in p2p_packet.neighbour_addresses:
                            self.send_hello_packet(p2p_packet.host_address)

                self.neighbour_addresses_lock.release()

    def remove_old_neighbours_run(self):
        while not self.is_finished:
            if not self.is_paused:
                neighbour_addresses = self.get_neighbour_addresses()

                for neighbour_address in neighbour_addresses:
                    if (time.time() - self.hosts_last_receive_time[neighbour_address]) >= config.REMOVE_NEIGHBOUR_TIME:
                        neighbour_addresses.remove(neighbour_address)
                
                self.neighbour_addresses_lock.release()
                
            time.sleep(config.REMOVE_OLD_NEIGHBOURS_PERIOD)
        

    def get_hello_packet(self, host_address):
        return P2PPacket(self.host_address, config.HELLO_MESSAGE_TYPE, 
            self.neighbour_addresses, time.time(), self.hosts_last_receive_time[host_address])

    def send_hello_packet(self, host_address):
        hello_packet = self.get_hello_packet(host_address)
        self.udp_tools.send_udp_packet(host_address, pickle.dumps(hello_packet))
                    