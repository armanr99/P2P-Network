class P2PPacket:
    def __init__(self, host_ip, host_port, message_type, bidrectional_ports, last_time_sent, last_time_received):
        self.host_ip = host_ip
        self.host_port = host_port
        self.message_type = message_type
        self.bidrectional_ports = bidrectional_ports
        self.last_time_sent = last_time_sent
        self.last_time_received = last_time_received
