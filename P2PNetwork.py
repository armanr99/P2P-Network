from P2PHost import P2PHost
import multiprocessing

class P2PNetwork:
    def __init__(self):
        self.host_processes = list()

    def start(self):
        self.create_host_processes()
        self.start_host_processes()

    def stop(self):
        pass

    def start_host_process(self):
        p2p_host = P2PHost()
        p2p_host.start()

    def create_host_processes(self):
        for i in range(0, 6):
            host_process = multiprocessing.Process(target=self.start_host_process)
            self.host_processes.append(host_process)

    def start_host_processes(self):
        for host_process in self.host_processes:
            host_process.start()
