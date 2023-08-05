.. _quickstart:

Quick Start
#################


The CNOGraph data structure
===============================

The CNOGraph data structures is a DiGraph data structures that takes as input a
SIF file (see later) and **possibly** a MIDAS file that contains data values
associated to some nodes contained in the SIF file.

However, you can play without any input files since the CNOGraph data structure
is a Digraph. However, there is a restriction on the type of edges that can be
only of two types: "+" for activation and "-" for inhibition.


.. plot::
    :include-source:
    :width: 30%

    from cellnopt.core import *
    c1 = CNOGraph()
    c1.add_edge("A","B", link="+")
    c1.add_edge("A","C", link="-")
    c1.plotdot()

The Digraph is intended to be associated to a MIDAS file. If so, it will
identifies the ligands, inhibitors and measured values with specific colors:
green, red and blue respectively. If you don't have a MIDAS file, you can still
specificy manually the colors:

.. plot::
    :include-source:
    :width: 30%

    from cellnopt.core import *
    c1 = CNOGraph()
    c1.add_edge("A","B", link="+")
    c1.add_edge("A","C", link="-")
    c1._stimuli = ["A"]
    c1._inhibitors = ["B"]
    c1._signals = ["C"]
    c1.plotdot()

There are many operators available and readers can refer to
:class:`cellnopt.core.cnograph.CNOGraph` for more examples.


CNOGraph as a data structure to manipulate SIF/MIDAS file
------------------------------------------------------------

The common data structure :class:`~cellnopt.core.cnograph.CNOGraph` can also take as input a SIF instance 
and a MIDAS instance (or filenames). The latter is optional. ::

    c = CNOGraph(s, m)

This data structure has many methods inherited from networkx.DiGraph class and many algorithms can be applied. 
The input SIF file is used to build the topology of the graph. The input MIDAS
file if provided is used to set the color of the nodes and edges when calling
plotting functions. Besides, with the information contained in the MIDAS file,
functions similar to those in CellNOptR can be applied (pre processing functions
to add AND gates, compress  nodes that are not measured; see :ref:`user_guide`  for details). 

As an example, you can plot the graph using :meth:`~cellnopt.core.cnograph.CNOGraph.plotdot`:

.. plot::
    :width: 80%
    :include-source:

    from cellnopt.core import *
    s = SIF(get_share_file("PKN-Test.sif"))
    m = MIDASReader(get_share_file("MD-Test.csv"))
    c = CNOGraph(s, m)
    c.plotdot(legend=True)


The CNOGraph structure provides methods to perform processing dedicated to CellNOpt analysis. This processing are made of three steps:

    #. removal of non observable and non controlable 
    #. compress nodes that are not measured, not stimuli, not inhibited.
    #. add AND gates

See :meth:`cellnopt.core.cnograph.CNOGraph` class for details.

Let us apply these 3 steps and plot the graph again:


.. plot::
    :width: 80%
    :include-source:

    from cellnopt.core import *
    s = SIF(get_share_file("PKN-Test.sif"))
    m = MIDASReader(get_share_file("MD-Test.csv"))
    c = CNOGraph(s, m)
    c.preprocessing()
    c.plotdot()




Read data files in SIF and MIDAS formats
============================================
To begin, the easiest is to import the entire package to get access to all classes and functions::

    >>> from cellnopt.core import *

In order to use some of the functionalities, we need some sample data sets. We will play with a protein-protein interactions network coded in 
(:ref:`sif` format) and a data set that stores signalling data stored in :ref:`midas` format. 
The package **cellnopt.core** provides samples to play with, which can be obtained using the :func:`cnodata` function (part of another package called :func:`cellnopt.data.tools.cnodata` but linked within cellnopt.core for convenience)::

    >>> sifFilename = cnodata("PKN-ToyPB.sif")
    >>> midasFilename = cnodata("MD-ToyPB.csv")

Alternatively, you can also use :func:`~cellnopt.core.get_share_file` to obtain test samples provided within **cellnopt.core** package itself::

    >>> from cellnopt.core import get_share_file
    >>> get_share_file("PKN-Test.sif")

Once you've chosen a filename, you can create a :class:`~cellnopt.core.sif.SIF` instance as follows::

    >>> s = SIF(sifFilename)

and a :class:`~cellnopt.core.midas.MIDASReader` instance as follows::

    >>> m = MIDASReader(midasFilename)

These two objects **m** and **s** have many methods and users should refer to
the reference guide for an exhaustive documentation. As an example, we can plot
the data contained in the MIDAS file::

    >>> m.plotMSEs()
    >>> m.plotExp()

.. plot::
    :width: 80%

    from cellnopt.core import *
    midasFilename = get_share_file("MD-Test.csv")
    m = MIDASReader(midasFilename)
    m.plotMSEs()
    m.plotExp()



