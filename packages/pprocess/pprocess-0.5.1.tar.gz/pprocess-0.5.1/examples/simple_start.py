#!/usr/bin/env python

"""
A simple example of parallel computation using message exchanges directly.
"""

import pprocess
import time
#import random

# Array size and a limit on the number of processes.

N = 10
limit = 10
delay = 1

# Work function and monitoring class.

def calculate(ch, i, j):

    """
    A supposedly time-consuming calculation on 'i' and 'j', using 'ch' to
    communicate with the parent process.
    """

    #time.sleep(delay * random.random())
    time.sleep(delay)
    ch.send((i, j, i * N + j))

class MyExchange(pprocess.Exchange):

    "Parallel convenience class containing the array assignment operation."

    def store_data(self, ch):
        i, j, result = ch.receive()
        self.D[i*N+j] = result

# Main program.

if __name__ == "__main__":

    t = time.time()

    # Initialise the communications exchange with a limit on the number of
    # channels/processes.

    exchange = MyExchange(limit=limit)

    # Initialise an array - it is stored in the exchange to permit automatic
    # assignment of values as the data arrives.

    results = exchange.D = [0] * N * N

    # Perform the work.

    print "Calculating..."
    for i in range(0, N):
        for j in range(0, N):
            exchange.start(calculate, i, j)

    # Wait for the results.

    print "Finishing..."
    exchange.finish()

    # Show the results.

    for i in range(0, N):
        for result in results[i*N:i*N+N]:
            print result,
        print

    print "Time taken:", time.time() - t

# vim: tabstop=4 expandtab shiftwidth=4
