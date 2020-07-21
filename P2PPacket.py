class P2PPacket:
    def __init__(self, host_id, host_address, message_type, neighbour_addresses, last_time_sent, last_time_received):
        self.host_id = host_id
        self.host_address = host_address
        self.message_type = message_type
        self.neighbour_addresses = neighbour_addresses
        self.last_time_sent = last_time_sent
        self.last_time_received = last_time_received
