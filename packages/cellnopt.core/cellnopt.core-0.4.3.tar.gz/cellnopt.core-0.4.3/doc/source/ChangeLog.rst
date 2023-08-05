ChangeLog
=================

.. rubric:: revision 0.4.2

* fix tests
* add or move modules into ./io directory
* cnograph: fix split_node function for AND gates
* cnograph: prevent compression to compress nodes that would lead to multiedge ambiguity.
* cnograph: can accept as input a networkx graph or any instance that contains reacID attribute. 
* cnograph: operator + keeps track of the _stimuli, _signals, _inhibitors  attributes.
* nonc: module usees signals and stimuli parameters instead of cnolist
* move SIF files from ./test directory to share/directory and improved test
  suite
* sif: empty lines may now be present in the SIF. input can be any instance that
  contains a reacID attriute. ands convertion may now fail (if the input
  contains incorrect ANDs).

.. rubric:: revision 0.4.1

* cnograph: fixed bug in compression to keep orphans if there are
  stimuli,inhibitors or signals. + Add properties to get stimuli, inhibitors,
  signals list


.. rubric:: revision 0.4.0

* First release of pypi

.. rubric:: revision 0.3.0

* cnograph stabalised
* normalisation class added
* tutorial done + documentation

.. rubric:: revision 0.2.0

* cnograph and sif modules are still in progress but ready to use
* test coverage of 80%



.. rubric:: revision 0.1.0

* add bunch of modules:
    * cnograph, cutnonc, compression
    * converter modules:
        * converter
        * sif2asp
        * adj2sif
        * sop2sif
    * readers:
        * metabolites
        * reactions
        * sif, midas, metabolites
        * kinexus
    * analysis





