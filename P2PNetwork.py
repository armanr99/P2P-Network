import threading
import time
import config

from P2PHost import P2PHost

class P2PNetwork:
    def __init__(self):
        self.hosts = list()

    def start(self):
        self.create_hosts()
        self.run_hosts()

    def stop(self):
        pass

    def create_hosts(self):
        for host_address in config.HOST_ADDRESSES:
            self.hosts.append(P2PHost(host_address))

    def run_hosts(self):
        for host in self.hosts:
            threading.Thread(target=host.start).start()