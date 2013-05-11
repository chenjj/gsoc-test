import socket
import struct
from threading import Thread
import logging

logger = logging.getLogger('server')
logging.basicConfig(level=0)

#the message opcode 
OP_SEND = 0 #send file
OP_RECV = 1 #receive file

# the max size of signle file
BUFSIZE = 40960

#the IP and port to listen
host = ""
port = 1234


def handle_connection(clientsock):
    clientInfo = str(clientsock.getpeername())
    logger.info('connection from {0}'.format(clientInfo))
    while True:
        #recieve msg
        data = clientsock.recv(BUFSIZE)
        if not len(data):
            break
        #decode the msg, msglen|opcode|filedata
	msglen, opcode = struct.unpack('!iB', buffer(data,0,5))
        if msglen < 5:
            continue
	filedata = bytearray(buffer(data, 5, msglen-5))
        #send data to each connection which is waiting for filedata
        if opcode == OP_SEND:
            for s in set(recv_collection):
                s.send(filedata)
        #add client sock to the set
        if opcode == OP_RECV:
            recv_collection.add(clientsock)

    logger.info('close {0} connection.'.format(clientInfo))
    #remove client sock to the set
    if clientsock in recv_collection:
    	recv_collection.remove(clientsock)
    clientsock.close()

# a set to store the socket handle of recieve connection
recv_collection = set()
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind((host, port))
sock.listen(1)

while True:
    try:
        clientsock, clientaddr = sock.accept()
    except (KeyboardInterrupt, SystemExit):
        raise
    except:
        continue
    #start a new thread, if a new connection comes
    t = Thread(target=handle_connection, args=[clientsock])
    t.setDaemon(1)
    t.start()

