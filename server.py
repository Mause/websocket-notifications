#!/usr/bin/env python
# File: server.py
#
# Project: Websocket webkit notification pusher
# Component: server end application logic
# Authors: Dominic May;
#          Lord_DeathMatch;
#          Mause
#
# Description: a simple javascript and websocket notification push service


import struct
import Queue
from threading import Thread as create_new_thread
import sys
import socket
import SocketServer
from base64 import b64encode
from hashlib import sha1
from mimetools import Message
from StringIO import StringIO


class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass


class WebSocketsHandler(SocketServer.StreamRequestHandler):
    global notif_q
    magic = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'

    def setup(self):
        SocketServer.StreamRequestHandler.setup(self)
        print "connection established", self.client_address
        self.handshake_done = False

    def handle(self):
        while not halt:
            if not self.handshake_done:
                self.handshake()
            else:
                while not notif_q.empty():
                    print 'sending notification'
                    self.send_message(notif_q.get())
                self.read_next_message()

    def read_next_message(self):
        length = ord(self.rfile.read(2)[1]) & 127
        if length == 126:
            length = struct.unpack(">H", self.rfile.read(2))[0]
        elif length == 127:
            length = struct.unpack(">Q", self.rfile.read(8))[0]
        masks = [ord(byte) for byte in self.rfile.read(4)]
        decoded = ""
        for char in self.rfile.read(length):
            decoded += chr(ord(char) ^ masks[len(decoded) % 4])
        self.on_message(decoded)

    def send_message(self, message):
        self.request.send(chr(129))
        length = len(message)
        if length <= 125:
            self.request.send(chr(length))
        elif length >= 126 and length <= 65535:
            self.request.send(126)
            self.request.send(struct.pack(">H", length))
        else:
            self.request.send(127)
            self.request.send(struct.pack(">Q", length))
        self.request.send(message)

    def handshake(self):
        data = self.request.recv(1024).strip()
        headers = Message(StringIO(data.split('\r\n', 1)[1]))
        self.originally_recieved_headers = headers
        if headers.get("Upgrade", None) != "websocket":
            return
        print 'Handshaking...'
        key = headers['Sec-WebSocket-Key']
        digest = b64encode(sha1(key + self.magic).hexdigest().decode('hex'))
        response = 'HTTP/1.1 101 Switching Protocols\r\n'
        response += 'Upgrade: websocket\r\n'
        response += 'Connection: Upgrade\r\n'
        response += 'Sec-WebSocket-Accept: %s\r\n\r\n' % digest
        self.handshake_done = self.request.send(response)

    def on_message(self, message):
        if message != 'ping' and message[:21] != 'port_thoroughput_test':
            print 'data;', message
        if message[:21] == 'port_thoroughput_test':
            self.client_guid = message[22:]
            print 'client guid is', self.client_guid
            if self.client_guid != '':
                client_list.append(self.client_guid)
            self.send_message('port_thoroughput_test_confirmation' + self.client_guid)
        elif message == 'ping':
            self.send_message('pong')
        else:
            self.send_message(message)


def handler(clientsocket, clientaddr):
    print 'control server started'
    data = ''
    global halt
    while not halt:
        try:
            data = clientsocket.recv(1024)
        except KeyboardInterrupt:
            print 'shutting down control server'
            break
        if data:
            print 'data;', data
            if data[:8] == 'shutdown':
                # break
                halt = True
                clientsocket.close()
                sys.exit(0)
            elif '~' in data:
                clientsocket.send('Creating new notification; ' + str(data))
                notif_q.put(data)
                # server.send_message(data)
            elif data[:3] == 'py;':
                exec(data[3:])
                clientsocket.send('Done')
            elif '/clients' in data:
                print 'sending client_list to control client'
                clientsocket.send(str(client_list))
            elif 'queue_test' in data:
                print notif_q.queue
                print notif_q.put('h')
                print notif_q.queue[0]
                clientsocket.send('Done')
            else:
                clientsocket.send('What do i do?')
    clientsocket.close()


def dispatch_control():
    global halt
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.bind(('', 50012))
    serversocket.listen(2)
    while not halt:
        try:
            clientsocket, clientaddr = serversocket.accept()
        except KeyboardInterrupt:
            print 'shutting down control dispatch server'
            break
        # thread.start_new_thread(handler, (clientsocket, clientaddr, server))
        print 'starting new control server'
        create_new_thread(target=handler, args=(clientsocket, clientaddr)).start()
    serversocket.close()


if __name__ == "__main__":
    print 'Started up'

    global notif_q
    notif_q = Queue.Queue()

    global client_list
    client_list = list()

    global halt
    halt = False

    # setup weksocket server :DSocketServer.TCPServer
    # print help(ThreadedTCPServer.__init__)
    server = ThreadedTCPServer(("", 9999), WebSocketsHandler)
    server.notif_q = notif_q
    server_thread = create_new_thread(target=server.serve_forever)
    # Exit the server thread when the main thread terminates
    server_thread.daemon = True
    server_thread.start()

    # setup control server

    # server_instance = server.serve_forever()
    print 'execution continues...'
    # print dir(server_thread)
    dispatch = create_new_thread(target=dispatch_control, args=()).start()  # notif_q
