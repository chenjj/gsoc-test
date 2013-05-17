import socket
import logging
import struct
import threading
import time

logging.basicConfig(level=logging.INFO)

#the message opcode 
OP_SEND = 0 #send file
OP_RECV = 1 #receive file

# the max size of single file
BUFSIZE = 40960

class BaseServer(object):
    """
    The base socket server class.
    """
    def __init__(self, host, port):
        """Simple constructor"""
        self.logger = logging.getLogger('server')
        self.logger.debug('__init__')
        self.host = host
        self.port = port
        self.runn_state = False

    def handle_connection(self):
        """Handle one new connection"""
        raise NotImplementedError()

    def handle_msg(self, msg):
        """Handle one incoming message"""
        raise NotImplementedError()

    def shutdown(self):
        """Close server"""
        self.run_state = False

    def serve(self):
        """Server start"""
        raise NotImplementedError()

class StreamServer(BaseServer):
    """Derive a simple TCP server from BaseServer"""
    def __init__(self, host, port):
        super(StreamServer, self).__init__(host, port)
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_sock.bind((host,port))
        self.server_sock.listen(1)
        self.run_state = True
        self.logger.info("Server has started.")

    def handle_connection(self, client_sock):
        """Handle one new connection, and receive msg from new connection."""
        client_info = str(client_sock.getpeername())
        self.logger.info('connection from {0}'.format(client_info))
        try:
            while True:
                data = self.recv_msg(client_sock)
                if not len(data):
                    break
                self.handle_msg(data)
        finally:
            client_sock.close()

    def send_msg(self, client_sock, msg):
        """Use client socket to send msg"""
        client_sock.send(msg)

    def recv_msg(self, client_sock):
        """receive msg from client_sock"""
        data = client_sock.recv(BUFSIZE)
        return data

    def serve(self):
        """Server start, if new connection comes, start a new thread"""
        try:
            while self.run_state:
                client_sock, client_addr = self.server_sock.accept()
                client_thread = threading.Thread(target=self.handle_connection, args=[client_sock])
                client_thread.setDaemon(True)
                client_thread.start()
        finally:
            self.server_sock.close()

class FileTransferServer(StreamServer):
    """
    A simple server to transfer file from one client to another.
    The file data is packed in a message. 
    Message format: | Messagelen | opcode | filedata
                    |---4bytes---|-1bytes-|---------
    Message types:
         opcode=0:send file data
         opcode=1:recv file data
    If a client wants to receive file data , it will send a recv msg with opcode=1 firstly.
    """
    def __init__(self, host, port):
        super(FileTransferServer, self).__init__(host, port)
        self.recv_collection = set()

    def handle_connection(self, client_sock):
        """Handle one new connection, and receive msg from new connection."""
        client_info = str(client_sock.getpeername())
        self.logger.info('new connection from {0}'.format(client_info))
        try:
            while True:
                data = self.recv_msg(client_sock)
                if not len(data):
                    break
                #wait for socket I/O to finish, or the server will show "connection reset by pee" error
                time.sleep(0.1)
                self.handle_msg(client_sock, data)
        finally:
            #remove client sock to the set
            if client_sock in self.recv_collection:
                self.recv_collection.remove(client_sock)
            self.logger.info('close connection {0}  '.format(client_info))
            client_sock.close()

    def handle_msg(self, client_sock, msg): 
        """decode msg, receive file data from one socket , and send it to another"""
        self.logger.debug('handle_msg')
        if len(msg) < 5:
            self.logger.warn("Useless message.")
        #decode the msg, msglen|opcode|filedata
        msg_len, opcode = struct.unpack("!iB", buffer(msg, 0, 5))
        if msg_len <5:
            self.logger.warn("Useless message.")
        file_data = bytearray(buffer(msg, 5, msg_len-5))
        if opcode == OP_SEND:
            #send data to each connection which is waiting for filedata
            for sock in set(self.recv_collection):
                self.send_msg(sock, file_data)
        elif opcode == OP_RECV:
            #add client sock to the set
            self.recv_collection.add(client_sock)
        else:
            self.logger.warn("Wrong message type")

if __name__ == '__main__':
    file_transfer_server = FileTransferServer('', 1234)
    file_transfer_server.serve()
