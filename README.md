gsoc-test
=========

A simple socket program to read arbitrary input from one socket and write it to another socket.

# Client
The client will send or receive file data to server. The recieved file will be named as its md5 value.

Example usage:

`python  client.py --host host -p port action [filepath]`

Two actions: `receive` and `send`

## Server
The server will listen on port 1234 to receives the file from client and send it back.

`Message Format:  MessageLength | opcode | filedata`

## Example

1.run `$ python server.py` to start the server

2.run `$ python client.py --host 127.0.0.1 -p 1234 receive` to receive file

3.run `$ python client.py --host 127.0.0.1 -p 1234 send yourfilename` to send file

