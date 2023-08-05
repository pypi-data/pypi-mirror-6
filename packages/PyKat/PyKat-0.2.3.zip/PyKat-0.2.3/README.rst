PyKat
===========

PyKat is a wrapper for using FINESSE (http://www.gwoptics.org/finesse).
It aims to provide a Python toolset for automating more complex tasks
as well as providing a GUI for manipulating and viewing simulation
setups.


Finesse Test Server
------------

A Flask based website that runs the Finesse test suites is included in PyKat. This can be hosted in Apache or run as a development server for quick testing on a system. This is a developer tool for testing FINESSE against a selection of known test cases.

Prerequistes:
    Flask
    Numpy
    
Command to start server:

::
  python -m pykat.test.web_server --path=[path to create website] --port=[HTTP port] --git-bin=[path to git binary]

The website can then be accessed in a web browser at the address: localhost:[port]