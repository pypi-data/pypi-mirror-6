#!/usr/bin/env python

"""
A simple example of parallel computation using map-style processing.
"""

import pprocess
import time
#import random

# Array size and a limit on the number of processes.

N = 10
limit = 10
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

    results = pprocess.pmap(calculate, sequence, limit=limit)

    # Show the results.

    for i, result in enumerate(results):
        print result,
        if i % N == N - 1:
            print

    print "Time taken:", time.time() - t

# vim: tabstop=4 expandtab shiftwidth=4
