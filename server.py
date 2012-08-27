#!/usr/bin/env python
# File: server.py
#
# Project: Websocket webkit notification pusher
# Component: server end application logic
#
# Authors: Dominic May;
#          Lord_DeathMatch;
#          Mause
#
# Description: a simple javascript and websocket notification push service


import version
import struct
import Queue
from threading import Thread
import socket
import SocketServer
from base64 import b64encode
from mimetools import Message
from StringIO import StringIO
try:
    from hashlib import sha1
except ImportError:
    from sha import sha as sha1
try:
    import json
except ImportError:
    import simplejson as json


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
        while hasattr(self, 'client_guid') == False:
            pass
        if self.client_guid not in notif_q:
            notif_q[self.client_guid] = Queue.Queue()
        while True:
            while len(notif_q[self.client_guid].queue) != 0:
                self.send_message(notif_q[self.client_guid].get())

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
            Thread(target=self.send_notif_to_client).start()

    def on_message(self, message):
        if message != 'ping' and message[:21] != 'port_thoroughput_test':
            print 'received from client;', message
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


def add_notif_to_q(notif, client):
    if client_dict[str(client)] not in notif_q:
        notif_q[client_dict[str(client)]] = Queue.Queue()
    notif_q[client_dict[str(client)]].put(json.dumps(notif))


def remove_item_from_dict(dictionary, item):
    to_output = {}
    for item in dictionary.keys():
        # item = item.encode('ascii')
        if item != 'client':
            to_output[item] = dictionary[item]
    return to_output


def handler(clientsocket, clientaddr):
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
            if '/clients' in data:
                print 'sending client_dict to control client'
                clientsocket.send(json.dumps(client_dict))

            elif '/notifs' in data:
                clientsocket.send(json.dumps([{x:map(None, notif_q[x].queue)} for x in notif_q.keys()][0]))

            else:
                data = json.loads(data)
                if len(client_dict) == 0:
                    clientsocket.send('error_no_clients_connected')
                    print 'error_no_clients_connected'

                elif str(data['client']) in client_dict.keys():
                    add_notif_to_q(remove_item_from_dict(data, 'client'), str(data['client']))
                    clientsocket.send('success')
                    print 'success'

                elif str(data['client']) == 'a':
                    for client in range(len(client_dict.keys())):
                        add_notif_to_q(remove_item_from_dict(data, 'client'), client)
                    clientsocket.send('success')
                    print 'success'

                else:
                    clientsocket.send('error_no_such_client')
                    print 'could not find client', data.split(':')[0]

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
        print 'starting new control server'
        cur_thread = Thread(target=handler, args=(clientsocket, clientaddr))
        cur_thread.daemon = True
        cur_thread.start()
    serversocket.close()


if __name__ == "__main__":
    version_string = version.get_version()
    print 'Websocket Notifications version %s' % version_string
    print 'Written by Dominic May'

    global notif_q
    notif_q = {}

    global client_dict
    client_dict = dict()

    global halt
    halt = False

    websocket_server = ThreadedTCPServer(("", 9999), WebSocketsHandler)
    websocket_server_thread = Thread(target=websocket_server.serve_forever)
    # Exit the server thread when the main thread terminates
    websocket_server_thread.daemon = True
    websocket_server_thread.start()

    # setup control server

    dispatch = Thread(target=dispatch_control, args=())
    # dispatch.daemon = True
    dispatch.start()
