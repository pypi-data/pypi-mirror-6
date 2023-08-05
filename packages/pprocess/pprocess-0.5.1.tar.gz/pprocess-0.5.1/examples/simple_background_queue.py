#!/usr/bin/env python

"""
A simple example of parallel computation using a queue, background callables and
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

# Main computation.

def task():

    # Initialise the communications queue with a limit on the number of
    # channels/processes.

    queue = pprocess.Queue(limit=limit)

    # Initialise an array.

    results = [0] * N * N

    # Wrap the calculate function and manage it.

    calc = queue.manage(pprocess.MakeParallel(calculate))

    # Perform the work.

    print "Calculating..."
    for i in range(0, N):
        for j in range(0, N):
            calc(i, j)

    # Store the results as they arrive.

    print "Finishing..."
    for i, j, result in queue:
        results[i*N+j] = result

    return results

# Main program.

if __name__ == "__main__":

    t = time.time()

    if "--reconnect" not in sys.argv:

        # Wrap the computation and manage it.

        ptask = pprocess.BackgroundCallable("task.socket", pprocess.MakeParallel(task))

        # Perform the work.

        ptask()

        # Discard the callable.

        del ptask
        print "Discarded the callable."

    if "--start" not in sys.argv:

        # Open a queue and reconnect to the task.

        print "Opening a queue."
        queue = pprocess.BackgroundQueue("task.socket")

        # Wait for the results.

        print "Waiting for persistent results"
        for results in queue:
            pass # should only be one element

        # Show the results.

        for i in range(0, N):
            for result in results[i*N:i*N+N]:
                print result,
            print

        print "Time taken:", time.time() - t

# vim: tabstop=4 expandtab shiftwidth=4
