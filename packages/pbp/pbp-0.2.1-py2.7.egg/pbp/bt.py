#!/usr/bin/env python

# todo rewrite using https://github.com/proquar/twisted-stuff
from bluetooth import *
from multiprocessing import Process, Manager, Queue
from Queue import Empty
import pysodium as nacl
import sys

PBP_BT_UUID = 'ae4880a6-8521-4231-a4bf-7dabadda382e'

def send2all(data):
    service_matches = find_service( uuid = PBP_BT_UUID)
    if len(service_matches) == 0:
        return
    receivers = {}
    for peer in service_matches:
        host = peer["host"]
        port = peer["port"]
        name = peer["name"]

        send(host, port, data)
        receivers[(host,port)]=name
    return receivers

def send(host, port, data):
    # Create the client socket
    sock=BluetoothSocket( RFCOMM )
    sock.connect((host, port))

    sock.send(data)
    sock.close()
    return host

def receive():
    server_sock=BluetoothSocket( RFCOMM )
    server_sock.bind(('',PORT_ANY))
    server_sock.listen(1)
    port = server_sock.getsockname()[1]
    advertise_service(server_sock, "MPECDHService",
                      service_id = PBP_BT_UUID,
                      service_classes = [ PBP_BT_UUID, SERIAL_PORT_CLASS ],
                      profiles = [ SERIAL_PORT_PROFILE ])
    client_sock, client_addr = server_sock.accept()
    server_sock.close()
    def res():
        try:
            while True:
                data = client_sock.recv(1024)
                if len(data) == 0: break
                yield data
        except IOError:
            pass
        client_sock.close()
    return client_addr, res()

def mpecdhannounce(res, ctrl):
    o = None
    while o != 'STOP':
        try:
            o = ctrl.get(False)
        except Empty:
            pass
        addr, ret = receive()
        res.append((addr, ''.join(ret)))

mgt = Manager()
q = Queue()
res = mgt.list()
announcer = Process(target=mpecdhannounce, args=(res,q))
announcer.start()

receivers = send2all("howdy")
print "sending over"
q.put('STOP')
announcer.join()

print sorted(receivers.keys())
print sorted(res)

#client, res = server()
#print client, ''.join(res)
#client("hello world")
