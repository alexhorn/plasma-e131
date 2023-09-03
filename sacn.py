import socket
import struct

class sACNServer:
    def __init__(self, universe = 1):
        self.universe = universe
        self.last_sequence = -1
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
    def bind(self, ip, port):
        self.sock.bind((ip, port))
        
    def recv(self):
        data, _ = self.sock.recvfrom(2048)
        return self.__process(data)
        
    def __process(self, data):
        if data[4:16] != b'ASC-E1.17\x00\x00\x00':
            # not an E1.17 packet
            print('not an E1.17 packet')
            return
        if data[18:22] != b'\x00\x00\x00\x04':
            # not an E1.31 root packet
            print('not an E1.31 root packet')
            return
        if data[40:44] != b'\x00\x00\x00\x02':
            # not an E1.31 data packet
            print('not an E1.31 data packet')
            return
        if data[125] != 0x00:
            # not a DMX lighting control packet
            print('not a DMX lighting control packet')
            return

        universe, = struct.unpack('!H', data[113:115])
        sequence = data[111]
        dmx = data[126:638]
        
        if universe != self.universe:
            return None

        if sequence > self.last_sequence:
            self.last_sequence = sequence
            return dmx
        if sequence < self.last_sequence - 128:
            # way out of sync, try to recover
            self.last_sequence = sequence
            return dmx
        else:
            return None
