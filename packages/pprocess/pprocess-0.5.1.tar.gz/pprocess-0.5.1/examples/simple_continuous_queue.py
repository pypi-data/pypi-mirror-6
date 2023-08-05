#!/usr/bin/env python

"""
A simple example of parallel computation using a queue and continuous
communications.
"""

import pprocess
import time
#import random

# Array size and a limit on the number of processes.

N = 10
limit = 10
delay = 1

# Work function.

def calculate(ch, i):

    """
    A supposedly time-consuming calculation on 'i'.
    """

    for j in range(0, N):
        #time.sleep(delay * random.random())
        time.sleep(delay)
        ch.send((i, j, i * N + j))

# Main program.

if __name__ == "__main__":

    t = time.time()

    # Initialise the communications queue with a limit on the number of
    # channels/processes.

    queue = pprocess.Queue(limit=limit, continuous=1)

    # Initialise an array.

    results = [0] * N * N

    # Manage the calculate function.

    calc = queue.manage(calculate)

    # Perform the work.

    print "Calculating..."
    for i in range(0, N):
        calc(i)

    # Store the results as they arrive.

    print "Finishing..."
    for i, j, result in queue:
        results[i*N+j] = result

    # Show the results.

    for i in range(0, N):
        for result in results[i*N:i*N+N]:
            print result,
        print

    print "Time taken:", time.time() - t

# vim: tabstop=4 expandtab shiftwidth=4
