#!/usr/bin/env python

"""
A simple example of parallel computation using a map and managed callables.
"""

import pprocess
import time
#import random

# Array size and a limit on the number of processes.

N = 10
limit = 10
delay = 1

# Work function and monitoring class.

def calculate(i, j):

    """
    A supposedly time-consuming calculation on 'i' and 'j'.
    """

    #time.sleep(delay * random.random())
    time.sleep(delay)
    return i * N + j

# Main program.

if __name__ == "__main__":

    t = time.time()

    # Initialise the results using a map with a limit on the number of
    # channels/processes.

    results = pprocess.Map(limit=limit)

    # Wrap the calculate function and manage it.

    calc = results.manage(pprocess.MakeParallel(calculate))

    # Perform the work.

    print "Calculating..."
    for i in range(0, N):
        for j in range(0, N):
            calc(i, j)

    # Show the results.

    for i in range(0, N):
        for result in results[i*N:i*N+N]:
            print result,
        print

    print "Time taken:", time.time() - t

# vim: tabstop=4 expandtab shiftwidth=4
