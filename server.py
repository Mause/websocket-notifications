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

    def send_notif_to_client(self):
        print 'notification pusher started'
        while hasattr(self, 'client_guid') == False:
            pass
        if self.client_guid not in notif_q:
            notif_q[self.client_guid] = []
            print 'no entry for this client in the notif dict'
        while True:
            while len(notif_q[self.client_guid]) != 0:
                print 'sending notification'
                self.send_message(notif_q[self.client_guid][0])
                notif_q[self.client_guid].pop(0)

    def handle(self):
        while not halt:
            if not self.handshake_done:
                self.handshake()
            else:
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
        if self.handshake_done:
            create_new_thread(target=self.send_notif_to_client).start()

    def on_message(self, message):
        if message != 'ping' and message[:21] != 'port_thoroughput_test':
            print 'data;', message
        if message[:21] == 'port_thoroughput_test':
            self.client_guid = message[22:]
            print 'client guid is', self.client_guid
            if self.client_guid != '':
                if len(client_dict) != 0:
                    pos = int(client_dict.keys()[0]) + 1
                else:
                    pos = 0
                client_dict[str(pos)] = self.client_guid
            self.send_message('port_thoroughput_test_confirmation' + self.client_guid)
        elif message == 'ping':
            self.send_message('pong')
        else:
            self.send_message(message)


def handler(clientsocket, clientaddr):
    print 'control server started'
    global client_dict
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
                if len(client_dict) == 0:
                    print 'No clients connected!'
                elif str(data.split(':')[0]) in client_dict.keys():
                    clientsocket.send('Creating new notification; ' + str(data))
                    if client_dict[str(data.split(':')[0])] not in notif_q:
                        notif_q[client_dict[str(data.split(':')[0])]] = []
                        print 'no entry for this client in the notif dict'

                    notif_q[client_dict[str(data.split(':')[0])]].append(''.join(data.split(':')[1:]))
                else:
                    clientsocket.send('Could not find that client')
                    print 'could not find client', data.split(':')[0]
                # server.send_message(data)
            elif data[:3] == 'py;':
                exec(data[3:])
                clientsocket.send('Done')
            elif '/clients' in data:
                print 'sending client_dict to control client'
                clientsocket.send(str(client_dict))
            elif '/notifs' in data:
                clientsocket.send(str(notif_q))
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
    # notif_q = Queue.Queue()
    notif_q = {}

    global client_dict
    client_dict = dict()

    global halt
    halt = False

    # setup weksocket server :DSocketServer.TCPServer
    # print help(ThreadedTCPServer.__init__)
    server = ThreadedTCPServer(("", 9999), WebSocketsHandler)
    # server.notif_q = notif_q
    server_thread = create_new_thread(target=server.serve_forever)
    # Exit the server thread when the main thread terminates
    server_thread.daemon = True
    server_thread.start()

    # setup control server

    # server_instance = server.serve_forever()
    print 'execution continues...'
    # print dir(server_thread)
    dispatch = create_new_thread(target=dispatch_control, args=()).start()  # notif_q
