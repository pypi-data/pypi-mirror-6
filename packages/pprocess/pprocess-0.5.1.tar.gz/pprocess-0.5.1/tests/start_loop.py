#!/usr/bin/env python

from pprocess import start

def loop(channel, limit):
    print "loop to", limit
    i = channel.receive()
    while i < limit:
        print i
        i = channel.receive()
    channel.send("Done")

if __name__ == "__main__":
    limit = 100
    channel = start(loop, limit)
    for i in range(0, limit + 1):
        channel.send(i)
    print channel.receive()

# vim: tabstop=4 expandtab shiftwidth=4
