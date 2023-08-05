#!/usr/bin/env python

"""
A simple example of parallel computation using exchanges, managed callables and
persistent communications.
"""

import pprocess
import time
#import random
import sys

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
    return (i, j, i * N + j)

class MyExchange(pprocess.Exchange):

    "Parallel convenience class containing the array assignment operation."

    def store_data(self, ch):
        i, j, result = ch.receive()
        self.D[i*N+j] = result

class MyPersistentExchange(pprocess.PersistentExchange):

    "A persistent exchange."

    def store_data(self, ch):
        self.D[:] = ch.receive()

# Main computation.

def task():

    # Initialise the communications exchange with a limit on the number of
    # channels/processes.

    exchange = MyExchange(limit=limit)

    # Initialise an array - it is stored in the exchange to permit automatic
    # assignment of values as the data arrives.

    results = exchange.D = [0] * N * N

    # Wrap the calculate function and manage it.

    calc = exchange.manage(pprocess.MakeParallel(calculate))

    # Perform the work.

    for i in range(0, N):
        for j in range(0, N):
            calc(i, j)

    # Wait for the results.

    exchange.finish()
    return results

# Main program.

if __name__ == "__main__":

    t = time.time()

    # Initialise an array - it is stored in the exchange to permit automatic
    # assignment of values as the data arrives.

    results = [0] * N * N

    if "--reconnect" not in sys.argv:

        # Initialise the persistent exchange with a single process for the main
        # computation.

        exchange = MyPersistentExchange(limit=1)

        # Wrap the computation and manage it.

        ptask = exchange.manage("task.socket", pprocess.MakeParallel(task))

        # Perform the work.

        ptask()

        # Close down the exchange.

        del exchange
        print "Closed original exchange."

    if "--start" not in sys.argv:

        # Open another exchange.

        print "Opening new exchange."
        exchange = MyPersistentExchange(limit=1)
        exchange.D = results

        # Reconnect to the task.

        exchange.connect("task.socket")

        # Wait for the results.

        print "Waiting for persistent results"
        exchange.finish()

        # Show the results.

        for i in range(0, N):
            for result in results[i*N:i*N+N]:
                print result,
            print

        print "Time taken:", time.time() - t

# vim: tabstop=4 expandtab shiftwidth=4
