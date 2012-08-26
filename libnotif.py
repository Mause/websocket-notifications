#!/usr/bin/env python
# File: libnotif.py
#
# Project: Websocket webkit notification pusher
# Component: notification api code
#
# Authors: Dominic May;
#          Lord_DeathMatch;
#          Mause
#
# Description: A ridiculously simple method of controlling the notifications system programmatically


import time
from socket import *
try:
    import json
except ImportError:
    import simplejson as json


def if_connected(handler):
    print dir(handler)
    # if not handler.connected:
    #     raise socket.error('Not connected')


class NotifConn:
    def __init__(self, host='localhost', port=50012):
        self.buf = 1024
        self.host = host
        self.port = port
        self.connected = False

    def connect(self):
        self.addr = (self.host, self.port)
        self.clientsocket = socket(AF_INET, SOCK_STREAM)
        self.clientsocket.connect(self.addr)
        self.connected = True

    # @if_connected
    def request_clients(self):
        self.clientsocket.send('/clients')
        data = json.loads(self.clientsocket.recv(self.buf))
        return data

    # @if_connected
    def request_notifs(self):
        self.clientsocket.send('/notifs')
        data = json.loads(self.clientsocket.recv(self.buf))
        return data

    # @if_connected
    def send_notif(self, title, client='a', content='', icon=''):
            # '%s:%s~%s~%s' % (client, icon, title, content)
        self.clientsocket.send(json.dumps({
            'client': client,
            'icon': icon,
            'title': title,
            'content': content
            })
        )
        status = self.clientsocket.recv(self.buf)
        if status.startswith('error_'):
            return status

    # @if_connected
    def disconnect(self):
        self.connected = False
        self.clientsocket.close()


def quick_send(title, client='a', content='', icon=''):
    conn = NotifConn('localhost', 50012)
    if len(conn.request_clients()) != 0:
        conn.send_notif(title, client, content, icon)
    conn.disconnect()


if __name__ == '__main__':
    conn = NotifConn('localhost', 50012)
    conn.connect()
    print 'Waiting for clients...'
    while len(conn.request_clients()) == 0:
        time.sleep(1)
    print 'Clients;',
    print conn.request_clients()
    message = True
    try:
        while message != '':
            message = raw_input('Message? ')
            conn.send_notif(str(message))
    except:
        if conn.connected:
            conn.disconnect()
    finally:
        if conn.connected:
            conn.disconnect()
    conn.disconnect()
