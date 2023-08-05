#!/usr/bin/env python2
from twisted.internet.protocol import DatagramProtocol, Protocol, ClientFactory
from twisted.internet import reactor
from twisted.internet.task import LoopingCall
import netifaces
import socket, binascii
import pysodium as nacl
from utils import b85encode, split_by_n

PORT = 23235
iface = 'wlan0'
bcastaddr=netifaces.ifaddresses(iface)[netifaces.AF_INET][0].get('broadcast')
myip=netifaces.ifaddresses(iface)[netifaces.AF_INET][0].get('addr')

ctx = {}
seedcache={}

def broadcast(data, range, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.sendto(data, (range, port))

def close(host):
    print 'closing', host

def stats(host):
    if not host in seedcache:
        return
    if (len([x for x in seedcache[host]['seeds'] if not 'noack' in x])%10) == 0:
        print ' '.join(split_by_n(binascii.hexlify(seedcache[host]['verifier'][:8]), 4)),
        print host, len(seedcache[host]['seeds'])

def addseed(peer, seed, noack):
    if not peer in seedcache:
        seedcache[peer]={'seeds':[seed],
                         'verifier': None}
    else:
        seedcache[peer]['seeds'].append(seed)
    if noack:
        seedcache[peer]['noack']=seed
    else:
        updateverifier(peer, seed)

def updateverifier(peer, seed):
    if not seedcache[peer]['verifier']:
        seedcache[peer]['verifier'] = nacl.crypto_scalarmult_curve25519_base(seed)
    else:
        seedcache[peer]['verifier'] = nacl.crypto_scalarmult_curve25519(seedcache[peer]['verifier'], seed)

class Seeder(DatagramProtocol):
    def handleinit(self, data, peer, port):
        peer_pub = data[:nacl.crypto_scalarmult_curve25519_BYTES]
        khash = data[nacl.crypto_scalarmult_curve25519_BYTES:]
        e = nacl.randombytes(nacl.crypto_scalarmult_curve25519_BYTES)
        secret = nacl.crypto_scalarmult_curve25519(e, peer_pub)
        pub = nacl.crypto_scalarmult_curve25519_base(e)
        self.transport.write("1"+pub+khash, (peer, PORT))
        addseed(peer,secret,True)

    def handleend(self, data, peer):
        peer_pub = data[:nacl.crypto_scalarmult_curve25519_BYTES]
        khash = data[nacl.crypto_scalarmult_curve25519_BYTES:]
        e = ctx[khash]
        secret = nacl.crypto_scalarmult_curve25519(e, peer_pub)
        self.transport.write("2"+khash, (peer, PORT))
        self.transport.write("2"+khash, (peer, PORT))
        self.transport.write("2"+khash, (peer, PORT))
        addseed(peer,secret,False)

    def datagramReceived(self, data, (host, port)):
        if host == myip: return
        if data[0] == '0':
            self.handleinit(data[1:], host, port)
            stats(host)
        elif data[0] == '1':
            self.handleend(data[1:], host)
            stats(host)
        elif data[0] == '2':
            entry = seedcache.get(data[1:])
            if entry and 'noack' in entry:
                updateverifier(host, entry['noack'])
                del entry['noack']
            stats(host)
        elif data[0] == '9':
            close(host)

class Echo(Protocol):
    def dataReceived(self, data):
        print data

class EchoClientFactory(ClientFactory):
    def startedConnecting(self, connector):
        print 'Started to connect.'

    def buildProtocol(self, addr):
        print 'Connected.'
        return Echo()

    def clientConnectionLost(self, connector, reason):
        print 'Lost connection.  Reason:', reason

    def clientConnectionFailed(self, connector, reason):
        print 'Connection failed. Reason:', reason

def shutdown():
    broadcast('9', bcastaddr, PORT)
    for host in seedcache.keys():
        close(host)
    print "shutting down"

def initiator():
    # send initial ecdh packet!
    e = nacl.randombytes(nacl.crypto_scalarmult_curve25519_BYTES)
    pub = nacl.crypto_scalarmult_curve25519_base(e)
    khash = nacl.crypto_generichash(pub)
    ctx[khash]=e
    broadcast("0"+pub+khash, bcastaddr, PORT)

initloop = LoopingCall(initiator)
initloop.start(0.2)

reactor.listenUDP(PORT, Seeder())
reactor.addSystemEventTrigger('before','shutdown',shutdown)
reactor.run()
