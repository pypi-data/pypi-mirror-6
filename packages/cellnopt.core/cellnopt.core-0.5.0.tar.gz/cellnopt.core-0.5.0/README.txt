The package cellnopt.core provides tools to manipulate networks and data related
to signalling pathways. It provides I/O functions for SIF, MIDAS, SOP formats 
and a convenient graph data structure called CNOGraph.

Here is a simple example that creates a graph and plots it using dot/graphviz::

    from cellnopt.core import *
    c = CNOGraph()
    c.add_reaction("A=B")
    c.add_reaction("A+B=C")
    c.plotdot()

For a full documentation, see the sphinx documentation in the ./doc directory.

Installation note
-------------------

**cellnopt.core** has a dependencies on **pandas**, which requires cython. So,
you must install cython first. 

All other dependencies should be installed automatically (networkx, numpy, matplotlib)

::

    pip install cython
    pip install cellnopt.core
