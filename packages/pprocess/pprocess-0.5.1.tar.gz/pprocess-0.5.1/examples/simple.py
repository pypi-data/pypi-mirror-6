#!/usr/bin/env python

"""
A simple example of a computation performed sequentially.
"""

import time
#import random

# Array size.

N = 10
delay = 1

# Main program.

if __name__ == "__main__":

    t = time.time()

    # Initialise an array.

    results = [0] * N * N

    # Perform the work.

    print "Calculating..."
    for i in range(0, N):
        for j in range(0, N):
            #time.sleep(delay * random.random())
            time.sleep(delay)
            results[i*N+j] = i * N + j

    # Show the results.

    for i in range(0, N):
        for result in results[i*N:i*N+N]:
            print result,
        print

    print "Time taken:", time.time() - t

# vim: tabstop=4 expandtab shiftwidth=4
