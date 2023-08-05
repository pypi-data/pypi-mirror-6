#!/usr/bin/env python2

import os
import pysodium as nacl
import scrypt
import publickey, pbp
from utils import b85encode
from SecureString import clearmem

class SeedStore():
    # TODO implement locking
    def __init__(self, key, basedir = '.'):
        self.key = publickey.Identity(key, basedir=basedir)
        self.basedir = basedir

    def load_seeds(self, id):
        keyfname="%s/dh/%s/%s.cs" % (self.basedir, self.key.name, id)
        if not os.path.exists(keyfname):
            return ''
        with open(keyfname,'r') as fd:
            nonce = fd.read(nacl.crypto_box_NONCEBYTES)
            raw = fd.read()
        return nacl.crypto_box_open(raw, nonce, self.key.cp, self.key.cs)

    def save_seeds(self, id, seeds):
        nonce = nacl.randombytes(nacl.crypto_box_NONCEBYTES)
        fname="%s/dh/%s/%s.cs" % (self.basedir,self.key.name, id)
        with open(fname,'wb') as fd:
            fd.write(nonce)
            fd.write(nacl.crypto_box(seeds, nonce, self.key.cp, self.key.cs))

    def store(self, id, secret):
        keyfdir="%s/dh/%s" % (self.basedir, self.key.name)
        if not os.path.exists(keyfdir):
            os.makedirs(keyfdir)
        fname='%s/%s.cs' % (keyfdir, id)
        nonce = nacl.randombytes(nacl.crypto_box_NONCEBYTES)
        seeds = self.load_seeds(id)
        self.save_seeds(id, seeds+secret)
        clearmem(seeds)
        seeds = None

    def pop_seed(self, id, seedid=None, delete=False):
        seeds = self.load_seeds(id)
        if not len(seeds) or len(seeds)%nacl.crypto_scalarmult_curve25519_BYTES != 0:
            return

        res = None
        i = 0
        if seedid:
            while i < len(seeds):
                curhash=nacl.crypto_generichash(seeds[i:i+nacl.crypto_scalarmult_curve25519_BYTES], outlen=6)
                if curhash==seedid:
                    res = seeds[i:i+nacl.crypto_scalarmult_curve25519_BYTES]
                    break
                i += nacl.crypto_scalarmult_curve25519_BYTES
        else:
            i = random(len(seeds)/nacl.crypto_scalarmult_curve25519_BYTES)
            res = seeds[i:i+nacl.crypto_scalarmult_curve25519_BYTES]
        if not res:
            return
        if delete:
            ns = seeds[:i]+seeds[i+nacl.crypto_scalarmult_curve25519_BYTES:]
            if len(ns):
                self.save_seeds(ns)
            clearmem(ns)
            ns = None
        # TODO make copy of res, and clearmem(seeds)
        return res

    def getkey(self, peerid, seedid=None):
        seed = self.pop_seed(peerid, seedid)
        if not seed:
            return
        key = scrypt.hash(seed, pbp.scrypt_salt)[:nacl.crypto_secretbox_KEYBYTES]
        if not seedid:
            seedhash = nacl.crypto_generichash(seed, outlen=6)
        clearmem(seed)
        seed=None
        if seedid:
            return key
        return key, seedhash

    def encrypt(self, peerid, msg):
        key, seedhash = self.getkey(peerid)
        nonce = nacl.randombytes(nacl.crypto_secretbox_NONCEBYTES)
        ciphertext = nacl.crypto_secretbox(msg, nonce, key)
        return (ciphertext, nonce, seedhash)

    def decrypt(self, peerid, cipher, nonce, seedhash):
        key = self.getkey(peerid, seedhash)
        if not key:
            return
        return nacl.crypto_secretbox_open(cipher, nonce, key)

def random(lim):
    res = ord(nacl.randombytes(1))
    while res> (255/lim)*lim:
        res = ord(nacl.randombytes(1))
    return res % lim

if __name__ == '__main__':
    ctxa = SeedStore('alice', '../test-pbp')
    ctxb = SeedStore('bob', '../test-pbp')
    shared = nacl.randombytes(nacl.crypto_secretbox_KEYBYTES)
    ctxa.store('test',shared)
    ctxb.store('test',shared)
    print ctxb.decrypt('test', *ctxa.encrypt('test', 'hello world'))
