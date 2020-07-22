import threading
import time
import random
import config
import pickle

from P2PPacket import P2PPacket
from UDPTools import UDPTools
from LogTools import LogTools

class P2PHost:
    def __init__(self, host_id, host_address, other_host_addresses):
        self.host_id = host_id
        self.host_address = host_address
        self.other_host_addresses = other_host_addresses
        self.is_finished = False
        self.is_paused = False
        self.neighbour_addresses = set()
        self.hosts_last_receive_time = dict()
        self.init_hosts_last_receive_time()
        self.lock = threading.Lock()
        self.udp_tools = UDPTools(host_address)
        self.log_tools = LogTools(host_address)

    def init_hosts_last_receive_time(self):
        for host_address in self.other_host_addresses:
            self.hosts_last_receive_time[host_address] = config.UNDEFINED
            
    def start(self):
        threading.Thread(target=self.send_neighbours_packets_run).start()
        threading.Thread(target=self.find_new_neighbours_run).start()
        threading.Thread(target=self.receive_packet_run).start()
        threading.Thread(target=self.remove_old_neighbours_run).start()
        threading.Thread(target=self.gather_log_info_run).start()

    def stop(self):
        self.is_finished = True
        self.udp_tools.stop()
        self.log_tools.write_results()

    def pause(self):
        self.is_paused = True

    def resume(self):
        self.is_paused = False

    def send_neighbours_packets_run(self):
        while not self.is_finished:
            if not self.is_paused:
                self.lock.acquire()
                self.send_neighbours_packets()
                self.lock.release()

            time.sleep(config.SEND_PERIOD)

    def send_neighbours_packets(self):
        for neighbour_address in self.neighbour_addresses:
                    self.send_hello_packet(neighbour_address)
                    self.log_tools.log_sent_packet(neighbour_address, self.neighbour_addresses)

    def find_new_neighbours_run(self):
        while not self.is_finished:
            if not self.is_paused:
                self.lock.acquire()
                self.find_new_neighbour()  
                self.lock.release()
                
            time.sleep(config.FIND_NEIGHBOURS_PERIOD)

    def find_new_neighbour(self):
        if len(self.neighbour_addresses) < config.MAX_NUMBER_OF_HOSTS:
            random_host_address = random.choice(tuple(self.other_host_addresses - self.neighbour_addresses))
            self.send_hello_packet(random_host_address)
            self.log_tools.log_sent_packet(random_host_address, self.neighbour_addresses)

    def receive_packet_run(self):
        while not self.is_finished:
            if not self.is_paused:
                try:
                    received_packet = self.receive_packet()
                    self.lock.acquire()
                    self.handle_received_packet(received_packet)
                    self.lock.release()
                except:
                    continue

    def receive_packet(self):
        received_data = self.udp_tools.receive_udp_packet()
        received_packet = pickle.loads(received_data)

        self.hosts_last_receive_time[received_packet.host_address] = time.time()
        self.log_tools.log_received_packet(received_packet.host_address, self.neighbour_addresses)
        
        if (random.randint(0, 100) <= config.PACKET_LOSS_PROBABILITY):
            raise Exception("Receiving packet is lost")
        else:
            return received_packet

    def handle_received_packet(self, received_packet):
        if len(self.neighbour_addresses) < config.MAX_NUMBER_OF_HOSTS:
            if received_packet.host_address not in self.neighbour_addresses:
                self.neighbour_addresses.add(received_packet.host_address)
                self.log_tools.log_neighbour(received_packet.host_address, received_packet.neighbour_addresses)
                if self.host_address not in received_packet.neighbour_addresses:
                    self.send_hello_packet(received_packet.host_address)
                    self.log_tools.log_sent_packet(received_packet.host_address, self.neighbour_addresses)

    def remove_old_neighbours_run(self):
        while not self.is_finished:
            if not self.is_paused:
                self.lock.acquire()
                self.remove_old_neighbours()                
                self.lock.release()
                
            time.sleep(config.REMOVE_OLD_NEIGHBOURS_PERIOD)
    
    def remove_old_neighbours(self):
        for neighbour_address in list(self.neighbour_addresses):
            if (time.time() - self.hosts_last_receive_time[neighbour_address]) >= config.REMOVE_NEIGHBOUR_TIME:
                self.neighbour_addresses.remove(neighbour_address)
                self.log_tools.log_remove_neighbour(neighbour_address)

    def gather_log_info_run(self):
        time_passed = 0
        while time_passed <= config.SIMULATION_TIME:
            self.log_tools.log_neighbours_access_times(self.neighbour_addresses)
            time_passed += config.LOG_NEIGHBOURS_TIME_PERIOD
            time.sleep(config.LOG_NEIGHBOURS_TIME_PERIOD)

    def get_hello_packet(self, host_address):
        return P2PPacket(self.host_id, self.host_address, config.HELLO_MESSAGE_TYPE, 
            self.neighbour_addresses, time.time(), self.hosts_last_receive_time[host_address])

    def send_hello_packet(self, host_address):
        hello_packet = self.get_hello_packet(host_address)
        self.udp_tools.send_udp_packet(host_address, pickle.dumps(hello_packet))
                    