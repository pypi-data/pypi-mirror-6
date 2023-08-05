#!/usr/bin/env python

"""
Example of concurrency when reading files.

See: http://wiki.python.org/moin/Concurrency/99Bottles

Based on the generator version.
"""

import pprocess
import time
import re

def follow(ch, fname):
    f = file(fname)
    f.seek(0,2) # go to the end
    while True:
        l = f.readline()
        if not l: # no data
            time.sleep(.1)
        else:
            ch.send(l)

def grep(ch, lines, pattern):
    regex = re.compile(pattern)
    for l in lines:
        if regex.match(l):
            ch.send(l)

def printer(lines):
    for l in lines:
        print l.strip()

def multigrep(ch, pattern):
    queue = pprocess.Queue(continuous=1)
    multifollow = queue.manage(follow)

    # Launch concurrent following activities.
    multifollow('/tmp/test') # '/var/log/system.log'
    multifollow('/tmp/test2')
    multifollow('/tmp/test3')

    # Handle incoming lines using the specified pattern.
    grep(ch, queue, pattern)

# Permit multiple simultaneous grep activities.
queue = pprocess.Queue(continuous=1)
multigrep = queue.manage(multigrep)

# Launch concurrent grep activities.
multigrep(".*pants.*")
multigrep(".*trousers.*")
multigrep(".*shorts.*")

# Print incoming lines.
p = printer(queue)

# vim: tabstop=4 expandtab shiftwidth=4
