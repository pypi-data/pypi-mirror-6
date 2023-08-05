#!/usr/bin/env python

"""
A simple example of parallel computation using a map and the create function.

NOTE: We could use the with statement in the innermost loop to package the
NOTE: try...finally functionality.
"""

import pprocess
import time
#import random

# Array size and a limit on the number of processes.

N = 10
limit = 10
delay = 1

# Main program.

if __name__ == "__main__":

    t = time.time()

    # Initialise the results using a map with a limit on the number of
    # channels/processes.

    results = pprocess.Map(limit=limit)

    # Perform the work.
    # NOTE: Could use the with statement in the loop to package the
    # NOTE: try...finally functionality.

    print "Calculating..."
    for i in range(0, N):
        for j in range(0, N):
            ch = results.create()
            if ch:
                try: # Calculation work.

                    #time.sleep(delay * random.random())
                    time.sleep(delay)
                    ch.send(i * N + j)

                finally: # Important finalisation.

                    pprocess.exit(ch)

    # Show the results.

    for i in range(0, N):
        for result in results[i*N:i*N+N]:
            print result,
        print

    print "Time taken:", time.time() - t

# vim: tabstop=4 expandtab shiftwidth=4
