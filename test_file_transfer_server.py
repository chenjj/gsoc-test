import unittest
import struct
import hashlib
import socket
import threading
import os
import time
from file_transfer_server import FileTransferServer
from file_transfer_server import BaseServer
from client import Client

class TestBaseServer(unittest.TestCase):
    """Test BaseServer"""
    def setUP(self):
        pass

    def tearDown(self):
        pass

    def test_init(self):
        """Test __init__ method"""
        base_server = BaseServer("127.0.0.1",1234)
        self.assertTrue(base_server.host == '127.0.0.1')
        self.assertTrue(base_server.port == 1234)
        
class TestFileTransferServer(unittest.TestCase):    
    """Test FileTranserServer"""
    def setUp(self):
        pass

    def tearDown(self):
        if os.path.exists("1135f0fa7fa005db3d04269e0bdc47e4"):
            os.remove("1135f0fa7fa005db3d04269e0bdc47e4")

    def test_handle_msg(self):
        file_transer_server = FileTransferServer('127.0.0.1',1234)
        #start server
        server_thread = threading.Thread(target=file_transer_server.serve)
        server_thread.setDaemon(True)
        server_thread.start()
        recv_sock = Client('127.0.0.1',1234)
        send_sock = Client('127.0.0.1',1234)
        #receive file
        recv_thread = threading.Thread(target=recv_sock.receivefile)
        recv_thread.setDaemon(True)
        recv_thread.start()
        #send file
        send_sock.sendfile("data")
        #wait for socket I/O to finish, or the test will fail.
        time.sleep(0.5)
        self.assertTrue(os.path.exists("1135f0fa7fa005db3d04269e0bdc47e4"))
        recv_sock.close()
        send_sock.close()
        file_transer_server.shutdown()
        #wait for the socket I/O to finish
        time.sleep(0.5)

def suite():
    suite = unittest.TestSuite()
    suite.addTest(TestBaseServer())
    suite.addTest(TestFileTransferServer())
    return suite

if __name__ == "__main__":
    unittest.main()
    
