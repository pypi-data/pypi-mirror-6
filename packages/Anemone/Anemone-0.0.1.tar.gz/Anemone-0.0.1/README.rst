Anemone
=======

Anemone is an analysis monitor written in Python. The typical use cases is monitoring of long 
running programs on remote machines. Anemone lets the long running program (scientific analysis or 
any other type of long running program) create reports which can be continously updated through the
running of the analysis. Anemone will run in a separate thread and talk to interested listeners,
typically plotting programs on remote machines. These programs can get a list of reports and
continously plot the evolvolution of the reported variables.

Anemone includes a graphical user interface (GUI) that can connect to a running analysis and show
a list of monitors. The monitors can be plotted and the plots will update automatically.

Currently only 2D plot reports are supported, but more advanced reports are also planned.

Usage
-----

An example of using Anemone in an application is included in the repository. The analysis program
will publish the monitors on a TCP port, via local IPC over a unix domain sockets or any other 
transport supported by the currently installed version of ZeroMQ.

If the example program communicates over IPC via the file ``my_com`` then you can connect to it
with the GUI and inspect the progress of the analysis live by running::

    python -m anemone wxgui ipc://my_com

You can connect mulitple GUI programs and connect/reconnect as often as you like. You can even
connect before the analysis program has started. The GUI will try to connect each second until the
analysis program responds.

Security
--------

The current proof-of-concept version of Anemone communicates over ZeroMQ via Python pickles which
is NOT secure! Do not use Anemone in an open network without replacing the pickles with some other
serialization format!

Installation
------------

Anemone is a Python package. It has been tested with Python 2.7 on Ubuntu Linux and requires the 
ZeroMQ Python bindings, wxPython and matplotlib to be available. No installation is required besides
making sure the ``anemone`` package is on the PYTHONPATH.

Version and stability
---------------------

The current version of Anemone is 0.01 and should be treated as a proof of concept and not as
production quality software.

Copyright and license
---------------------

Anemone is copyright Tormod Landet, 2014. Anemone is licensed under the Apache 2.0 license.
