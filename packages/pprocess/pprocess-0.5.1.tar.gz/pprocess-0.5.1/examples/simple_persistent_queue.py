#!/usr/bin/env python

"""
A simple example of parallel computation using persistent queues and
communications.
"""

import pprocess
import time
#import random
import sys

# Array size and a limit on the number of processes.

N = 10
limit = 2 # since N background processes will be used, this is reduced
delay = 1

# Work function and monitoring class.

def calculate(i, j):

    """
    A supposedly time-consuming calculation on 'i' and 'j'.
    """

    #time.sleep(delay * random.random())
    time.sleep(delay)
    return (i, j, i * N + j)

# Background computation.

def task(i):

    # Initialise the communications queue with a limit on the number of
    # channels/processes.

    queue = pprocess.Queue(limit=limit)

    # Initialise an array.

    results = [0] * N

    # Wrap the calculate function and manage it.

    calc = queue.manage(pprocess.MakeParallel(calculate))

    # Perform the work.

    print "Calculating..."
    for j in range(0, N):
        calc(i, j)

    # Store the results as they arrive.

    print "Finishing..."
    for i, j, result in queue:
        results[j] = result

    return i, results

# Main program.

if __name__ == "__main__":

    t = time.time()

    if "--reconnect" not in sys.argv:

        # Wrap the computation and manage it.

        ptask = pprocess.MakeParallel(task)

        for i in range(0, N):

            # Make a distinct callable for each part of the computation.

            ptask_i = pprocess.BackgroundCallable("task-%d.socket" % i, ptask)

            # Perform the work.

            ptask_i(i)

        # Discard the callable.

        del ptask
        print "Discarded the callable."

    if "--start" not in sys.argv:

        # Open a queue and reconnect to the task.

        print "Opening a queue."
        queue = pprocess.PersistentQueue()
        for i in range(0, N):
            queue.connect("task-%d.socket" % i)

        # Initialise an array.

        results = [0] * N

        # Wait for the results.

        print "Waiting for persistent results"
        for i, result in queue:
            results[i] = result

        # Show the results.

        for i in range(0, N):
            for result in results[i]:
                print result,
            print

        print "Time taken:", time.time() - t

# vim: tabstop=4 expandtab shiftwidth=4
