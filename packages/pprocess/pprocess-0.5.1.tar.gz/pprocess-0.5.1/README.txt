Introduction
------------

The pprocess module provides elementary support for parallel programming in
Python using a fork-based process creation model in conjunction with a
channel-based communications model implemented using socketpair and poll. On
systems with multiple CPUs or multicore CPUs, processes should take advantage
of as many CPUs or cores as the operating system permits.

Tutorial
--------

The tutorial provides some information about the examples described below.
See the docs/tutorial.html file in the distribution for more details.

Reference
---------

A description of the different mechanisms provided by the pprocess module can
be found in the reference document. See the docs/reference.html file in the
distribution for more details.

Quick Start
-----------

Try running the simple examples. For example:

PYTHONPATH=. python examples/simple_create.py

(These examples show in different ways how limited number of processes can be
used to perform a parallel computation. The simple.py, simple1.py, simple2.py
and simple_map.py programs are sequential versions of the other programs.)

The following table summarises the features used in the programs:

Program (.py)         pmap  MakeParallel manage start create Map Queue Exchange
-------------         ----  ------------ ------ ----- ------ --- ----- --------
simple_create_map                                     Yes    Yes
simple_create_queue                                   Yes        Yes
simple_create                                         Yes              Yes
simple_managed_map          Yes          Yes                 Yes
simple_managed_queue        Yes          Yes                     Yes
simple_managed              Yes          Yes                           Yes
simple_pmap           Yes
simple_pmap_iter      Yes
simple_start_queue          Yes                 Yes              Yes
simple_start                                    Yes                    Yes

The simplest parallel programs are simple_pmap.py and simple_pmap_iter.py
which employ the pmap function resembling the built-in map function in
Python.

Other simple programs are those employing the Queue class, together with those
using the manage method which associates functions or callables with Queue or
Exchange objects for convenient invocation of those functions and the
management of their communications.

The most technically involved program is simple_start.py which uses the
Exchange class together with a calculation function which is aware of the
parallel environment and which communicates over the supplied communications
channel directly to the creating process.

It should be noted that with the exception of simple_start.py, those examples
employing calculation functions (as opposed to doing a calculation inline in a
loop body) all use MakeParallel to make those functions parallel-aware, thus
permitting the conversion of "normal" functions to a form usable in the
parallel environment.

Reusable Processes
------------------

An additional example not listed above, simple_managed_map_reusable.py,
employs the MakeReusable class instead of MakeParallel in order to demonstrate
reusable processes and channels:

PYTHONPATH=. python examples/simple_managed_map_reusable.py

Continuous Process Communications
---------------------------------

Another example not listed above, simple_continuous_queue.py, employs
continuous communications to monitor output from created processes:

PYTHONPATH=. python examples/simple_continuous_queue.py

Persistent Processes
--------------------

A number of persistent variants of some of the above examples employ a
persistent or background process which can be started by one process and
contacted later by another in order to collect the results of a computation.
For example:

PYTHONPATH=. python examples/simple_persistent_managed.py --start
PYTHONPATH=. python examples/simple_persistent_managed.py --reconnect

PYTHONPATH=. python examples/simple_background_queue.py --start
PYTHONPATH=. python examples/simple_background_queue.py --reconnect

PYTHONPATH=. python examples/simple_persistent_queue.py --start
PYTHONPATH=. python examples/simple_persistent_queue.py --reconnect

Parallel Raytracing with PyGmy
------------------------------

The PyGmy raytracer modified to use pprocess can be run to investigate the
potential for speed increases in "real world" programs:

cd examples/PyGmy
PYTHONPATH=../..:. python scene.py

(This should produce a file called test.tif - a TIFF file containing a
raytraced scene image.)

Examples from the Concurrency SIG
---------------------------------

The special interest group (SIG) for concurrency in Python proposed a
particular application as a showcase for concurrency libraries. Two examples
are included which demonstrate pprocess and the use of continuous processes to
implement the application concerned:

PYTHONPATH=. python examples/concurrency-sig/bottles.py
PYTHONPATH=. python examples/concurrency-sig/bottles_heartbeat.py

Test Programs
-------------

There are some elementary tests:

PYTHONPATH=. python tests/create_loop.py
PYTHONPATH=. python tests/start_loop.py

(Simple loop demonstrations which use two different ways of creating and
starting the parallel processes.)

PYTHONPATH=. python tests/start_indexer.py <directory>

(A text indexing demonstration, where <directory> should be a directory
containing text files to be indexed, although HTML files will also work well
enough. After indexing the files, a prompt will appear, words or word
fragments can be entered, and matching words and their locations will be
shown. Run the program without arguments to see more information.)

Contact, Copyright and Licence Information
------------------------------------------

The current Web page for pprocess at the time of release is:

http://www.boddie.org.uk/python/pprocess.html

The author can be contacted at the following e-mail address:

paul@boddie.org.uk

Copyright and licence information can be found in the docs directory - see
docs/COPYING.txt, docs/lgpl-3.0.txt and docs/gpl-3.0.txt for more information.

For the PyGmy raytracer example, different copyright and licence information
is provided in the docs directory - see docs/COPYING-PyGmy.txt and
docs/LICENCE-PyGmy.txt for more information.

Dependencies
------------

This software depends on standard library features which are stated as being
available only on "UNIX"; it has only been tested repeatedly on a GNU/Linux
system, and occasionally on systems running OpenSolaris.

New in pprocess 0.5.1 (Changes since pprocess 0.5)
--------------------------------------------------

  * Added IOError handling when processes exit apparently without warning.

New in pprocess 0.5 (Changes since pprocess 0.4)
------------------------------------------------

  * Added proper support in the Exchange class for continuous communications
    between processes, providing examples: simple_continuous_queue.py and the
    concurrency-sig directory.
  * Changed the Map class to permit incremental access to received results
    from completed parts of the sequence of inputs, also adding an iteration
    interface.
  * Added an example, simple_pmap_iter.py, to demonstrate iteration over maps.
  * Fixed the get_number_of_cores function to work with /proc/cpuinfo where
    the "physical id" field is missing.
  * Tidied the Exchange class, adding distinct status methods: unfinished and
    busy.

New in pprocess 0.4 (Changes since pprocess 0.3.1)
--------------------------------------------------

  * Added support for persistent/background processes.
  * Added a utility function to detect and return the number of processor
    cores available.
  * Added missing documentation stylesheet.
  * Added support for Solaris using pipes instead of socket pairs, since
    the latter do not apparently work properly with poll on Solaris.

New in pprocess 0.3.1 (Changes since pprocess 0.3)
--------------------------------------------------

  * Moved the reference material out of the module docstring and into a
    separate document, converting it to XHTML in the process.
  * Fixed the project name in the setup script.

New in pprocess 0.3 (Changes since parallel 0.2.5)
--------------------------------------------------

  * Added managed callables: wrappers around callables which cause them to be
    automatically managed by the exchange from which they were acquired.
  * Added MakeParallel: a wrapper instantiated around a normal function which
    sends the result of that function over the supplied channel when invoked.
  * Added MakeReusable: a wrapper like MakeParallel which can be used in
    conjunction with the newly-added reuse capability of the Exchange class in
    order to reuse processes and channels.
  * Added a Map class which attempts to emulate the built-in map function,
    along with a pmap function using this class.
  * Added a Queue class which provides a simpler iterator-style interface to
    data produced by created processes.
  * Added a create method to the Exchange class and an exit convenience
    function to the module.
  * Changed the Exchange implementation to not block when attempting to start
    new processes beyond the process limit: such requests are queued and
    performed as running processes are completed. This permits programs using
    the start method to proceed to consumption of results more quickly.
  * Extended and updated the examples. Added a tutorial.
  * Added Ubuntu Feisty (7.04) package support.

New in parallel 0.2.5 (Changes since parallel 0.2.4)
----------------------------------------------------

  * Added a start method to the Exchange class for more convenient creation of
    processes.
  * Relicensed under the LGPL (version 3 or later) - this also fixes the
    contradictory situation where the GPL was stated in the pprocess module
    (which was not, in fact, the intention) and the LGPL was stated in the
    documentation.

New in parallel 0.2.4 (Changes since parallel 0.2.3)
----------------------------------------------------

  * Set buffer sizes to zero for the file object wrappers around sockets: this
    may prevent deadlock issues.

New in parallel 0.2.3 (Changes since parallel 0.2.2)
----------------------------------------------------

  * Added convenient message exchanges, offering methods handling common
    situations at the cost of having to define a subclass of Exchange.
  * Added a simple example of performing a parallel computation.
  * Improved the PyGmy raytracer example to use the newly added functionality.

New in parallel 0.2.2 (Changes since parallel 0.2.1)
----------------------------------------------------

  * Changed the status testing in the Exchange class, potentially fixing the
    premature closure of channels before all data was read.
  * Fixed the PyGmy raytracer example's process accounting by relying on the
    possibly more reliable Exchange behaviour, whilst also preventing
    erroneous creation of "out of bounds" processes.
  * Added a removed attribute on the Exchange to record which channels were
    removed in the last call to the ready method.

New in parallel 0.2.1 (Changes since parallel 0.2)
--------------------------------------------------

  * Added a PyGmy raytracer example.
  * Updated copyright and licensing details (FSF address, additional works).

New in parallel 0.2 (Changes since parallel 0.1)
------------------------------------------------

  * Changed the name of the included module from parallel to pprocess in order
    to avoid naming conflicts with PyParallel.

Release Procedures
------------------

Update the pprocess __version__ attribute and the setup.py file version field.
Change the version number and package filename/directory in the documentation.
Update the release notes (see above).
Check the release information in the PKG-INFO file.
Tag, export.
Archive, upload.
Update PyPI.

Making Packages
---------------

To make Debian-based packages:

  1. Create new package directories under packages if necessary.
  2. Make a symbolic link in the distribution's root directory to keep the
     Debian tools happy:

     ln -s packages/ubuntu-hoary/python2.4-parallel-pprocess/debian/

     Or:

     ln -s packages/ubuntu-feisty/python-pprocess/debian/

  3. Run the package builder:

     dpkg-buildpackage -rfakeroot

  4. Locate and tidy up the packages in the parent directory of the
     distribution's root directory.
