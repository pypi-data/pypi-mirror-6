#!/usr/bin/env python

"""
A simple example of serial computation using map-style processing.
See the simple_pmap.py program for the corresponding parallel version.
"""

import time
#import random

# Array size.

N = 10
delay = 1

# Work function.

def calculate(t):

    "A supposedly time-consuming calculation on 't'."

    i, j = t
    #time.sleep(delay * random.random())
    time.sleep(delay)
    return i * N + j

# Main program.

if __name__ == "__main__":

    t = time.time()

    # Initialise an array.

    sequence = []
    for i in range(0, N):
        for j in range(0, N):
            sequence.append((i, j))

    # Perform the work.

    results = map(calculate, sequence)

    # Show the results.

    for i in range(0, N):
        for result in results[i*N:i*N+N]:
            print result,
        print

    print "Time taken:", time.time() - t

# vim: tabstop=4 expandtab shiftwidth=4
