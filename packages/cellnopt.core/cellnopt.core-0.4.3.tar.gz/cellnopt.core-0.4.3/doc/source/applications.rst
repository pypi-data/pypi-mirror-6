.. _applications:

##############
MISC code
##############
.. contents::


.. topic:: miscellaneous

    This section provides piece of code that are not finalised but could be
    useful. 




Renames nodes in a graph and combining several graph
########################################################

:status: draft

This is a piece of code used to create a big network by combining  three times
the same network. 
For the renaming, you need networkx relabel_node function that returns a n graph. This is not
inline modification. The function expect a mapping of new names to the old ones,
which is done using a dict conversion of a list of tuples:

::

    # create a graph
    c1 = CNOGraph(a valid filename, midas name)
    c1.add_edge("A", "B", link="+")
    c1.add_edge("A", "C", link="+")
    # create duplicates with different names
    c2 = nx.relabel_nodes(c, dict([(x, x+"_a" )for x in c.nodes()]))
    c3 = nx.relabel_nodes(c, dict([(x, x+"_b" )for x in c.nodes()]))

    # create a full network with all previous edges/nodes
    c = c1+c2+c3
    #c.midas = 

    # finally add cross-talk edges from subPKN1 to 2 and 2 to 3
    Nedges = 10

    nodes1 = random.sample(c1.nodes(), Nedges)
    nodes2 = random.sample(c2.nodes(), Nedges)
    for n1, n2 in zip(nodes1, nodes2):
        if n1!=n2:
            c.add_edge(n1,n2, link="+")
    nodes1 = random.sample(c2.nodes(), Nedges)
    nodes2 = random.sample(c3.nodes(), Nedges)
    for n1, n2 in zip(nodes1, nodes2):
        if n1!=n2:
            c.add_edge(n1,n2, link="+")

    #c.midas = 
    c._signals += [x+"_a" for x in c1.midas.cnolist.namesSignals]
    c._signals += [x+"_b" for x in c1.midas.cnolist.namesSignals]
    c._stimuli += [x+"_b" for x in c1.midas.cnolist.namesStimuli]
    c._stimuli += [x+"_a" for x in c1.midas.cnolist.namesStimuli]
    c._inhibitors += [x+"_a" for x in c1.midas.cnolist.namesInhibitorsShort]
    c._inhibitors += [x+"_b" for x in c1.midas.cnolist.namesInhibitorsShort]

    c._node_set_attributes()
    c.plotdot()
    nx.write_dot(c, "test.dot")


combine with cellnopt.wrapper
==============================

::

    from cellnopt.core import *
    from cellnopt.wrapper import *
    import tempfile

    f1 = tempfile.NamedTemporaryFile(delete=False)
    midasFilename = cnodata("MD-ToyMMB.csv")

    c = CNOGraph(cnodata("PKN-ToyMMB.sif"), cnodata("MD-ToyMMB.csv"))
    # play with the SIF file and save it
    c.export2sif(f1.name)

    b = CNORbool(f1.name, midasFilename)
    b.preprocessing()
    b.gaBinaryT1()

    # the optimised model
    c2 = CNOGraph()
    reactions = list(b.expmodel.reacID)
    bString = list(b.T1opt.bString)
    s = SIF()
    for r in reactions: s.add_reaction(r)
    c2 = CNOGraph(s, midasFilename)
    

    # TODO: be able to add AND gate in the SIF or CNOGraph data structure

    # Need to color the edges now and/or add a label

