gsoc-test
=========

simple socket program,reads arbitrary input from one socket and writes it to another socket.

##client
This  program  is a client to send or recieve  file data.
The recieved file will be named as its md5 value.

usage:
python  client.py --host host -p port <action> [<filepath>]

##server
This program is a server which is listen on port 1234

usage:
python server.py

##example
1.run `$ python server.py` to start server
2.run `$ python client.py --host 127.0.0.1 -p 1234 recieve` to recieve file
3.run `$ python client.py --host 127.0.0.1 -p 1234 send yourfilename` to send file

