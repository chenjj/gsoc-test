gsoc-test
=========

A simple socket program to read arbitrary input from one socket and write it to another socket.

##client
This  program  is a client to send or receive  file data.
* The recieved file will be named as its md5 value.

usage:
python  client.py --host host -p port action [filepath]

##server
This program is a server which is listening on port 1234.
The server receives the file from the sender,and sends it to the receiver.
Message Format:  MessageLength | opcode | filedata

usage:
python server.py

##example
1.run `$ python server.py` to start server

2.run `$ python client.py --host 127.0.0.1 -p 1234 receive` to receive file

3.run `$ python client.py --host 127.0.0.1 -p 1234 send yourfilename` to send file

