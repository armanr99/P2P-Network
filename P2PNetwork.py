import threading
import time
import random
import config

from P2PHost import P2PHost

class P2PNetwork:
    def __init__(self):
        self.hosts = list()

    def start(self):
        self.create_hosts()
        self.run_hosts()
        threading.Thread(target=self.finish_hosts_run).start()
        threading.Thread(target=self.pause_host_run).start()

    def stop(self):
        pass

    def create_hosts(self):
        for host_address in config.HOST_ADDRESSES:
            self.hosts.append(P2PHost(host_address))

    def run_hosts(self):
        for host in self.hosts:
            threading.Thread(target=host.start).start()

    def finish_hosts_run(self):
        time.sleep(config.SIMULATION_TIME)
        for host in self.hosts:
            host.stop()

    def pause_host_run(self):
        passed_time = 0
        paused_hosts_infos = list()

        while passed_time < config.SIMULATION_TIME:
            time.sleep(config.PAUSE_HOST_PERIOD)
            passed_time += config.PAUSE_HOST_PERIOD 

            random_host = random.choice(self.hosts)
            random_host.pause()
            paused_hosts_infos.append((random_host, passed_time))

            if passed_time - paused_hosts_infos[0][1] >= config.PAUSE_HOST_TIME:
                to_resume_host = paused_hosts_infos.pop()[0]
                if to_resume_host not in [paused_hosts_info[0] for paused_hosts_info in paused_hosts_infos]:
                    to_resume_host.resume()
        