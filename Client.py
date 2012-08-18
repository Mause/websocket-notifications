#!/usr/bin/env python
from socket import *
import os
import platform

if 'windows' in platform.platform().lower():
    os.system('title DTMUD CLIent')

#host = 'irc.lysdev.com'
host = raw_input('Please enter the hostname [localhost]: ')
if host in ['', None]:
    host = 'localhost'
port = 50012

print 'DTMUD CLIent\nIs set to connect to localhost:50012.'

if __name__ == '__main__':
    buf = 1024
    addr = (host, port)
    clientsocket = socket(AF_INET, SOCK_STREAM)
    #try:
    if True:
        clientsocket.connect(addr)
    #except:# socket.error:
     #   print "Couldn't connect to the server;\nare you have the right address and that the server is running?"
    while 1:
        data = raw_input(">> ")
        if not data:
            clientsocket.send('')
            break
        else:
            clientsocket.send(data)
            data = clientsocket.recv(buf)
            if not data or data == '':
                clientsocket.send('')
                break
            else:
                print data
    print '\nDisconnecting from server..'
    clientsocket.close()
