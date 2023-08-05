#!/usr/bin/env python

"""Asynchronous client using Twisted with GNUTLS"""

import sys
import os

from twisted.internet import reactor
from eventlet.twistedutil.protocol import GreenClientCreator

from gnutls.constants import *
from gnutls.crypto import *
from gnutls.errors import *
from gnutls.interfaces.twisted import X509Credentials

script_path = os.path.realpath(os.path.dirname(sys.argv[0]))
certs_path = os.path.join(script_path, 'certs')

cert = X509Certificate(open(certs_path + '/valid.crt').read())
key = X509PrivateKey(open(certs_path + '/valid.key').read())
ca = X509Certificate(open(certs_path + '/ca.pem').read())
crl = X509CRL(open(certs_path + '/crl.pem').read())
cred = X509Credentials(cert, key, [ca])
cred.verify_peer = True

try:
    conn = GreenClientCreator(reactor).connectTLS('localhost', 10000, cred)
    conn.write('echo\r\n')
    print "received: %s" % conn.recv().rstrip()
    conn.loseConnection()
except CertificateError, e:
    print e

