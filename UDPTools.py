import socket

class UDPTools:
    def __init__(self, server_address):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind((server_address[0], server_address[1]))

    def stop(self):
        self.server_socket.close()

    def send_udp_packet(self, host_address, data):
        client_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_sock.sendto(data, (host_address[0], host_address[1]))
        client_sock.close()

    def receive_udp_packet(self):
        data_bytes, address = self.server_socket.recvfrom(1024)
        return data_bytes