import unittest

from samsa.utils import protocol

class TestProtocol(unittest.TestCase):

    def test__metadata_request(self):
        msg = protocol.pack_produce_request(messages)
        import socket
        conn = socket.create_connection(('localhost', 9092))
        conn.sendall(msg)
        h = conn.recv(4)
        import struct
        ln = struct.unpack('!i', h)[0]
        resp = conn.recv(ln)
        resp = protocol.unpack_produce_response(resp[4:])
        from pprint import pprint; pprint(resp)
        import pdb; pdb.set_trace()
        conn.close()

    def test_decode_metadata_request(self):
        pass


if __name__ == '__main__':
    unittest.main()
