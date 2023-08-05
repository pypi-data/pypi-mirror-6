

#############################
CellNOpt.CORE documentation
#############################

.. topic:: cellnopt.core

    .. image:: network.png
        :width: 30%


Motivation 
###########


**Cellnopt.core** is a pure Python library that provides core functions to manipulate signalling data. It provides functions to create and manipulate networks that can be used later on with MIDAS files (phosphorylation measurements). You can read/write data formats such as :ref:`sif` and :ref:`midas` that are used in `CellNOptR <http://bioconductor.org/packages/release/bioc/html/CellNOptR.html>`_.

It does not provide any logical formalism to simulate or optimise the network to
the data. It is rather intended to be a package dedicated to the pre and post
processing of signalling pathways. 


Installation
###################

Since **cellnopt.core** is available on `PyPi <http://pypi.python.org/>`_, one of the following commands should install the package and its dependencies automatically:: 

    easy_install cellnopt.core
    pip install cellnopt.core



User guide
##################


.. toctree::
    :maxdepth: 2
    :numbered:

    quickstart.rst
    userguide.rst
    applications.rst

References
##################


.. toctree::
    :maxdepth: 2
    :numbered:

    references




.. toctree::

    biblio.rst


.. toctree::

    todo.rst
    ChangeLog.rst
    authors.rst
    contribute
