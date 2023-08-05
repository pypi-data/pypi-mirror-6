#!/usr/bin/env python

"A simple text indexing activity."

from pprocess import start, Exchange
from Dict import Indexer, Searcher, Parser
import os

def apply_parser(channel, filenames, delay=None):

    """
    Apply the parser, returning results through the given 'channel', processing
    the files with the given 'filenames', and imposing a optional 'delay' in the
    parser to simulate heavy processing.
    """

    #print "Parsing", filenames
    parser = Parser(filenames, delay=delay)
    parser.send_entries(channel)
    #print "Done", filenames

def fill_window(filenames, i, window_size, exchange, slice_size, delay=None):

    """
    Fill a "window" of channels using the given 'filenames', starting from index
    'i' in that list, choosing a number of channels limited to 'window_size' and
    adding those channels to the given 'exchange'. Each channel will be
    employed by a parser which will be given a number of filenames limited to
    'slice_size', and which will be requested to wait periodically if specified
    by the optional 'delay'.
    """

    number = 0
    limit = len(filenames)
    active = len(exchange.active())
    while i < limit and number < window_size - active:
        j = i + slice_size
        channel = start(apply_parser, filenames[i:j], delay)
        exchange.add(channel)
        i = j
        number += 1
    return i

def get_searcher(filenames, window_size, slice_size, delay=None):

    """
    Get a searcher object, providing searching on the contents of the given
    'filenames', employing a 'window_size' and 'slice_size' as parameters to
    respectively control the number of monitored channels in the exchange, and
    the number of filenames given to each created process. The optional 'delay'
    is used to simulate heavy processing in each created process.
    """

    master_index = Indexer()

    # Start indexing by filling a window with channels.

    exchange = Exchange()
    i = fill_window(filenames, 0, window_size, exchange, slice_size, delay)

    # Start listening for responses.

    while exchange.active():
        #print "(%d)" % len(exchange.active()),
        for channel in exchange.ready():
            entry = channel.receive()
            master_index.add_entry(entry)

        i = fill_window(filenames, i, window_size, exchange, slice_size, delay)

    # Provide a search interface.

    #print
    return Searcher(master_index.get_index())

if __name__ == "__main__":
    import sys, os

    # Get the parameters.

    try:
        directory = sys.argv[1]
    except IndexError:
        print "Please specify a directory where text files reside."
        print "To investigate other performance factors, you can also specify"
        print "a window size (eg. 1, 5, 10, ...) indicating the number of"
        print "channels/processes being used, a slice size (eg. 5, 10, ...)"
        print "indicating the number of filenames given to each created process"
        print "and a time delay to simulate heavy processing in each created"
        print "process (eg. 0.5, 1, ...)."
        sys.exit(1)

    if len(sys.argv) > 2:
        window_size = int(sys.argv[2])
    else:
        window_size = 4

    if len(sys.argv) > 3:
        slice_size = int(sys.argv[3])
    else:
        slice_size = 5

    if len(sys.argv) > 4:
        delay = float(sys.argv[4])
    else:
        delay = None

    # Build a list of filenames.

    filenames = [os.path.join(directory, filename) for filename in os.listdir(directory)]
    filenames = [filename for filename in filenames if os.path.isfile(filename)]

    # Get a searcher using an index built in parallel.

    searcher = get_searcher(filenames, window_size, slice_size, delay)

    # Present a user interface.

    if "--noprompt" not in sys.argv:
        while 1:
            print "Pattern:",
            pattern = raw_input()
            print searcher.find(pattern)

# vim: tabstop=4 expandtab shiftwidth=4
