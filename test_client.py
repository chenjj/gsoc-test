import unittest
import SocketServer
import struct
import hashlib
import socket
import threading
import os
import time
from client import Client

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    def server_bind(self):
        #set reuseaddr option
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.server_address)

class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        data = self.request.recv(40960)
        msglen, opcode = struct.unpack('!iB', buffer(data,0,5))
        filedata = bytearray(buffer(data, 5, msglen-5))
        if opcode == 0:#send msg
            #send back the data to client
            self.request.send(filedata)
        if opcode == 1:#recv msg
            #send test data
            self.request.send("abcdABCD1234%$#(")

class TestClient(unittest.TestCase):
    def setUp(self):
        self.server = ThreadedTCPServer(('127.0.0.1', 1234), ThreadedTCPRequestHandler)
        #start server
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()

    def tearDown(self):
        self.server.shutdown()
        #close the server socket
        self.server.socket.close()
        #md5("abcdABCD1234%$#(") = 1135f0fa7fa005db3d04269e0bdc47e4
        if os.path.exists("1135f0fa7fa005db3d04269e0bdc47e4"):
            os.remove("1135f0fa7fa005db3d04269e0bdc47e4")

    def test_send_file(self):
        """test send file"""
        clientsock = Client("127.0.0.1",1234)
        #send test data
        clientsock.sendfile("data")
        data = clientsock.socket_handle.recv(40960)
        self.assertTrue(hashlib.md5(data).hexdigest() == "1135f0fa7fa005db3d04269e0bdc47e4")
        clientsock.close()
    
    def test_receive_file(self):
        """test receive file"""
        clientsock = Client("127.0.0.1",1234)
        #receive test data
        clientsock.receivefile()
        self.assertTrue(os.path.exists("1135f0fa7fa005db3d04269e0bdc47e4"))
        clientsock.close()

def suite():
    suite = unittest.TestSuite()
    suite.addTest(TestClient())
    return suite

if __name__ == "__main__":
    unittest.main()
    
