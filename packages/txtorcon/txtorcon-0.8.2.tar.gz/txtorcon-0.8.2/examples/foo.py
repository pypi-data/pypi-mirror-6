#!/usr/bin/env python

import functools

from twisted.python import log
from twisted.internet import reactor, defer
from zope.interface import implements

import txtorcon

def ding(foo, bar):
    print "DING", foo, bar

def setup_complete(state):
    path0 = [state.guards.values()[0], state.guards.values()[0], state.guards.values()[0]]
    path1 = [state.guards.values()[1], state.guards.values()[1], state.guards.values()[1]]
    state.build_circuit(path0).addCallback(functools.partial(ding, "zero"))
    state.build_circuit(path1).addCallback(functools.partial(ding, "one"))

def setup_failed(arg):
    print "SETUP FAILED", arg
    reactor.stop()

d = txtorcon.build_local_tor_connection(reactor)
d.addCallback(setup_complete).addErrback(setup_failed)
reactor.run()
