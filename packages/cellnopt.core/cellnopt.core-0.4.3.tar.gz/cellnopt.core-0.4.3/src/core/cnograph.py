# -*- python -*-
#
#  This file is part of the cinapps.tcell package
#
#  Copyright (c) 2012-2013 - EMBL-EBI
#
#  File author(s): Thomas Cokelaer (cokelaer@ebi.ac.uk)
#
#  Distributed under the GLPv3 License.
#  See accompanying file LICENSE.txt or copy at
#      http://www.gnu.org/licenses/gpl-3.0.html
#
#  website: www.cellnopt.org
#
##############################################################################
"""

.. testsetup:: addition

    from cellnopt.core import *
    c1 = CNOGraph()
    c1.add_edge("A","B", link="+")
    c1.add_edge("A","C", link="+")
    c2 = CNOGraph()
    c2.add_edge("A","E", link="+")
    c2.add_edge("C","E", link="+")



"""
from __future__ import print_function
#from __future__ import unicode_literals
import os
import copy
import tempfile
import itertools
import subprocess


import pylab
import networkx as nx

from easydev import Logging

# cellnopt modules
from cellnopt.core.sif import SIF
from cellnopt.core.midas import MIDASReader

__all__ = ["CNOGraph", "CNOGraphMultiEdges", "CNOGraphAttributes"]


class Attributes(dict):
    """Simple dictionary to handle attributes (nodes or eges)"""
    def __init__(self, color, **kargs):
        self['color'] = color
        for k,v in kargs.iteritems():
            self[k] = v


class EdgeAttributes(Attributes):
    def __init__(self, penwidth=1, color="black", arrowhead="normal", **kargs):
        super(EdgeAttributes, self).__init__(color=color, **kargs)
        self['penwidth'] = penwidth
        self['arrowhead'] = arrowhead

class NodeAttributes(dict):
    """A class to manage attributes of the nodes (graphviz attribute)

    Used by the :class:`CNOGraph`.

    ::

        >>> a = Attributes(color="red", fillcolor="white")
        >>> assert a['color'] == "red"
        True

    """
    def __init__(self, color="black", fillcolor="white", shape="rectangle",
                 style="filled,bold", **kargs):
        """

        :param color: color of the border
        :param fillcolor: color inside the shape
        :param shape color inside the shape
        :param style: color inside the shape
        """
        super(NodeAttributes, self).__init__(color=color, **kargs)

        #self['color'] = color
        self['fillcolor'] = fillcolor
        self['shape'] = shape
        self['style'] = style

class CNOGraphAttributes(object):

    def __init__(self):

        self.attributes = {
               'activation': EdgeAttributes(color='black', arrowhead="normal"),
               'inhibition': EdgeAttributes(color='red', arrowhead="tee"),
               'stimuli': NodeAttributes(fillcolor='#9ACD32'),
               'inhibitors': NodeAttributes(fillcolor='orangered'),
               'signals': NodeAttributes(fillcolor='lightblue'),
               'nonc': NodeAttributes(fillcolor='yellow', style='diagonals'),
               'compressed': NodeAttributes(fillcolor="white",style='dashed', penwidth=2),
               'others': NodeAttributes(fillcolor="white",style='filled,bold',penwidth=2),
               'and': NodeAttributes(shape='circle',style='filled',width=.1,
                            height=.1, fixedsize=True, label='')
               }
    def keys(self):
        return self.attributes.keys()
    def __getitem__(self, key):
        return self.attributes[key]


class CNOGraph(nx.DiGraph):
    """Data structure (Digraph) used to manipulate networks 

    The networks can represent for instance a protein interaction network.

    CNOGraph is a graph data structure dedicated to the analysis of 
    phosphorylation data within protein-protein interaction networks 
    but can be used in a more general context. Indeed no data is 
    required. Note that CNOGraph inherits from the **directed graph**
    data structure of networkx. 

    However, we impose links between nodes to be restricted to two types:  
        * "+" for activation 
        * "-" for inhibition. 
        
    An instance can be created from an empty graph::

        c = CNOGraph()

    and edge can be added as follows::

        c.add_edge("A", "B", link="+")
        c.add_edge("A", "C", link="-")

    The methods :meth:`add_node`  and :meth:`add_edge` methods can be used to
    populate the graph. However, it is also possible to read a network 
    stored in a file in :class:`cellnopt.core.sif.SIF` format::

        >>> from cellnopt.core import *
        >>> pknmodel = cnodata("PKN-ToyPB.sif")
        >>> c = CNOGraph(pknmodel)

    The SIF model can be a filename, or an instance of 
    :class:`~cellnopt.core.sif.SIF`. Note for CellNOpt users 
    that if **and** nodes are contained in the original SIF files, they are
    kept (see the SIF documentation for details).

    You can add or remove nodes/edges in the CNOGraph afterwards.

    As mentionned above, you can also populate data within the CNOGraph data
    structure. The input data is an instance of
    :class:`~cellnopt.core.midas.MIDASReader`
    or a MIDAS filename. MIDAS file contains measurements made on proteins
    in various experimental conditions (stimuli and inhibitors). The names of
    the simuli, inhibitors and signals are used to color the nodes in the
    plotting function. However, the data itself is not used.

    If you don't use any MIDAS file as input, you can set the
    stimuli/inhibitors/signals manually by filling the hidden attributes
    _stimuli, _signals and _inhibitors.

    .. rubric:: Node and Edge attributes

    The node and edge attributes can be accessed as follows (and changed)::

        >>> c.node['egf']
        {'color': u'black',
         u'fillcolor': u'white',
         'penwidth': 2,
         u'shape': u'rectangle',
         u'style': u'filled,bold'}

        >>> c.edge['egf']['egfr']
        {u'arrowhead': u'normal',
         u'color': u'black',
         u'compressed': [],
         'link': u'+',
         u'penwidth': 1}

    .. rubric:: OPERATORS

    CNOGraph is a data structure with useful operators (e.g. union). Note,
    however, that these operators are applied on the topology only (MIDAS
    information is ignored). For instance, you can add graphs with the **+** operator
    or check that there are identical ::

        c = a+b
        a += b
        a == b

    Let us illustrate the + operation with another example. Let us consider the following graphs:

    .. plot::
        :include-source:
        :width: 30%

        from cellnopt.core import *
        c1 = CNOGraph()
        c1.add_edge("A","B", link="+")
        c1.add_edge("A","C", link="-")
        c1.plotdot()


    .. plot::
        :include-source:
        :width: 30%

        from cellnopt.core import *
        c2 = CNOGraph()
        c2.add_edge("A","E", link="+")
        c2.add_edge("C","E", link="+")
        c2.plotdot()

    ::

        (c1+c2).plotdot()


    .. plot::
        :width: 50%

        from cellnopt.core import *
        c1 = CNOGraph()
        c1.add_edge("A","B", link="+")
        c1.add_edge("A","C", link="-")
        c1.plotdot()
        c2 = CNOGraph()
        c2.add_edge("A","E", link="+")
        c2.add_edge("C","E", link="+")
        c2.plotdot()
        (c1+c2).plotdot()

    You can also substract a graph from another one::

        c3 = c1 - c2
        c3.nodes()

    The new graph should contains only one node (B). Additional functionalities
    such as :meth:`intersect`, :meth:`union` and :meth:`difference` can be used to see the difference
    between two graphs.

    .. rubric:: PLOTTING

    There are plotting functionalities to look at the graph, which are based on graphviz
    library. For instance, the :meth:`plotdot` is quite flexible but has a
    default behaviour following CellNOptR convention,  where stimuli are colored in green, 
    inhibitors in red and measurements in blue: 

    .. plot::
        :include-source:
        :width: 50%

        from cellnopt.core import *
        pknmodel = cnodata("PKN-ToyPB.sif")
        data = cnodata("MD-ToyPB.csv")
        c = CNOGraph(pknmodel, data)
        c.plotdot()

    If you did not use any MIDAS file as input parameter, you can still populate the hidden fields
    :attr:`_stimuli`, :attr:`_inhibitors`, :attr:`_signals`.

    You can also overwrite this behaviour by using the node_attribute parameter when 
    calling :meth:`plotdot`. For instance, if you call :meth:`centrality_degree`, which 
    computes and populate the node attribute
    **degree**. You can then call plotdot as follows to replace the default
    color:

    .. plot::
        :include-source:
        :width: 50%

        from cellnopt.core import *
        pknmodel = cnodata("PKN-ToyPB.sif")
        data = cnodata("MD-ToyPB.csv")
        c = CNOGraph(pknmodel, data)
        c.centrality_degree()
        c.plotdot(node_attribute="degree")

    Similarly, you can tune the color of the edge attribute. See the :meth:`plotdot` for more details.

    .. seealso::  tutorial, user guide

    """
    def __init__(self, model=None, data=None, verbose=False, **kargs):
        """.. rubric:: Constructor

        :param str model: optional network in SIF format. Can be the filename
            or instance of :class:`~cellnopt.core.sif.SIF`
        :param data: optional data file in MIDAS format. Can be a filename or
            instance of :class:`~cellnopt.core.midas.MIDASReader`
        :param bool verbose:
        :param str celltype: if a MIDAS file contains more that 1 celltype, you
            must provide a celltype name

        .. todo:: check that the celltype option works

        """
        super(CNOGraph, self).__init__(**kargs)
        self.kargs = kargs.copy()

        self.graph['graph'] = {"dpi":200}

        #: the attributes for nodes and edges are stored within this attribute. See :class:`CNOGraphAttributes`
        self.attributes = CNOGraphAttributes()
        self._midas = None
        self.verbose = verbose
        self.logging = Logging("INFO")

        #: stimuli
        self._stimuli = []
        self._compressed = []
        self._signals =[]
        #: inhibitors
        self._inhibitors = []
        self._nonc = []

        if hasattr(model, "nodes") and hasattr(model, "edges"):
            for node in model.nodes():
                self.add_node(str(node))
            for edge in model.edges(data=True):
                if "link" in edge[2]:
                    self.add_edge(str(edge[0]), str(edge[1]), link=edge[2]['link'])
                else:
                    self.add_edge(str(edge[0]), str(edge[1]), link="+")
            self.set_default_node_attributes() # must be call if sif or midas modified.
        else:
            self.readSIF(model)
        self.midas = data

        self._set_dot_attributes()

    def _set_dot_attributes(self):
        # other attributes

        self._dot_mode = "end_signals_bottom"

        self.dotattrs = {}
        self.dotattrs['graph'] = {"title": "CNOGraph output from cellnopt.core.cnograph.plotdot",
                    'fontname': 'helvetica',
                    'fontsize': 22,
                    'size': "25,25",
                    'ordering': "out",
                    'splines':True}

        self.dotattrs['edge'] = {
            'minlen':1,
            'color':'black'}

    # SOME PROPERTIES
    def _get_midas(self):
        return self._midas
    def _set_midas(self, data):
        if isinstance(data, str):
            self._midas = MIDASReader(data, celltype=self.kargs.get("celltype", None))
        elif isinstance(data, MIDASReader):
            self._midas = copy.deepcopy(data)
        elif data != None:
            self._midas = MIDASReader(data)
        elif data == None:
            self._midas = data 
        else:
            raise ValueError("Incorrect data, Must a valid MIDAS file or instance of MIDAS class")
        #if self._midas != None:
        #self._dataModelCompatibility()
        self.set_default_node_attributes()
    midas = property(fget=_get_midas, fset=_set_midas,
                     doc="MIDAS Read/Write attribute. An instance of :class:`MIDASReader`.")

    def _get_stimuli(self):
        stimuli = list(self._stimuli[:])
        if self.midas:
            stimuli += self.midas.cnolist.namesStimuli[:]
        return stimuli
    stimuli = property(_get_stimuli,
            doc="list of stimuli found in the :attr:`midas` and hidden attribute :meth:`_stimuli`")

    def _get_inhibitors(self):
        inhibitors = list(self._inhibitors)
        if self.midas:
            inhibitors += self.midas.cnolist.namesInhibitorsShort[:]
        return inhibitors
    inhibitors = property(_get_inhibitors, 
            doc="list of inhibitors found in the :attr:`midas` and hidden attribute :attr:`_inhibitors`")

    def _get_signals(self):
        signals = list(self._signals) # do not reference
        if self.midas:
            signals += self.midas.cnolist.namesSignals[:]
        return signals
    signals = property(_get_signals,
            doc="list of signals found in the :attr:`midas` and hidden attribute :meth:`_signals`")

    # METHODS
    def readSIF(self, model):
        """If the SIF file changes, we need to rebuild the graph."""
        # takes the SIF input file and build up the CNOGraph. remove all nodes
        # before
        self.clear()

        if isinstance(model, str):
            sif = SIF(model)
        elif isinstance(model, SIF):
            sif = model
        elif hasattr(model, "reacID"):
            sif = model
        elif model==None:
            sif = SIF()
        else:
            raise ValueError("The sif input must be a filename to a SIF file or an instance of the SIF class")

        # add all reactions
        for reac in sif.reacID:
            self.add_reaction(reac)

        # now, we need to set the attributes, only if we have a cnolist,
        # otherwise color is the default (white)
        self.set_default_node_attributes() # must be call if sif or midas modified.


    def _add_simple_reaction(self, reac):
        """A=B or !!A=B"""
        # not the second argument: we split only once so you can add a reaction
        # where the RHS is a AND gate coded with a "=" character in it (e.g., 
        # A=A+B=C which means reaction from A to AND gate called A+B=C)
        lhs, rhs = reac.split("=", 1)
        if lhs=="":
            self.add_node(rhs)
        elif rhs == "":
            self.add_node(lhs)
        else:
            if lhs.startswith("!"):
                link = "-"
                lhs = lhs[1:]
            else:
                link = "+"
            if self.has_edge(lhs, rhs):
                if self[lhs][rhs]['link'] == link:
                    self.logging.info("skip existing reactions %s %s %s" % (lhs, link, rhs))
                else:
                    self.add_edge(lhs,rhs, link=link)
            else:
                self.add_edge(lhs,rhs, link=link)

    def add_reaction(self, reac):
        """Add nodes and edges given a reaction

        :param str reac: a valid reaction. See below for examples

        Here are some valid reactions that includes NOT, AND and OR gates. + is an OR
        and ^ character is an AND gate::

            >>> s.add_reaction("A=B")
            >>> s.add_reaction("A+B=C")
            >>> s.add_reaction("A^C=E")
            >>> s.add_reaction("!F+G=H")

        .. plot::
            :width: 50%
            :include-source:

            from cellnopt.core import *
            c = CNOGraph()
            c.add_reaction("a+b^c+e+d^h=Z")
            c.plotdot()


        """
        # TODO: check if this is a valid reaction
        # ro rhs if there is an AND in LHS is wrong
        # mixing ^ and & and + is not implemented for now
        reac = reac.strip()
        reac = reac.replace("&", "^")
        lhs, rhs = reac.split("=")

        # if there is an OR gate, easy, just need to add simple reactions
        # A+!B=C is splitted into A=C and !B=C
        if "+" in lhs and "^" not in lhs:
            print(reac, "case 1")
            for this in lhs.split("+"):
                self._add_simple_reaction(this+"="+rhs)
            return

        # if no AND gates, even simpler it can only be reaction A=B or !A=B
        if "^" not in lhs and "+" not in lhs:
            #print(reac, "case 2")
            self._add_simple_reaction(lhs+"="+rhs)
            return

        if "^" and "+" in lhs:
            #print(reac, "case 3")
            # let us suppose that there is no mix such as a+b^c+d^h
            for this in lhs.split("+"):
                if "+" in this:
                    self._add_simple_reaction(this +"=" + rhs)
                else:
                    self.add_reaction(this +"=" + rhs)
            return
        
        # finally case with AND gates only
        if "^" in lhs and "+" not in rhs:
            #print(reac, "case 4")
            # and gates need a little bit more work
            self.add_edge(reac, rhs, link="+") # the AND gate and its the unique output
            # now the inputs
            species = lhs.split("^")
            for this in species:
                self._add_simple_reaction(this + "=" + reac)
            return

    def set_default_edge_attributes(self,  **attr):
        if "compressed" not in attr.keys():
            attr["compressed"] = []

        link = attr.get("link")
        if link == "-":
            attrs = self.attributes['inhibition']
        elif link == "+":
            attrs = self.attributes['activation']
        else:
            raise ValueError("link must be '+' or '-'. Found %s" % link)

        for k in attrs.keys():
            attr[k] = attrs[k]
        return attr

    def set_edge_attributes(self):
        """set all edge attributes to default attributes

        .. seealso:: :meth:`set_default_edge_attribute`
        """
        for edge in self.edges():
            attrs = self.edge[edge[0]][edge[1]]
            attrs = self.set_default_edge_attributes(**attrs)
            self.edge[edge[0]][edge[1]] = attrs

    def add_edge(self, u, v, attr_dict=None, **attr):
        """adds an edge between node u and v.

        :param str u: source node
        :param str v: target node
        :param str link: compulsary keyword. must be "+" or "-"
        :param dict attr_dict: dictionary, optional (default= no attributes)
             Dictionary of edge attributes.  Key/value pairs will update existing 
             data associated with the edge.
        :param attr: keyword arguments, optional
            edge data (or labels or objects) can be assigned using keyword arguments.
            keywords provided will overwrite keys provided in the **attr_dict** parameter

        .. warning:: color, penwidth, arrowhead keywords are populated according to the 
            value of the link.



        * If link="+", then edge is black and arrowhead is normal.
        * If link="-", then edge is red and arrowhead is a tee

        .. plot::
            :include-source:
            :width: 50%

            from cellnopt.core import *
            c = CNOGraph()
            c.add_edge("A","B",link="+")
            c.add_edge("A","C",link="-")
            c.add_edge("C","D",link="+", mycolor="blue")
            c.add_edge("C","E",link="+", data=[1,2,3])


        Attributes on the edges can be provided using the parameters **attr_dict** (a dictionary)
        and/or ****attr**, which is a list of key/value pairs. The latter will overwrite the 
        key/value pairs contained in the dictionary. Consider this example::
         
            c = CNOGraph()
            c.add_edge("a", "c", attr_dict={"k":1, "data":[0,1,2]}, link="+", k=3)
            c.edges(data=True)
            [('a',
            'c',
                {'arrowhead': 'normal',
                'color': 'black',
                'compressed': [],
                'k':3
                'link': '+',
                'penwidth': 1})]

        The field "k" in the dictionary (attr_dict) is set to 1. However, it is also 
        provided as an argument but with the value 3. The latter is the one used to populate 
        the edge attributes, which can be checked by printing the data of the edge (c.edges(data=True())


        .. seealso:: special attributes are automatically set by :meth:`set_default_edge_attributes`.
            the color of the edge is black if link is set to "+" and red otherwie.



        """
        u = u.replace("&", "+")
        #v = v.replace("^", "+")

        if "link" not in attr.keys():
            raise KeyError("link keyword must be provided")

        attr = self.set_default_edge_attributes(**attr)

        super(CNOGraph, self).add_edge(u, v, attr_dict, **attr)
        if "+" in u:
            lhs = u.split("+")
            for x in lhs:
                if x.startswith("-"):
                    attr["link"] = "+"
                    super(CNOGraph, self).add_edge(x[1:], u, attr_dict, **attr)
                else:
                    attr["link"] = "+"
                    super(CNOGraph, self).add_edge(x, u, attr_dict, **attr)


    def clear(self):
        """Remove nodes and edges"""
        super(CNOGraph, self).clear()


    def clean_orphan_ands(self):
        """Remove AND gates that are not AND gates anymore

        When removing an edge or a node, AND gates may not be valid anymore
        either because the output does not exists or there is a single input.

        This function is called when :meth:`remove_node` or :meth:`remove_edge` are called.
        However, if you manipulate the nodes/edges manually you may need to call
        this function afterwards.
        """
        for node in self._find_and_nodes():
            if len(self.successors(node))==0 or len(self.predecessors(node))<=1:
                self.remove_node(node)
                continue

    def _dataModelCompatibility(self):
        """When setting a MIDAS file, need to check that it is compatible with
        the graph, i.e. species are found in the model."""
        for x in self.midas.cnolist.namesCues:
            if x not in self.nodes():
                raise ValueError("""The cue %s was found in the MIDAS file but is
not present in the model. Change your model or MIDAS file. """ % x)
        for x in self.midas.cnolist.namesSignals:
            if x not in self.nodes():
                raise ValueError("""The signal %s was found in the MIDAS file but is
not present in the model. Change your model or MIDAS file. """ % x)

    def remove_and_gates(self):
        """Remove the AND nodes added by :meth:`expand_and_gates`"""
        for n in self._find_and_nodes():
            self.remove_node(n)

    def __eq__(self, other):
        # we must look at the data to figure out the link + or - but should ignore
        # all other keys

        try:
            edges1 = sorted(self.edges(data=True))
            edges2 = sorted(other.edges(data=True))
            edges1  = [(e[0], e[1], {'link':e[2]['link']}) for e in edges1]
            edges2  = [(e[0], e[1], {'link':e[2]['link']}) for e in edges2]
            res = edges1 == edges2
            return res
        except Exception:
            print("found exception")
            return False

    def __add__(self, other):
        """allows a+b operation
        
        combines the _inhibitors, _signals, _stimuli but keep only the first
        midas file.
        
        """
        print("calling __add__")
        G = self.copy()
        G.add_nodes_from(other.nodes(data=True))
        edges = other.edges(data=True)
        for e1,e2,d in edges:
            G.add_edge(e1,e2,None, **d)
            G._inhibitors += other._inhibitors
            G._signals += other._signals
            G._stimuli += other._stimuli
            # TODO: merge the MIDAS files. ?

        return G

    def __radd__(self, other):
        print("calling __radd__")
        self.add_nodes_from(other.nodes(data=True))
        edges = other.edges(data=True)
        for e1,e2,d in edges:
            self.add_edge(e1,e2,None, **d)

    #def __iadd__(self, other):
    #    print("calling iadd")
    #    self.add_nodes_from(other.nodes(data=True))
    #    edges = other.edges(data=True)
    #    for e1,e2,d in edges:
    #        self.add_edge(e1,e2,None, **d)
    #    return self

    def __sub__(self, other):
        print("calling __sub__")
        G = self.copy()
        G.remove_nodes_from([n for n in G if n in other.nodes()])
        return G

    #def __rsub__(self, other):
    #    self.remove_nodes_from([n for n in self if n in other.nodes()])

    def union(self, other):
        """Return graph with elements from this instance and the input graph.

        .. plot::
            :include-source:
            :width: 50%

            from cellnopt.core import *
            from pylab import subplot, title

            c1 = CNOGraph()
            c1.add_edge("A", "B", link="+")
            c1.add_edge("A", "C", link="-")
            c1.add_edge("C", "E", link="+")
            subplot(1,3,1)
            title(r"graph $C_1$")
            c1.plotdot(hold=True)

            c2 = CNOGraph()
            c2.add_edge("A", "B", link="+")
            c2.add_edge("B", "D", link="+")
            c2.add_edge("B", "F", link="+")
            subplot(1,3,2)
            c2.plotdot(hold=True)
            title(r"graph $C_2$")

            c3 = c1.union(c2)
            subplot(1,3,3)
            c3.plotdot(hold=True)
            title(r"graph $C_3 = C_1 \cup C_2$")

        """
        c = self + other
        return c

    def difference(self, other):
        """Return a CNOGraph instance that is the difference with the input graph

        (i.e. all elements that are in this set but not the others.)

        .. plot::
            :include-source:
            :width: 50%

            from cellnopt.core import *
            from pylab import subplot, title

            c1 = CNOGraph()
            c1.add_edge("A", "B", link="+")
            c1.add_edge("A", "C", link="-")
            c1.add_edge("C", "E", link="+")
            subplot(1,3,1)
            title("graph C1")
            c1.plotdot(hold=True)

            c2 = CNOGraph()
            c2.add_edge("A", "B", link="+")
            c2.add_edge("B", "D", link="+")
            c2.add_edge("B", "F", link="+")
            subplot(1,3,2)
            c2.plotdot(hold=True)
            title("graph C2")

            c3 = c1.difference(c2)
            subplot(1,3,3)
            c3.plotdot(hold=True)
            title("graph C3=C1-C2")


        .. note:: this method should be equivalent to the - operator. So c1-c2 == c1.difference(c2) 
        """
        G = self.copy()
        G.remove_nodes_from([n for n in G if n in other.nodes()])
        return G

    def intersect(self, other):
        """Return a graph with only nodes found in "other" graph.

        .. plot::
            :include-source:
            :width: 50%

            from cellnopt.core import *
            from pylab import subplot, title

            c1 = CNOGraph()
            c1.add_edge("A", "B", link="+")
            c1.add_edge("A", "C", link="-")
            c1.add_edge("C", "E", link="+")
            subplot(1,3,1)
            title(r"graph $C_1$")
            c1.plotdot(hold=True)

            c2 = CNOGraph()
            c2.add_edge("A", "B", link="+")
            c2.add_edge("B", "D", link="+")
            c2.add_edge("B", "F", link="+")
            subplot(1,3,2)
            c2.plotdot(hold=True)
            title(r"graph $C_2$")

            c3 = c1.intersect(c2)
            subplot(1,3,3)
            c3.plotdot(hold=True)
            title(r"graph $C_3 = C_1 \cap C_2$")

        """
        G = self.copy()
        G.remove_nodes_from([n for n in G if n not in other])
        return G

    def __str__(self):
        nodes = len([x for x in self.nodes() if '^' not in x])
        andnodes = len([x for x in self.nodes() if '^' in x])

        msg = "The model contains %s nodes (and %s AND node)\n" % (nodes, andnodes)

        self.logging.warning("Edge counting valid only if and node have only 2 inputs")
        edges = len([e for e in self.edges() if '^' not in e[0] and '^' not in e[1]])
        andedges = len([e for e in self.edges() if '^'  in e[0] or '^'  in e[1]])/3
        msg += "%s Hyperedges found (%s+%s) \n" % (edges+andedges, edges, andedges)

        return msg

    #def _get_link(self):
    #    return [self.edge[x[0]][x[1]]['link'] for x in self.edges_iter()]
    #links = property(fget=_get_link,  doc="Read only attribute.")
    #def _get_weight(self):
    #    return [self.edge[x[0]][x[1]]['weight'] for x in self.edges_iter()]
    #weights = property(fget=_get_weight,  doc="Read only attribute.")


    def draw(self, prog="dot", hold=False, attribute="fillcolor", colorbar=True,
         **kargs):
        """Draw the network using matplotlib. Not exactly what we want but could be useful.

        :param str prog: one of the graphviz program (default dot)
        :param bool hold: hold previous plot (default is False)
        :param str attribute: attribute to use to color the nodes (default is "fillcolor").
        :param node_size: default 1200
        :param width: default 2
        :param bool colorbar: add colorbar (default is True)

        Uses the fillcolor attribute of the nodes
        Uses the link attribute of the edges

        .. seealso:: :meth:`plotdot` that is dedicated to this kind of plot using graphviz
        """
        self.logging.warning("Not for production. Use plotdot() instead")
        pos = nx.drawing.graphviz_layout(self, prog=prog)

        if hold==False:
            from pylab import clf
            clf()
        node_size = kargs.get('node_size', 1200)
        kargs['node_size'] = node_size

        width = kargs.get('width', 2)
        kargs['width'] = width

        # node attributes
        nodes = sorted(self.nodes())
        node_colors = [self.node[x][attribute] if attribute in self.node[x].keys() else "gray" for x in nodes]

        # edge attributes
        edges = self.edges(data=True)
        colors = {'-':'red', '+':'black'}
        edge_colors = [colors[x[2]['link']] for x in edges]


        nx.draw(self, prog=prog, hold=hold, nodelist=nodes,
            edge_color=edge_colors, node_color=node_colors,
            pos=pos, **kargs)

        if attribute in ["dergee_cent", "betweeness_cent", "closeness_cent"]:
            if colorbar:
                from pylab import colorbar
                colorbar(shrink=0.7, pad=0.01, fraction=0.10)

    def _plot_legend(self):
        """used by plotdot""" 
        from pylab import gca, text
        a = gca()
        text(0.95, 0.95, "Color legend:\n--------------------\n green:stimuli\nred:inhibitors\nblue:readouts\nred arrow: inhibits\n: black arrow:direct link",
            transform=a.transAxes,
            verticalalignment='top', bbox=dict(facecolor="wheat", boxstyle="round",
            alpha=0.5))

    def _check_dot_prog(self, prog):
        import easydev
        easydev.checkParam(prog, ["twopi", "gvcolor", "wc", "ccomps", "tred",
            "sccmap", "fdp", "circo", "neato", "acyclic", "nop", "gvpr", "dot",
            "sfdp"])

    def plot(self, **kargs):
        self.plotdot(**kargs)

    def plotdot(self, prog="dot", viewer="pylab", hold=False, legend=False,
        show=True, filename=None, node_attribute=None, edge_attribute=None,
        cmap=None, show_colorbar=False, remove_dot=True, cluster_stimuli=True):
        """plotting graph using dot program (graphviz) and networkx

        By default, a temporary file is created to hold the image created by
        graphviz, which is them shown using pylab. You can choose not to see the
        image (show=False) and to save it in a local file instead (set the
        filename). The output format is PNG. You can play with
        networkx.write_dot to save the dot and create the SVG yourself.

        :param str prog: the graphviz layout algorithm (default is dot)
        :param viewer: pylab
        :param bool legend: adds a simple legend (default is False)
        :param bool show: show the plot (True by default)
        :param bool remove_dot: if True, remove the temporary dot file.

        Additional attributes on the graph itself can be set up by populating the
        graph attribute with a dictionary called "graph"::

            c.graph['graph'] = {"splines":True, "size":(20,20), "dpi":200}

        Useful other options are::

            c.edge["tnfa"]["tnfr"]["penwidth"] = 3
            c.edge["tnfa"]["tnfr"]["label"] = " 5"

        See the graphviz homepage documentation for more options.



        """
        # update the attributes
        if node_attribute == None:
            self.set_default_node_attributes()
        else:
            if len(self):
                node = self.nodes()[0]
            else:
                self.logging.info("Empty graph. Nothing to plot")
                return
            #if node_attribute not in self.node[node].keys():
            #    self.logging.info("attribute %s not found. We may need to call a specific method (e.g., centrality_closeness before")
            #    return

            import matplotlib
            cmap = matplotlib.cm.get_cmap(cmap)
            sm = matplotlib.cm.ScalarMappable(
                norm=matplotlib.colors.Normalize(vmin=0,vmax=1), cmap=cmap)
                    
            M = [node[1][node_attribute] for node in self.nodes(data=True) if node_attribute in node[1].keys()]
            if len(M):
                M = max(M)
            else:
                self.logging.error("attribute %s not found in any nodes" % node_attribute)

            for node in self.nodes():
                try:
                    value = self.node[node][node_attribute]/float(M)
                    rgb = sm.to_rgba(value)
                    colorHex = matplotlib.colors.rgb2hex(rgb)
                    self.node[node]['fillcolor'] = colorHex
                except:
                    self.node[node]['fillcolor'] = "#FFFFFF"

        if edge_attribute == None:
            self.set_edge_attributes()
        else:
            import matplotlib
            cmap = matplotlib.cm.get_cmap(cmap)
            sm = matplotlib.cm.ScalarMappable(
                norm=matplotlib.colors.Normalize(vmin=0,vmax=1), cmap=cmap)
            M = max([self.edge[edge[0]][edge[1]][edge_attribute] for edge in self.edges()])
            for edge in self.edges():
                value = self.edge[edge[0]][edge[1]][edge_attribute]/float(M)
                rgb = sm.to_rgba(value)
                colorHex = matplotlib.colors.rgb2hex(rgb)
                self.edge[edge[0]][edge[1]]['color'] = colorHex

        # ?
        self._check_dot_prog(prog)

        # create temp files
        infile  = tempfile.NamedTemporaryFile(suffix=".dot", delete=False)
        if filename == None:
            outfile  = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
            filename = outfile.name


        # Some nodes may belong to 2 colors. Creating subgraph is one way to go
        # around. Having graphviz 2.30 we could use striped node.
        if self.midas and node_attribute==None:
            for node in self.nodes():
                if node in self.midas.cnolist.namesSignals and node in self.midas.cnolist.namesInhibitorsShort:
                    self.node[node]['style'] = "diagonals,filled"
                    self.node[node]['color'] = "red"
                    self.node[node]['fillcolor'] = "lightblue"
                if node in self.midas.cnolist.namesStimuli and node in self.midas.cnolist.namesInhibitorsShort:
                    self.node[node]['style'] = "diagonals,filled"
                    self.node[node]['color'] = "red"
                    self.node[node]['fillcolor'] = "#9ACD32"

        H = nx.to_agraph(self)
        cluster = 1

        # we want stimuli to be on top
        if self.midas and cluster_stimuli:
            stimuli = self.midas.namesStimuli[:]
            H.add_subgraph(stimuli, name="cluster_stimuli", rank="source", style="filled", fillcolor="white")

        H.write(infile.name)

        #nx.write_doit(self, infile.name)
        if filename.endswith(".png"):
            cmd = "%s -Tpng %s -o %s" % (prog, infile.name, filename)
        elif filename.endswith(".svg"):
            cmd = "%s -Tsvg %s -o %s" % (prog, infile.name, filename)
        self.logging.info(cmd)
        ret = subprocess.call(cmd, shell=True)

        if viewer=="pylab" and show==True:
            from pylab import imshow, imread, axis, clf, gcf, colorbar
            if hold == False:
                clf()
                f = gcf()
                f.set_facecolor("white")
                a = f.add_axes([0.01,0.01,0.9,0.9])
                a.imshow(imread(filename))
                a.axis('off')
                #colorbar()
            else:
                a = imshow(imread(filename))
                axis('off')
                if show_colorbar:
                    colorbar()
                f = gcf()
                f.set_facecolor("white")
            if legend:
                self._plot_legend()
        elif show==True:
            ret = subprocess.call("%s %s &" % (viewer, filename), shell=True)
        else:
            a = None

        if remove_dot == True:
            infile.delete = True
            infile.close()
        else:
            import shutil
            if filename == None:
                shutil.move(infile.name, "test.dot")
            else:
                name = os.path.splitext(filename)[0] + ".dot"
                shutil.move(infile.name, name)
            infile.close()

        if filename == False:
            outfile.delete = True
            outfile.close()

        if node_attribute != None:
            self.set_default_node_attributes()
        if edge_attribute != None:
            self.set_edge_attributes()

        return a

    def plotdot2(self, viewer="pylab", prog="dot", legend=False):
        """plotting graph using dot program (graphviz) and own write_dot

        :param str prog: the graphviz layout algorithm (default is dot)
        :param viewer: pylab
        :param bool legend: adds a simple legend (default is False)

        .. warning:: not maintained but may be useful.

        """
        self._check_dot_prog(prog)
        trials = 0
        ret = 1
        while ret!=0 and trials<10:
            infile = self._write_dot()
            outfile  = tempfile.NamedTemporaryFile(suffix=".png", delete=False)            
            cmd = "%s -Tpng %s -o %s;" % (prog, infile.name, outfile.name)
            self.logging.info(cmd)
            ret = subprocess.call(cmd, shell=True)
            if ret!=0:
                self.logging.warning("failed to generate the image from the dot file. Trying again")
            trials+=1
        if ret != 0:
            raise IOError("could not create the image from the dot file...")

        if viewer=="pylab":
            from pylab import imshow, imread, axis, clf, gcf
            clf()
            f =gcf()
            f.set_facecolor("white")
            print(outfile.name)
            imshow(imread(outfile.name))
            axis('off')
            if legend:
                self._plot_legend()
        else:
            ret = subprocess.call("%s %s &" % (viewer, outfile.name), shell=True)
        infile.delete = False
        outfile.delete = True
        outfile.close()
        infile.close()

    def _write_dot(self, filename='test.dot'):
        H = nx.to_agraph(self)
        # some general stuff

        for k,v in self.dotattrs['graph'].iteritems():
            H.graph_attr[k] = v

        for k,v in self.dotattrs['edge'].iteritems():
            H.edge_attr[k] = v

        # order the graph for ranks
        allranks = self.get_same_rank()
        ranks  = {}
        for k,v in allranks.iteritems():
            ranks[k] = sorted([x for x in v if '=' not in x], cmp=lambda x,y:cmp(x.lower(), y.lower()))
            # add invisible edges so that the nodes that have the same rank are
            # ordered.
            for i, node1 in enumerate(ranks[k]):
                if i!=len(ranks[k])-1:
                    node2 = ranks[k][i+1]
                    H.add_edge(node1, node2, style="invis")


        M = max(ranks.keys())
        for rank in sorted(ranks.keys()):
            name = str(rank)
            if rank==0:
                name = "stimuli"
                print(ranks[rank])
                H.add_subgraph(ranks[rank], name="cluster_"+name, label="Stimuli" , rank='min')
            elif rank==M:
                name = "end_signals"
                H.add_subgraph(ranks[rank], name=name, rank='sink')
            else:
                H.add_subgraph(ranks[rank], name=name, rank='same')

        # save the file in a temporary directory
        infile  = tempfile.NamedTemporaryFile(suffix=".dot", delete=False)
        H.write(infile.name)
        H.clear()
        #self.agraph = H
        return infile

    def _get_nonc(self):
        nonc = self.findnonc()
        return nonc
    nonc = property(fget=_get_nonc,
        doc="Returns list of Non observable and non controlable nodes (Read-only).")

    def _get_reacID(self):
        edges =  [x for x in self.edges()]
        links = [str(self.edge[x[0]][x[1]]['link']) for x in edges]
        nodes1 = [x[0] for x in edges]
        nodes2 = [x[1] for x in edges]

        reacs = []
        for n1,link,n2 in zip(nodes1, links, nodes2):
            if "=" in n1 or "=" in n2:
                continue
            if link == "+":
                reacs.append(n1 + "=" + n2)
            else:
                reacs.append("!" + n1 + "=" + n2)
        return reacs
    reacID = property(_get_reacID, doc="return the reactions (edges)")

    def _get_namesSpecies(self):
        nodes = self.nodes()
        nodes = [x for x in nodes if "+" not in x and "=" not in x]
        return sorted(nodes)
    namesSpecies = property(fget=_get_namesSpecies,
        doc="Return sorted list of species (ignoring and gates) Read-only attribute.")


    def dependencyMatrix(self, fontsize=12):
        r"""Return dependency matrix

        * :math:`D_{i,j}` = green ; species i is an activator of species j (only positive path)
        * :math:`D_{i,j}` = red   ; species i is an inhibitor of species j (only negative path)
        * :math:`D_{i,j}` = yellow; ambivalent (positive and negative paths connecting i and j)
        * :math:`D_{i,j}` = red   ; species i has no influence on j


        .. plot::
            :include-source:
            :width: 80%

            from cellnopt.core import *
            c = CNOGraph(cnodata("PKN-ToyPB.sif"), cnodata("MD-ToyPB.csv"))
            c.dependencyMatrix()


        :status: in progress
        .. todo:: what to do if A-|B-|C ? is it a direct link or inhibitor ? 
        .. warning:: in progress. not yet finalised
        """
        import numpy
        nodes = sorted(self.nodes())
        N = len(nodes)
        data = numpy.zeros((len(nodes), len(nodes)))
        for i,node1 in enumerate(nodes):
            paths = nx.shortest_path(self, node1)
            for j,node2 in enumerate(nodes):
                if node1 == node2:
                    data[i][j] = 0
                elif node2 not in paths.keys():
                    data[i][j] = 0
                else:
                    path = paths[node2]
                    links = [self.edge[path[ii]][path[ii+1]]["link"] for ii in range(0,len(path)-1)]
                    if len(numpy.unique(links)) == 2:
                        data[i][j] = 1  # yellow
                    elif "+" in links:
                        data[i][j] = 2  #green
                    elif "-" in links:
                        data[i][j] = 3   #red
                    else:
                        print(node1, node2, path)
                        print(links)
                        raise ValueError("should not be here; a found link was different from + or -")

        nodeNames = [node.replace("_", "\_") for node in nodes]
        nodeNamesY = [node.replace("_", "\_") for node in nodes]
        from pylab import flipud, fliplr, pcolor, axis, yticks, xticks, arange,clf, colorbar
        from matplotlib import colors
        norm = colors.Normalize(vmin=0, vmax=3)

        cmap = colors.ListedColormap([[0., 0, 0], [1,1,0],[.5, 1, 0.], [1., 0, 0.]])
        clf();
        indices = [i for i, node in enumerate(nodes) if "and" not in node or "+" in nodes]
        pcolor(flipud(data[indices][:,indices]), edgecolors="w", cmap=cmap,norm=norm);
        #axis("off");

        N = len(indices)
        nodeNames = numpy.array(nodeNames)[indices]
        nodeNamesY = numpy.array(nodeNamesY)[indices[::-1]]
        axis([0,N,0,N])

        xticks([0.5+x for x in arange(N)], nodeNames, rotation=90, fontsize=fontsize)
        yticks([0.5+x for x in arange(N)], nodeNamesY, rotation=0, fontsize=fontsize)
        colorbar(ticks=[0.5,1.5,2.5,3.5]);

        return data

    def adjacencyMatrix(self, nodelist=None, weight=None):
        """Return adjacency matrix.

        :param list nodelist: The rows and columns are ordered according to the nodes in nodelist.
            If nodelist is None, then the ordering is produced by :meth:`nodes` method.

        :param str weight: (default=None) The edge data key used to provide each value in the matrix.
            If None, then each edge has weight 1. Otherwise, you can set it to
            "weight"

        :returns: numpy matrix Adjacency matrix representation of CNOGraph.

        .. note:: alias to :meth:`networkx.adjacency_matrix`

        .. seealso:: :meth:`adjacency_iter` and :meth:`adjacency_list`

        """
        from networkx import adjacency_matrix
        return adjacency_matrix(self, nodelist=nodelist).astype(int)

    def plotAdjacencyMatrix(self, fontsize=12, **kargs):
        """Plots adjacency matrix

        :param kargs : optional arguments accepted by pylab.pcolor

        .. plot::
            :width: 70%

            from cellnopt.core import *
            from pylab import *
            c = CNOGraph(cnodata("PKN-ToyMMB.sif"), cnodata("MD-ToyMMB.csv"))
            c.plotdot(hold=True)

        .. plot::
            :width: 70%
            :include-source:

            from cellnopt.core import *
            from pylab import *
            c = CNOGraph(cnodata("PKN-ToyMMB.sif"), cnodata("MD-ToyMMB.csv"))
            c.plotAdjacencyMatrix()

        """
        from pylab import pcolor, xticks, yticks, fliplr, array, arange, axis, flipud
        nodeNames = sorted(self.nodes())
        nodeNamesY = sorted(self.nodes())

        nodeNamesY.reverse()
        N = len(nodeNames)

        data = self.adjacencyMatrix(nodelist=nodeNames)

        pcolor(flipud(array(data)), edgecolors="k", **kargs)
        axis([0,N,0,N])
        xticks([0.5+x for x in arange(N)], nodeNames, rotation=90, fontsize=fontsize)
        yticks([0.5+x for x in arange(N)], nodeNamesY, rotation=0, fontsize=fontsize)


    def remove_edge(self, u, v):
        """Remove the edge between u and v.

        :param str u: node u
        :param str u: node v

        Calls :meth:`clean_orphan_ands` afterwards
        """
        super(CNOGraph, self).remove_edge(u,v)
        #if "+" not in n:
        self.clean_orphan_ands()

    def remove_node(self, n):
        """Remove a node n

        :param str node: the node to be removed

        Edges linked to **n** are also removed. **AND** gate may now be
        irrelevant (only one input or no input). Orphan AND gates are removed.

        .. seealso:: :meth:`clean_orphan_ands`

        """
        super(CNOGraph, self).remove_node(n)
        if "^" not in n:
            self.clean_orphan_ands()

    def add_node(self, node, attr_dict=None, **attr):
        """Add a node

        :param str node: a node to add
        :param dict attr_dict: dictionary, optional (default= no attributes)
             Dictionary of edge attributes.  Key/value pairs will update existing 
             data associated with the edge.
        :param attr: keyword arguments, optional
            edge data (or labels or objects) can be assigned using keyword arguments.
            keywords provided will overwrite keys provided in the **attr_dict** parameter

        .. warning:: color, fillcolor, shape, style are automatically set.


        ::

            c = CNOGraph()
            c.add_node("A", data=[1,2,3,]

        .. warning:: ****attr** replaces any key found in attr_dict. See :meth:`add_edge` for details.

        """
        if attr_dict:
            print("Warning: attr_dict overwritten")

        if "fillcolor" not in attr.keys():
            attr["fillcolor"] = "white"
        attr_dict = self.get_node_attributes(node)
        if "fillcolor" not in attr_dict.keys():
            attr_dict["fillcolor"] = "white"
            attr["fillcolor"] = "white"
        super(CNOGraph, self).add_node(node, attr_dict, **attr)

    def preprocessing(self, expansion=True, compression=True, cutnonc=True,
                      maxInputsPerGate=2):
        """Performs the 3 preprocessing steps (cutnonc, expansion, compression)

        :param bool expansion: calls :meth:`expand_and_gates` method
        :param bool compression: calls :meth:`compress` method
        :param bool cutnon: calls :meth:`cutnonc` method
        :param int maxInputPerGates: parameter for the expansion step

        .. plot::
            :width: 80%
            :include-source:

            from cellnopt.core import *
            c = CNOGraph(cnodata("PKN-ToyPB.sif"), cnodata("MD-ToyPB.csv"))
            c.preprocessing()
            c.plotdot()

        """
        if cutnonc:
            self.cutnonc()
        if compression:
            self.compress()
        if expansion:
            self.expand_and_gates(maxInputsPerGate=maxInputsPerGate)


    def cutnonc(self):
        """Finds non-observable and non-controllable nodes and removes them.

        .. plot::
            :include-source:
            :width: 50%

            from cellnopt.core import *
            c = CNOGraph(cnodata("PKN-ToyPB.sif"), cnodata("MD-ToyPB.csv"))
            c.cutnonc()
            c.plotdot()

        """
        nonc = self.nonc[:]
        for node in nonc:
            self.collapse_node(node)

    def compress(self):
        """Finds compressable nodes and removes them from the graph

        A compressable node is a node that is not part of the special nodes
        (stimuli/inhibitors/readouts mentionned in the MIDAS file). Nodes
        that have multiple inputs and multiple outputs are not compressable
        either.


        .. plot::
            :include-source:
            :width: 50%

            from cellnopt.core import *
            c = CNOGraph(cnodata("PKN-ToyPB.sif"), cnodata("MD-ToyPB.csv"))
            c.cutnonc()
            c.compress()
            c.plotdot()



        .. seealso:: :meth:`compressable_nodes`, :meth:`is_compressable`
        """
        
        #Patched to proceed on sorted lists and provide always the same results.
        #for node in self.compressable_nodes:
        for node in sorted(self.compressable_nodes):
            if self.is_compressable(node) == True:
                # update the graph G as well and interMat/notMat
                self.collapse_node(node)
                #self.midas.cnolist.namesCompressed.append(node)
        
        #Patched to proceed on a sorted list and provide always the same results.
        #for node in self.nodes():
        for node in sorted(self.nodes()):
            if self.degree(node) == 0 and node not in self.stimuli and \
                node not in self.signals and node not in self.inhibitors:
                """Luca: TODO? Shouldn't one check that an eventual orphan is not an observed node?
                Removing a node that is observed generates an incompatibility between the compressed network
                and the MIDAS file.

                The incompatibility arises when saving the compressed network and trying to use it with the same MIDAS
                file used to compress.

                In cellnopt.asp.netrec I have a workaround for this. It consists in finding the list of nodes that belong
                to the network but are in no edges (if a node A is removed during compression, it appears in no edges, 
                but you can still find it in CNOGraph.nodes()). For this set of nodes that do not belong to the network,
                I add fake edges like A + mock1 and so on.

                Doing like this I am able to save the compressed (or the repaired) network, while using the same MIDAS file.
                
                I was afraid to touch the code because I am not sure whether this is the intended behaviour."""

                
                
                self.logging.info("Found an orphan, which has been removed (%s)" % node)
                self.remove_node(node)

    def _decompress(self):
        """uncompress some nodes if possible.

        .. warning:: works for simple cases only so far


        """
        for n1, n2 in self.edges():
            compressedNodes = self.edge[n1][n2]['compressed']
            if compressedNodes==[]:
                continue
            for this in compressedNodes:
                link1 = this[0]
                link2 = this[-1]
                node = this[1:len(this)-1]
                #print(link1, node, link2)
                # must remove from compress list before add_node that calls
                # set_attributes (that check for compress list)
                # TODO check if this is correct to use try/except
                try:self.midas.cnolist.namesCompressed.remove(node)
                except: print("could not remove %s" % node)
                self.add_node(node)
                self.add_edge(n1,node, link=link1)
                self.add_edge(node,n2, link=link2)
            self.remove_edge(n1, n2)

    def collapse_nodes(self, nodes):
        """Collapse a list of nodes

        :param list nodes: a list of node to collapse

        .. seealso:: :meth:`collapse_node`.


        """
        for node in nodes:
            self.collapse_node(node)

    def _get_collapse_edge(self, inputAttrs, outputAttrs):
        attrs = inputAttrs.copy()
        if inputAttrs['link'] == outputAttrs['link']:
            attrs['link'] = "+"
            attrs['color'] = "black"
            attrs['arrowhead'] = "normal"
        else:
            attrs['link'] = "-"
            attrs['color'] = "red"
            attrs['arrowhead'] = "tee"

        return attrs

    def collapse_node(self, node):
        """Collapses a node (removes a node but connects input nodes to output nodes)

        This is different from :meth:`remove_node`, which removes a node and its edges thus
        creating non-connected graph. :meth:`collapse_node`, instead remove the node but merge the input/output
        edges IF possible. If there are multiple inputs AND multiple outputs the
        node is not removed.

        :param str node: a node to collapse.

        * Nodes are collapsed if there is at least one input or output.
        * Node are not removed if there is several inputs and several ouputs.
        * if the input edge is -, and the next is + or viceversa then the final edge if -
        * if the input edge is - and output is - then final edge is +

        .. warning:: to be used with cautious. For instance, if AND gates
            are present, there are kept.
        """
        # Removing a node that has several entries and several outputs is not
        # implemented because there is no such situation in CNO.
        successors = self.successors(node)
        predecessors = self.predecessors(node)

        newnodes1 = []
        newnodes2 = []
        newedges = []
        # todo: may be simplified ?
        if len(successors) == 1 and len(predecessors)==1:
            self.logging.debug("Compressing %s 1,1 mode" % node)
            # compressed node
            attr1 = self.edge[node][successors[0]]
            #
            attr2 = self.edge[predecessors[0]][node]

            compressed = attr2['link'] + node + attr1['link']
            attrs = self._get_collapse_edge(attr1, attr2)
            attrs['compressed'].append(compressed)
            if predecessors[0] != successors[0]:
                self.add_edge(predecessors[0], successors[0], None, **attrs)
            #newnodes1.append(predecessors[0])
            #newnodes2.append(successors[0])
            #newedges.append(attr['link'])
        elif len(successors) == 1:

            for predecessor in predecessors:
                attr = self.edge[predecessor][node]
                if predecessor != successors[0]:
                    attr2 = self.edge[node][successors[0]]
                    compressed = attr2['link'] + node + attr['link']
                    attrs = self._get_collapse_edge(attr, attr2)
                    attrs['compressed'].append(compressed)
                    self.add_edge(predecessor, successors[0], None, **attrs)
                #newnodes1.append(predecessor)
                #newnodes2.append(successors[0])
                #newedges.append(attr['link'])
        elif len(predecessors) == 1:
            #print(node)
            #print(predecessors)
            for successor in successors:
                #print(successor)
                attr = self.edge[node][successor]
                if predecessors[0] != successor:
                    attr2 = self.edge[predecessors[0]][node]
                    compressed = attr2['link'] + node + attr['link']
                    attrs = self._get_collapse_edge(attr, attr2)
                    attrs['compressed'].append(compressed)
                    self.add_edge(predecessors[0], successor, None,  **attrs)
                #newnodes1.append(predecessors[0])
                ##newnodes2.append(successor)
                #newedges.append(attr['link'])
        else:
            if len(successors) > 1 and len(predecessors) > 1:
                self.logging.debug(node, successors, predecessors)
                self.logging.warning("N succ >1 and N pred >1. Node not removed. use remove_node() if you really want to remove it")
                return
                #raise ValueError("invalid node to remove several in/out")
            else:
                self.logging.debug("%s %s %s" % (node, successors, predecessors))
                self.logging.warning("unknown case (no output or input ?). Node %s removed"% node)
                #raise ValueError("invalid node to remove several in/out")
        self.remove_node(node)

    def get_node_attributes(self, node):
        """Returns attributes of a node using the MIDAS attribute

        Given a node, this function identifies the type of the input
        node and returns a dictionary with the relevant attributes found
        in :attr:`node_attributes.attributes`.

        For instance, if a midas file exists and if **node** belongs to the stimuli,
        then the dicitonary returned contains the color green.

        :param str node:
        :returns: dictionary of attributes.

        """
        # default
        attr = self.attributes['others'].copy()
        # otherwisen
        if self.midas:
            if node in self.stimuli:
                attr = self.attributes['stimuli'].copy()
            elif node in self.signals:
                attr = self.attributes['signals'].copy()
            elif node in self.inhibitors:
                #midas.cnolist.namesInhibitorsShort or node in self._inhibitors:
                attr = self.attributes['inhibitors'].copy()
            elif node in self.midas.cnolist.namesNONC or node in self._nonc:
                attr = self.attributes['nonc'].copy()
            elif '^' in node:
                attr = self.attributes['and'].copy()
            elif node in self.midas.cnolist.namesCompressed or node in self._compressed:
                attr = self.attributes['compressed'].copy()
        else:
            if '^' in node:
                attr = self.attributes['and'].copy()

        if node in self._stimuli:
            attr = self.attributes['stimuli'].copy()
        if node in self._signals:
            attr = self.attributes['signals'].copy()
        if node in self._inhibitors:
            attr = self.attributes['inhibitors'].copy()
        return attr


    def set_default_node_attributes(self):
        """Set all node attributes to default attributes

        .. seealso:: :meth:`get_node_attributes`
        """
        for node in self.nodes():
            attrs = self.get_node_attributes(node)
            for k,v in attrs.iteritems():
                self.node[node][k] = v

    def get_same_rank(self):
        """Return ranks of the nodes.

        Used by plotdot/graphviz. Depends on attribute :attr:`dot_mode`

        """
        # some aliases
        try:
            stimuli = self.midas.cnolist.namesStimuli[:]
            if len(stimuli) == 0:
                stimuli = self._get_inputs()
        except:
            stimuli = self._get_inputs()

        try:
            signals = self.midas.cnolist.namesSignals[:]
            if len(signals) == 0:
                signals = self._get_outputs()
        except:
            signals = self._get_outputs()

        func_path = nx.algorithms.floyd_warshall(self)

        maxrank = int(self.get_max_rank())
        # start populating the ranks starting with the obvious one: stimuli and
        # signals
        ranks = {}
        ranks[0] = stimuli
        for i in range(1, maxrank+1):
            ranks[i] = []

        from pylab import inf, nanmin, nanmax
        if self.dot_mode == 'free':
            """default layout but stimuli on top"""
            for node in self.nodes():
                if node not in stimuli:
                    distances = [func_path[s][node] for s in stimuli]
                    distances = [abs(x) for x in distances if x != inf]
                    if len(distances) != 0:
                        M = nanmin([x for x in distances if x != inf])
                        try:
                            ranks[M].append(node)
                        except:
                            ranks[M] = [node]
                    else:
                        self.logging.debug('warning, rank %s is empyt'% node)

        elif self.dot_mode == 'signals_bottom':
            # no need for max rank here
            for node in self.nodes():
                if node not in stimuli and node not in signals:
                    distances = [func_path[s][node] for s in stimuli]
                    distances = [x for x in distances if x != inf]
                    if len(distances) != 0:
                        M = nanmax([abs(x) for x in distances if x != inf])
                        try:
                            ranks[M].append(node)
                        except:
                            ranks[M] = [node]
                    else:
                        self.logging.debug('warning, rank %s is empyt'% node)
            M = max(ranks.keys())
            ranks[M+2] = signals

        elif self.dot_mode == 'end_signals_bottom':
            maxrank = max(ranks.keys())
            for node in sorted(self.nodes(),cmp=lambda x,y: cmp(x.lower(), y.lower())):
                # end signals
                #print(node,)
                if node in signals and len(self.successors(node))==0:
                    continue
                elif node not in stimuli:
                    distances = [func_path[s][node] for s in stimuli]
                    distances = [x for x in distances if x != inf]
                    #print(distances)
                    if len(distances) != 0:
                        M = nanmax([abs(x) for x in distances if x != inf])
                        try:
                            ranks[M].append(node)
                        except:
                            ranks[M] = [node]

                    else:
                        self.logging.debug('warning, rank %s is empyt'% node)
            for node in sorted(self.nodes(), cmp=lambda x,y: cmp(x.lower(),y.lower())):

                if node in signals and len(self.successors(node))==0:
                    try:
                        ranks[maxrank].append(node)
                    except:
                        print("isssu")
                        ranks[maxrank] = [node]
        return ranks

    def _get_inputs(self):
        self.logging.warning('no stimuli found, trying to build one. consider using a cnolist')
        return [x for x in self.nodes() if len(self.predecessors(x))==0]

    def _get_outputs(self):
        self.logging.warning('WARNING. no signals found, tryring to build one. consider using a cnolist')
        return  [x for x in self.nodes() if len(self.successors(x))==0]

    def get_max_rank(self):
        """Get the maximum rank from the inputs using floyd warshall algorithm

        If a MIDAS file is provided, the inputs correspond to the stimuli.
        Otherwise, (or if there is no stimuli in the MIDAS file),
        use the nodes that have no predecessors as inputs (ie, rank=0).

        """
        from pylab import nanmax, inf
        if self.midas:
            stimuli = self.midas.cnolist.namesStimuli[:]
            if len(stimuli) == 0:
                stimuli = self._get_inputs()
        else:
            stimuli = self._get_inputs()

        func_path = nx.algorithms.floyd_warshall(self)
        # compute the longest path from Stimuli by using the floyd warshall
        # algorithm. inputs/stimuli has rank 0.
        ranks = [[x for x in func_path[stimulus].values() if x !=inf]
            for stimulus in stimuli]

        allranks = []
        for r in ranks:
            allranks = allranks + r #concatenate all ranks includeing empty []
        maxrank = nanmax(allranks)
        return maxrank

    def _get_dot_mode(self):
        return self._dot_mode
    def _set_dot_mode(self, value):
        valid = ['free', 'signals_bottom', 'end_signals_bottom']
        assert value in valid, "unknown value. must be in %s" % valid
        self._dot_mode = value
    dot_mode = property(fget=_get_dot_mode, fset=_set_dot_mode,
        doc="Read/Write attribute to use with plotdot2 method (experimental).")

    def _add_and_gates(self, node, maxInputsPerGate=2):
        """See expand_and_gates docstring"""
        preds = self.predecessors(node)
        preds = [pred for pred in preds if "^" not in pred]
        assert maxInputsPerGate>=2 and maxInputsPerGate<=5, "maxInputsPerGate must be >2 and less than 5"
        #todo: order predecessirs according to nameSpecies order
        self.logging.debug( "node %s, pred=%s " % (node,  preds))

        if len(preds) == 1:
            self.logging.debug("Nothing to do with %s (only 1 predecessor)" % node)
            return

        for inputsPerGates in range(2, maxInputsPerGate+1):
            self.logging.debug(inputsPerGates)
            if inputsPerGates>len(preds):
                continue
            for combi in itertools.combinations(preds, inputsPerGates):
                self.logging.debug("adding %s input gate from %s to %s" % (inputsPerGates, combi, node))
                shape = "circle"
                if len(combi) == 3:
                    shape = "triangle"
                elif len(combi) >= 4:
                    shape = "square"
                andNode = self._nodes2reac(list(combi), node)
                self.logging.debug("add_and_gates: %s " % andNode)
                self.add_node(andNode, shape=shape)
                for combinode in combi:
                    attr = self.edge[combinode][node].copy()
                    attr['link'] = self.edge[combinode][node]['link']
                    #attr['weight'] = pylab.nan # edge from and to specy always + and nan weight
                    self.add_edge(combinode, andNode, None, **attr)
                attr['link'] = "+" # edge from and to specy always +
                #attr['weight'] = pylab.nan # edge from and to specy always + and nan weight
                attr['color'] = 'black' # and output is always black
                self.add_edge(andNode, node, None, **attr)

    def _nodes2reac(self, inputsNodes, output):
        inputs = []
        for node in inputsNodes:
            if self.edge[node][output]['link']=="-":
                inputs.append("!"+node)
            else:
                inputs.append(node)

        reac = "^".join(inputs)
        reac += "=" + output
        return reac

    def _find_nodes_with_multiple_inputs(self):
        """return a list of nodes that have multiple predecessors"""
        nodes = []
        for node in self.nodes():
            if len(self.predecessors(node))>1 and "^" not in node:
                nodes.append(node)
            else:
                if len(self.predecessors(node))>1 and "^" in node:
                    self.logging.debug("ignore ", node)
        return nodes

    def _find_and_nodes(self):
        andNodes = [x for x in self.nodes() if "^" in x]
        return andNodes

    def expand_or_gates(self):
        """Expand OR gates given AND gates

        If a graph contains AND gates (without its OR gates), you can add back
        the OR gates automatically using this function.

        .. plot::
            :include-source:
            :width: 50%

            from cellnopt.core import *
            from pylab import subplot, title

            c1 = CNOGraph()
            c1.add_edge("A", "C", link="-")
            c1.add_edge("B", "C", link="+")
            c1.expand_and_gates()
            subplot(1,3,1)
            title("OR and AND gates")
            c1.plotdot(hold=True)

            c1.remove_edge("A", "C")
            c1.remove_edge("B", "C")
            subplot(1,3,2)
            c1.plotdot(hold=True)
            title("AND gates only")

            c1.expand_or_gates()
            subplot(1,3,3)
            c1.plotdot(hold=True)
            title("after call to \\n expand_or_gates function")

        .. seealso:: :meth:`~cellnopt.core.cnograph.CNOGraph.expand_and_gates`

        """


        for this in self._find_and_nodes():
            p = self.predecessors(this)
            s = self.successors(this)
            assert len(s) == 1
            for node in p:
                link = self.edge[node][this]['link']
                self.add_edge(node, s[0], link=link)


    def expand_and_gates(self, maxInputsPerGate=2):
        """Expands the network to incorporate AND gates

        :param int maxInputsPerGate: restrict maximum number of inputs used to
            create AND gates (default is 2)

        The CNOGraph instance can be used to model a boolean network.  If a node
        has several inputs,  then the combinaison of the inputs behaves like an OR gate
        that is we can take the minimum over the inputs.

        In order to include AND behaviour, we introduce a special node called
        AND gate. This function adds AND gates whenever a node has several
        inputs. The AND gates can later on be used in a boolean formalism.

        In order to recognise AND gates, we name them according to the following
        rule. If a node A has two inputs B and C, then the AND gate is named::

            B+C=A

        and 3 edges are added: B to the AND gates, C to the AND gates and the AND gate to A.

        If an edge is a "-" link then, an **!** character is introduced. 

        In this expansion process, AND gates themselves are ignored.

        If there are more than 2 inputs, all combinaison of inputs may be
        considered but the default parameter **maxInputsPerGate** is set to 2. 
        For instance, with 3 inputs A,B,C you may have the
        following combinaison: A+B, A+C, B+C. The link A+B+C will be added only
        if **maxInputsPerGate** is set to 3.
 

        .. plot::
            :include-source:
            :width: 50%

            from cellnopt.core import *
            from pylab import subplot, title

            c = CNOGraph()
            c.add_edge("A", "C", link="+")
            c.add_edge("B", "C", link="+")
            subplot(1,2,1)
            title("Original network")
            c.plotdot(hold=True)

            c.expand_and_gates()
            subplot(1,2,2)
            c.plotdot(hold=True)
            title("Expanded network")

        .. seealso:: :meth:`remove_and_gates`, :meth:`clean_orphan_ands`, 
            :meth:`expand_or_gates`.
            :meth:`_add_and_gates`.

        .. note:: this method adds all AND gates in one go. If you want to add a specific AND gate,
            you have to do it manually. You can use the :meth:`add_reaction` for that purpose.

        .. todo:: attributes on the edges could be copied into the edge attributes ?

        """
        nodes2expand = self._find_nodes_with_multiple_inputs()
        for node in nodes2expand:
            self._add_and_gates(node, maxInputsPerGate)
    
    #def subgraph(self, nodes):
    #    """networkx method not to be used"""
    #    raise NotImplementedError("must implement this method by removing columns i n MIDAS file")

    def add_cycle(self, nodes, **attr):
        """Add a cycle

        :param list nodes: a list of nodes. A cycle will be constructed from
           the nodes (in order) and added to the graph.
        :param dict attr: must provide the "link" keyword. Valid values are "+", "-"
            the links of every edge in the cycle will be identical.

        .. plot::
            :include-source:
            :width: 50%

            from cellnopt.core import *
            c = CNOGraph()
            c.add_edge("A", "C", link="+")
            c.add_edge("B", "C", link="+")
            c.add_cycle(["B", "C", "D"], link="-")
            c.plotdot()

        .. warning:: added cycle overwrite previous edges

        """

        if "link" not in attr.keys():
            raise KeyError("link keyword must be provided")

        attr = self.set_default_edge_attributes(**attr)

        super(CNOGraph, self).add_cycle(nodes, **attr)

    def add_path(self):
        """networkx method not to be used"""
        raise NotImplementedError

    def to_directed(self):
        """networkx method not to be used"""
        raise NotImplementedError

    def add_star(self):
        """networkx method not to be used"""
        raise NotImplementedError

    def remove_edges_from(self):
        """networkx method not to be used"""
        raise NotImplementedError

    def add_weighted_edges_from(self):
        """networkx method not to be used"""
        raise NotImplementedError

    def add_edges_from(self, ebunch, attr_dict=None, **attr):
        """add list of edges with same parameters

        ::

            c.add_edges_from([(0,1),(1,2)], data=[1,2]) 

        .. seealso:: :meth:`add_edge` for details.

        """
        super(CNOGraph, self).add_edges_from(ebunch, attr_dict=None, **attr)
        #for e in ebunch:
        #    self.add_edge(e[0], e[1], attr_dict=attr_dict, **attr)

    def add_nodes_from(self, nbunch, attr_dict=None, **attr):
        """Add a bunch of nodes

        :param list nbunch: list of nodes. Each node being a string.
        :param dict attr_dict: dictionary, optional (default= no attributes)
             Dictionary of edge attributes.  Key/value pairs will update existing 
             data associated with the edge.
        :param attr: keyword arguments, optional
            edge data (or labels or objects) can be assigned using keyword arguments.
            keywords provided will overwrite keys provided in the **attr_dict** parameter

        .. warning:: color, fillcolor, shape, style are automatically set.

        .. seealso:: :meth:`add_node` for details.


        """
        super(CNOGraph, self).add_nodes_from(nbunch, attr_dict=None, **attr)

        #for n in nbunch:
        #    self.add_node(n, attr_dict=attr_dict, **attr) 

    def remove_nodes_from(self, nbunch):
        """Removes a bunch of nodes

        .. warning:: need to be tests with and gates."""
        super(CNOGraph, self).remove_nodes_from(nbunch)

    def _get_compressable_nodes(self):
        return [x for x in self.nodes() if self.is_compressable(x)]
    compressable_nodes = property(fget=_get_compressable_nodes,
        doc="Returns list of compressable nodes (Read-only).")

    def _ambiguous_multiedge(self, node):
        """Test whether the removal of a node may lead to multi edges ambiguity

        e.g., A-->B and A--| B
        """
        edges = [(x[0], x[1], x[2]['link']) for x in self.edges(data=True)]
        for A in self.predecessors(node):
            for B in self.successors(node):
                link = self.edge[node][B]['link']
                if link == "+": link = "-"
                elif link == "-": link = "+"
                if (A, B, link) in edges:
                    return True
        return False

    def is_compressable(self, node):
        """Returns True if the node can be compressed, False otherwise

        :param str node: a valid node name
        :return: boolean value

        Here are the rules for compression. The main idea is that a node can be removed if the 
        boolean logic is preserved (i.e. truth table on remaining nodes is preserved).

        A node is compressable if it is not part of the stimuli, inhibitors, or
        signals specified in the MIDAS file. 
        
        If a node has several outputs and inputs, it cannot be compressed.
        
        If a node has one input or one output, it may be compressed.
        However, we must check the following possible ambiguity that could be raised by the removal
        of the node: once removed, the output of the node may have multiple input edges with different
        types of inputs edges that has a truth table different from the original truth table.
        In such case, the node cannot be compressed.

        Finally, a node cannot be compressed if one input is also an output (e.g., cycle).


        .. plot::
            :include-source:
            :width: 50%

            from cellnopt.core import *
            from pylab import subplot,show, title
            c = cnograph.CNOGraph()
            c.add_edge("a", "c", link="-")
            c.add_edge("b", "c", link="+")
            c.add_edge("c", "d", link="+")
            c.add_edge("b", "d", link="-")
            c.add_edge("d", "e", link="-")
            c.add_edge("e", "g", link="+")
            c.add_edge("g", "h", link="+")
            c.add_edge("h", "g", link="+")

            # multiple inputs/outputs are not removed
            c.add_edge("s1", "n1", link="+")
            c.add_edge("s2", "n1", link="+")
            c.add_edge("n1", "o1", link="+")
            c.add_edge("n1", "o2", link="+")

            c._stimuli = ["a", "b", "s1", "s2"]
            c._signals = ["d", "g", "o1", "o2"]

            subplot(1,2,1)
            c.plotdot(hold=True)
            title("Initial graph")

            c.compress()
            subplot(1,2,2)
            c.plotdot(hold=True)
            title("compressed graph")

            show()
            
        
        
        """
        if node not in self.nodes():
            msg = "node %s is not in the graph" % node
            raise ValueError(msg)

        # there is always a MIDAS file for now but we may remove it later on
        specialNodes = self.inhibitors + self.signals  + self.stimuli
        notcompressable = [x for x in self.nodes() if x in specialNodes]
        if node in notcompressable:
            return False

        succs = self.successors(node)
        preds = self.predecessors(node)

        # if one input is an input, no compression
        if len(set(succs).intersection(set(preds))) > 0:
            self.logging.debug('skipped node (retroaction ? %s) ' % node)
            print("%s case cycle input is in output" % node)
            return False

        # if no output or no input, can be compressed. 
        # somehow this is redundant with NONC algorithm, which is not required
        # anymore.
        if len(self.successors(node)) == 0 or len(self.predecessors(node))==0:
            self.logging.debug('skipped node %s (input/output case ' % node)
            return True

        # if multiple input AND multiple output, no ambiguity: nothing to compress
        elif len(self.successors(node)) >1 and len(self.predecessors(node))>1:
            self.logging.debug('skipped node %s >1,>1 case ' % node)
            return False

        # if one input and several outputs OR several input and one ouptut, we
        # can compress. However, if the compressable node once removed is an
        # edge that already exists, then we will have multiedges, which is not
        # handled in a DIgraph. So, we cannot comrpess that particular case.


        # if one input only and one output only, no ambiguity: we can compress
        elif len(self.predecessors(node)) == 1 and len(self.successors(node))==1:
            ambiguous = self._ambiguous_multiedge(node)
            if ambiguous == True:
                self.logging.debug('%s could be compressed but ambiguity with existing edge so not removed ' % node)
                return False
            else:
                self.logging.debug('Add node %s =1,=1 to be removed ' % node)
                return True

        # one output but several input may be ambiguous. If output is inhibitor
        # and input contains an mix of inhibitor/activation then we can not
        # compress
        elif len(preds) > 1 and len(succs)==1:
            input_links = [self[p][node]['link'] for p in preds]
            output_links = self[node][succs[0]]['link']
            if (output_links == "-") and len(set(input_links))>=2:
                self.logging.debug('skipped node %s output=inhibitor and ambiguous inputs' % node)
                return False
            else:
                ambiguous = self._ambiguous_multiedge(node)
                if ambiguous == True:
                    self.logging.debug('%s could be compressed but ambiguity with existing edge so not removed ' % node)
                    return False
                else:
                    self.logging.debug('Add node %s >1,=1 case to be removed' % node)
                    return True

        # one input and several ouptut, no ambiguity: we can compress
        elif len(preds) == 1 and len(succs)>1:
            ambiguous = self._ambiguous_multiedge(node)
            if ambiguous == True:
                self.logging.debug('%s could be compressed but ambiguity with existing edge so not removed ' % node)
                return False
            else:
                self.logging.debug('Add node %s =1,>1 case to be removed' % node)
                return True
        else:
            self.logging.debug('do not remove node %s' % node)
            return False

    def rename_node(self,oldname,newname):
        """Function to rename a node, while keeping all its attributes."""
        raise NotImplementedError
        from copy import deepcopy
        # first fix the node:
        self.node[newname] = deepcopy(self.node[oldname])
        del self.node[oldname]

        self.add_node(newname) #add the node. The attributes should be set.
        # now fix the edges
        from_old = [x[1] for x in self.edges() if x[0]==oldname] #get the list of nodes targeted by oldname
        to_old = [x[0] for x in self.edges() if x[1]==oldname] #get the list of nodes that target oldname

        self.edge[newname] = deepcopy(self.edge[oldname])
        del self.edge[oldname]

#         for n in from_old:
#             self.edge[newname][n] = self.edge[oldname][n]
#             del self.edge[oldname][n]

        for n in to_old:
             self.edge[n][newname] = deepcopy(self.edge[n][oldname])
             del self.edge[n][oldname]


    def centrality_degree(self):
        """Compute the degree centrality for nodes.

        The degree centrality for a node v is the fraction of nodes it
        is connected to.

        :return: list of nodes with their degree centrality. It is also added to the list
            of attributes with the name "degree_centr"

        .. plot::
            :include-source:
            :width: 50%

            from cellnopt.core import *
            c = CNOGraph(cnodata("PKN-ToyPB.sif"), cnodata("MD-ToyPB.csv"))
            c.centrality_degree()
            c.plotdot(node_attribute="centrality_degree")


        """
        res = nx.degree_centrality(self)
        nx.set_node_attributes(self, 'degree', res)
        nx.set_node_attributes(self, 'centrality_degree', res)
        import operator
        degcent_sorted = sorted(res.items(), key=operator.itemgetter(1), reverse=True)
        #for k,v in degcent_sorted:
        #    self.logging.info("Highest degree centrality %s %s", v,k)
        return res

    def degree_histogram(self, show=True, normed=False):
        """Compute histogram of the node degree (and plots the histogram)

        .. plot::
            :include-source:
            :width: 50%

            from cellnopt.core import *
            c = CNOGraph(cnodata("PKN-ToyPB.sif"), cnodata("MD-ToyPB.csv"))
            c.degree_histogram()


        """
        degree = self.degree().values()
        Mdegree = max(degree)

        from pylab import bar, xlim, ylim, axis, grid, title, clf, hist
        if show == True:
            clf()
            res = hist(degree, bins=range(0,Mdegree+1), align='left', rwidth=0.8, normed=normed)
            xlims = xlim()
            ylims = ylim()
            axis([0, xlims[1], ylims[0], ylims[1]*1.1])
            grid()
            title("Degree distribution")
        return res

    def centrality_closeness(self, **kargs):
        """Compute closeness centrality for nodes.

        Closeness centrality at a node is 1/average distance to all other nodes.

        :param v: node, optional  Return only the value for node v
        :param str distance: string key, optional (default=None)  Use specified edge key as edge distance.   If True, use 'weight' as the edge key.
        :param bool normalized:  optional   If True (default) normalize by the graph size.

        :return: Dictionary of nodes with closeness centrality as the value.

        .. plot::
            :include-source:
            :width: 50%

            from cellnopt.core import *
            c = CNOGraph(cnodata("PKN-ToyPB.sif"), cnodata("MD-ToyPB.csv"))
            c.centrality_closeness()
            c.plotdot(node_attribute="centrality_closeness")

        """
        res = nx.centrality.closeness_centrality(self, **kargs)

        nx.set_node_attributes(self, 'closeness', res)
        nx.set_node_attributes(self, 'centrality_closeness', res)
        import operator
        degcent_sorted = sorted(res.items(), key=operator.itemgetter(1), reverse=True)
        #for k,v in degcent_sorted:
        #    self.logging.info("Highest closeness centrality %s %s", v,k)
        return res


    def centrality_betweeness(self, k=None, normalized=True,
        weight=None, endpoints=False, seed=None):
        r"""Compute the shortest-path betweeness centrality for nodes.

        Betweenness centrality of a node `v` is the sum of the
        fraction of all-pairs shortest paths that pass through `v`:

        .. math::

            c_B(v) =\sum_{s,t \in V} \frac{\sigma(s, t|v)}{\sigma(s, t)}

        where :math:`V` is the set of nodes, :math:`\sigma(s, t)` is the number of
        shortest :math:`(s, t)`-paths,  and :math:`\sigma(s, t|v)` is the number of those
        paths  passing through some  node :math:`v` other than :math:`s, t`.
        If :math:`s = t`, :math:`\sigma(s, t) = 1`, and if :math:`v \in {s, t}`,
        :math:`\sigma(s, t|v) = 0` .

        :param int k: (default=None)
          If k is not None use k node samples to estimate betweeness.
          The value of k <= n where n is the number of nodes in the graph.
          Higher values give better approximation.
        :param bool normalized:   If True the betweeness values are normalized by :math:`2/((n-1)(n-2))`
          for graphs, and :math:`1/((n-1)(n-2))` for directed graphs where :math:`n`
          is the number of nodes in G.
        :param str weight: None or string, optional
          If None, all edge weights are considered equal.

        .. plot::
            :include-source:
            :width: 50%

            from cellnopt.core import *
            c = CNOGraph(cnodata("PKN-ToyPB.sif"), cnodata("MD-ToyPB.csv"))
            c.centrality_betweeness()
            c.plotdot(node_attribute="centrality_betweeness")

        .. seealso:: networkx.centrality.centrality_betweeness

        """
        res = nx.centrality.betweenness_centrality(self,k=k,normalized=normalized,
            weight=weight, endpoints=endpoints, seed=seed)
        nx.set_node_attributes(self, 'centrality_betweeness', res)
        nx.set_node_attributes(self, 'betweeness', res)
        import operator
        degcent_sorted = sorted(res.items(), key=operator.itemgetter(1), reverse=True)
        #for k,v in degcent_sorted:
        #    self.logging.info("Highest betweeness centrality %s %s", v,k)
        return res

    def export2gexf(self, filename):
        """Export into GEXF format

        :param str filename:

        This is the networkx implementation and requires the version 1.7
        This format is quite rich and can be used in external software such as Gephi.

        .. warning:: color and labels are lost. information is stored as
            attributes.and should be as properties somehow. 
            Examples:  c.node['mkk7']['viz'] =  {'color': {'a': 0.6, 'r': 239, 'b': 66,'g': 173}}

        """
        from networkx.readwrite import write_gexf
        write_gexf(self, filename)

    def export2sif(self, filename):
        """Export CNOGraph into a SIF file.

        Takes into account and gates. If a species called  "A^B=C" is found, it is an AND
        gate that is encoded in a CSV file as::

            A 1 and1
            B 1 and1
            and1 1 C

        :param str filename:

        .. todo:: could use SIF class instead to simplify the code
        """
        andCounter = 0
        fh = open(filename, "w")
        for edge in self.edges(data=True):
            n1 = edge[0]
            n2 = edge[1]
            if "^" not in n1 and "^" not in n2:
                link = edge[2]['link']
                if link == "+":
                    fh.write("%s 1 %s\n" % (n1,n2))
                else:
                    fh.write("%s -1 %s\n" % (n1,n2))

        for node in self._find_and_nodes():
            andCounter += 1
            andNode = "and%s" % andCounter 
            succs = self.successors(node)
            preds = self.predecessors(node)
            for succ in succs:
                link = self.edge[node][succ]['link']
                if link == "+":
                    fh.write("%s 1 %s\n" % (andNode,succ))
                else:
                    fh.write("%s -1 %s\n" % (andNode,succ))
            for pred in preds:
                link = self.edge[pred][node]['link']
                if link == "+":
                    fh.write("%s 1 %s\n" % (pred,andNode))
                else:
                    fh.write("%s -1 %s\n" % (pred,andNode))
        fh.close()


    def export2json(self, filename):
        """Export the graph into a JSON format

        :param str filename:

        .. seealso:: :meth:`loadjson`
        """
        from networkx.readwrite import json_graph
        data = json_graph.node_link_data(self)
        import json
        json.dump(data, open(filename, "w"))


    def export2SBMLQual(self, filename, modelName="CellNOpt_model"):
        """Export the topology into SBMLqual and save in a file

        This requires only the topology information (i.e. MIDAS content is ignored).

        .. seealso:: :meth:`cellnopt.core.sif.SIF.export2SBMLQual`
        """
        s = SIF()
        for reac in self.reacID:
            s.add_reaction(reac)
        res = s.export2SBMLQual(filename=filename, modelName=modelName)

    def loadjson(self, filename):
        """Load a network in JSON format as exported from :meth:`export2json`

        :param str filename:

        .. seealso:: :meth:`export2json`
        """
        from networkx.readwrite import json_graph
        graph = json_graph.load(open(filename))

        self.clear()
        for node in graph.nodes():
            self.add_node(node)
        for edge in graph.edges(data=True):
            self.add_edge(edge[0], edge[1], link=edge[2]['link'])

        return graph


    def lookfor(self, specyName):
        """Prints information about a species

        If not found, try to find species by ignoring cases.

        """
        #try to find the specy first:
        if specyName not in self.nodes():
            print("did not find the requested specy")
            proposals = [node for node in self.nodes() if specyName.lower() in node.lower()]
            if len(proposals):
                print("try one of ")
                for p in proposals:
                    print(proposals)
        else:
            print("predecessors")
            print(self.predecessors(specyName))
            print("successors")
            print(self.successors(specyName))

    def plotFeedbackLoopsSpecies(self, cmap="Reds"):
        """Returns and plots species part of feedback loops


        :param str cmap: a color map
        :return: dictionary with key (species) and values (number of feedback loop 
            containing the species) pairs.


        """
        #import matplotlib
        from pylab import flatten
        data = nx.simple_cycles(self)
        data = list(flatten(data))
        if len(data) == 0:
            print("no loops found")
            return
        counting = [(x, data.count(x)) for x in self.nodes() if data.count(x)!=0 and "and" not in x and "^" not in x]

        M = float(max([count[1] for count in counting]))
        # set a default
        #for node in self.nodes():
        #    self.node[node]['loops'] = "#FFFFFF"
        for node in self.nodes():
            self.node[node]['loops'] = 0

        for count in counting:
            #ratio_count = sm.to_rgba(count[1]/M)
            ratio_count = count[1]/M
            colorHex = ratio_count
            #self.node[count[0]]['loops'] = colorHex
            self.node[count[0]]['loops'] = ratio_count
            self.node[count[0]]['style'] =  'filled,bold'

        self.plotdot(node_attribute="loops", cmap=cmap)
        return counting

    def plotFeedbackLoopsHistogram(self):
        """Plots histogram of the cycle lengths found in the graph

        :return: list of lists containing all found cycles
        """
        import networkx as nx
        from pylab import hist, title
        data = list(nx.simple_cycles(self))
        hist([len(x) for x in data])
        title("Length of the feedback loops")
        return data


    def summary(self):
        """Plot information about the graph"""
        import networkx as nx
        flow = nx.flow_hierarchy(self)
        print("Flow hierarchy = %s (fraction of edges not participating in cycles)" % flow)
        print("Average degree = " + str(sum(self.degree().values())/float(len(self.nodes()))))


    def merge_nodes(self, nodes, node):
        """Merge several nodes into a single one

        .. todo:: check that if links of the inputs or outputs are different, there is no ambiguity..


        .. plot::
            :include-source:
            :width: 50%

            from cellnopt.core import *
            from pylab import subplot
            c = CNOGraph()
            c.add_edge("AKT2", "B", link="+")
            c.add_edge("AKT1", "B", link="+")
            c.add_edge("A", "AKT2", link="+")
            c.add_edge("A", "AKT1", link="+")
            c.add_edge("C", "AKT1", link="+")
            subplot(1,2,1)
            c.plotdot(hold=True)
            c.merge_nodes(["AKT1", "AKT2"], "AKT")
            subplot(1,2,2)
            c.plotdot(hold=True)


        """
        assert len(nodes)>1, "nodes must be a list of species"
        for n in nodes:
            if n not in self.nodes():
                raise ValueError("%s not found in the graph !" % n)
        
        self.add_node(node)

        for n in nodes:
            for pred in self.predecessors(n):
                attrs = self.edge[pred][n]
                if "^" in pred:
                    pred = self._rename_node_in_reaction(pred, n, node)
                    self.add_reaction(pred)
                else:
                    self.add_edge(pred, node, **attrs)
            for succ in self.successors(n):
                attrs = self.edge[n][succ]
                if "^" in succ:
                    succ = self._rename_node_in_reaction(succ, n, node)
                    self.add_reaction(succ)
                else:
                    self.add_edge(node, succ, **attrs)
        for n in nodes:
            self.remove_node(n)

    def split_node(self, node, nodes):
        """

        .. plot::
            :include-source:
            :width: 50%

            from cellnopt.core import *
            from pylab import subplot
            c = CNOGraph()
            c.add_reaction("!A=C")
            c.add_reaction("B=C")
            c.add_reaction("!b1=B")
            c.add_reaction("b2=B")
            c.expand_and_gates()

            subplot(1,2,1)
            c.plotdot(hold=True)

            c.split_node("B", ["B1", "B2", "B3"])
            subplot(1,2,2)
            c.plotdot(hold=True)

       """
        for n in nodes:
            for pred in self.predecessors(node):
                attrs = self.edge[pred][node]
                if "^" in pred:
                    pred = self._rename_node_in_reaction(pred, node, n)
                    self.add_reaction(pred)
                else:
                    self.add_edge(pred, n, **attrs)

            for succ in self.successors(node):
                attrs = self.edge[node][succ]
                # special case of the AND gates
                if "^" in succ:
                    succ = self._rename_node_in_reaction(succ, node, n)
                    self.add_reaction(succ)
                else: # normal case
                    self.add_edge(n, succ, **attrs)
        self.remove_node(node)
    
    def _rename_node_in_reaction(self, reaction, old, new):
        """This function rename a species within a reaction.

        It takes into account that the species may be inhibited or may be part
        of an AND reaction.


        """
        lhs, rhs = reaction.split("=")

        # rename LHS taking ! and AND into account
        species = lhs.split("^")
        new_species = []
        for name in species:
            if name.startswith("!"):
                name = name[1:]
                if name == old:
                    name = new
                new_species.append("!"+name)
            elif name == old:
                new_species.append(new)
            else:
                new_species.append(name)
        if len(new_species) == 1:
            lhs = new_species
        else:
            lhs = "^".join(new_species)

        #rename RHS if needed
        if rhs == old:
            rhs = new

        new_reaction = "=".join([lhs,rhs])
        return new_reaction



    # Repeats the compression until no further compression 
    # can be performed (or the max number of compression cycles has been reached)
    def recursive_compress(self, max_num_iter = 25):
        #the nodes are sorted to obtain every time the same results:
        n = 0
        while self.compressable_nodes and n <= max_num_iter:
            self.compress()
            n+=1
        
        if self.compressable_nodes :
             print("Warning: There still are compressable nodes after {mni} compression cycles".format(mni=max_num_iter))
        
        

    def sif(self):
        """Return a SIF instance corresponding to this graph"""
        s = SIF()
        for r in self.reacID:
            s.add_reaction(r)
        return s

    def findnonc(self):
        """Finds the Non-Observable and Non-Controllable nodes
    
        #. Non observable nodes are those that do not have a path to any measured
           species in the PKN
        #. Non controllable nodes are those that do not receive any information
           from a species that is perturbed in the data.
    
        Such nodes can be removed without affecting the readouts.
    
    
        :param G: a CNOGraph object
        :param stimuli: list of stimuli
        :param stimuli: list of signals
    
        :return: a list of names found in G that are NONC nodes
    
        .. doctest::
    
            >>> from cellnopt.core import *
            >>> from cellnopt.core.nonc import findNONC
            >>> model = cnodata('PKN-ToyMMB.sif')
            >>> data = cnodata('MD-ToyMMB.csv')
            >>> c = CNOGraph(model, data)
            >>> namesNONC = c.nonc()
    
        :Details: Using a floyd Warshall algorithm to compute path between nodes in a
          directed graph, this class
          identifies the nodes that are not connected to any signals (Non Observable)
          and/or any stimuli (Non Controllable) excluding the signals and stimuli,
           which are kept whatever is the outcome of the FW algorithm.
        """
        # some aliases
        from numpy import inf
        assert (self.stimuli!=None and self.signals!=None)
    
        dist = nx.algorithms.floyd_warshall(self)
    
        namesNONC = []
        for node in self.nodes():
            # search for paths from the species to the signals
            spe2sig = [(node, dist[node][s]) for s in self.signals if dist[node][s]!=inf]
            # and from the nstimuli to the species
            sti2spe = [(node, dist[s][node]) for s in self.stimuli if dist[s][node]!=inf]

            if len(spe2sig)==0 or len(sti2spe)==0:
                if node not in self.signals and node not in self.stimuli:
                    namesNONC.append(node)

        namesNONC  = list(set(namesNONC)) # required ?

        return namesNONC


class CNOGraphMultiEdges(CNOGraph, nx.MultiDiGraph):
    """A multiDigraph version could be used but edges are dealt with differntly

        self.edge returns a dictionary of edges not a single edge so some function
        such as as set_edge_attributes have to be rewritten

    """
    def __init__(self, model=None, data=None, verbose=False, **kargs):
        super(CNOGraphMultiEdges, self).__init__(**kargs)

    def set_edge_attributes(self):
        """set all edge attributes to default attributes

        .. seealso:: :meth:`set_default_edge_attribute`
        """
        for edge in self.edges():
            for key in self.edge[edge[0]][edge[1]].keys():

                attrs = self.edge[edge[0]][edge[1]][key]
                attrs = self.set_default_edge_attributes(**attrs)
                self.edge[edge[0]][edge[1]][key] = attrs









