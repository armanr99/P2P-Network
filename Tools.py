import socket
import pickle

class Tools:
    def send_udp_packet(self, host_address, data):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(pickle.dumps(data), (host_address[0], host_address[1]))
        sock.close()