import socket
import logging
import optparse
import io
import sys
import time
import os
import struct
import hashlib

logger = logging.getLogger('client')
logging.basicConfig(level=0)

#the message opcode 
OP_SEND = 0 #send file
OP_RECV = 1 #receive file

# the max size of signle file
BUFSIZE = 40960

def opts():
    """prase the options."""
    usage="%prog --host host -p port <action> [<filepath>]"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option("--host",
        action="store", dest='host', nargs=1, type='string',
        help="server host")
    parser.add_option("-p", "--port",
        action="store", dest='port', nargs=1, type='int',
        help="server port")
    options, args = parser.parse_args()
    if len(args)<1:
        parser.error('You need to give "send" or "receive" as <action>.')
    action = args[0]
    if action not in ['send', 'receive']:
        parser.error('You need to give "send" or "receive" as <action>.')
    filepath = None
    if action == 'send':
        filepath = args[1]
        if not os.path.exists(filepath):
            parser.error("The file {0} doesn't exsits".format(filepath))
    return options, action, filepath

def main(opts, action, filepath=None):
    """main function."""
    try:
        client = Client(opts.host, opts.port)
    except ClientException, e:
        logger.error("ClientException Error:{0}".format(e))
        return 1
    if action == 'send':
        client.sendfile(filepath)
    if action == 'receive':
        client.receivefile()
    logger.info("connection closed")
    client.close()

class ClientException(Exception):
    """client exception"""
    pass

class Client(object):
    """A simple Client which can send and receive files"""
    def __init__(self, host, port,reconnect=True):
        """simple constructor"""
        self.host=host
        self.port=port
        self.connect_state = False

        self.connect();

    def connect(self):
        """Connect to the server"""
        logger.info('connecting to {0}:{1}'.format(self.host, self.port))
        self.socket_handle = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_handle.settimeout(3)
        try: 
            self.socket_handle.connect((self.host, self.port))
        except: 
            raise ClientException('Fail to connect to the server')
        self.connect_state = True
        logger.info("Client established")
        self.socket_handle.settimeout(None)
        self.socket_handle.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)

    def receivefile(self):
        """receive the data and store it ,name the file after its md5"""
        #send a subscribe message to the server 
        fileheader = struct.pack('!iB', 5, OP_RECV)
        ml, opcode = struct.unpack('!iB', buffer(fileheader,0,5))
        self.socket_handle.send(fileheader)

        #recieve data
        while self.connect_state:
            filedata=self.socket_handle.recv(BUFSIZE)
            if not filedata:
                self.connect_state = False
                break
            try:                
                filehandle = open(hashlib.md5(filedata).hexdigest(), 'wb')
                filehandle.write(filedata)
                filehandle.close()
            except:
                raise ClientException('Cannot write data to current directory.')

    def  sendfile(self,filepath):
        """send file data"""
        #the max size of filedata is BUFSIZE ,if a file is larger than BUFSIZE,
        #  it will only send  first BUFSIZE bytes.
        filehandle = open(filepath, 'rb')
        fsize = os.stat(filepath).st_size
        if fsize > BUFSIZE:
            fsize = BUFSIZE
        fileheader = struct.pack('!iB', 5+fsize, OP_SEND)
        filedata = filehandle.read(BUFSIZE)
        self.socket_handle.send(fileheader+filedata)
        filehandle.close()

    def close(self):
        """Close client"""
        try: 
            self.socket_handle.close()
            self.connect_state = False
        except: 
            logger.warn('ClientException while closing socket')

if __name__ == '__main__':
    options, action, filepath = opts()
    try:
        sys.exit(main(options, action, filepath=filepath))
    except KeyboardInterrupt:
        sys.exit(0)

