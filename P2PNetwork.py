from P2PHost import P2PHost
import multiprocessing
import config

class P2PNetwork:
    def __init__(self):
        self.host_processes = list()

    def start(self):
        self.create_host_processes()
        self.start_host_processes()

    def stop(self):
        pass

    def start_host_process(self, host_ip, host_port):
        p2p_host = P2PHost(host_ip, host_port)
        p2p_host.start()

    def create_host_processes(self):
        for host_port in config.HOSTS_PORTS:
            host_process = multiprocessing.Process(target=self.start_host_process, args=(config.HOSTS_IP, host_port))
            self.host_processes.append(host_process)

    def start_host_processes(self):
        for host_process in self.host_processes:
            host_process.start()
