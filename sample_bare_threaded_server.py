from socket import *
import thread


def handler(clientsocket, clientaddr):
    data = ''
    while True:
        try:
            data = clientsocket.recv(1024)
        except KeyboardInterrupt:
            print 'shutting down control server'
            break
        if data:
            print 'data;', data
            if 'shutdown' in data:
                break
                clientsocket.close()
            else:
                clientsocket.send(data)
    clientsocket.close()


if __name__ == "__main__":

    buf = 1024

    serversocket = socket(AF_INET, SOCK_STREAM)
    serversocket.bind(('', 50012))
    serversocket.listen(2)

    while True:
        try:
            clientsocket, clientaddr = serversocket.accept()
        except KeyboardInterrupt:
            print 'shutting down control dispatch server'
            break
        thread.start_new_thread(handler, (clientsocket, clientaddr))
    serversocket.close()
