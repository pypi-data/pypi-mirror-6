#!/usr/bin/env python

from pprocess import create

limit = 100
channel = create()
if channel.pid == 0:
    i = channel.receive()
    while i < limit:
        print i
        i = channel.receive()
    channel.send("Done")
else:
    for i in range(0, limit + 1):
        channel.send(i)
    print channel.receive()

# vim: tabstop=4 expandtab shiftwidth=4
