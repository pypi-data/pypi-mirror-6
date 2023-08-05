#!/usr/bin/env python

import pprocess

class Ex(pprocess.Exchange):
    def store_data(self, channel):
        data = channel.receive()
        print "Parent:", data
        channel.send(data - 1)
        print "Parent sent"

def child(channel, data):
    while data != 0:
        print "Child:", data
        channel.send(data)
        print "Child sent"
        data = channel.receive()

ex = Ex()
ex.add(pprocess.start(child, 20))
ex.finish()

# vim: tabstop=4 expandtab shiftwidth=4
