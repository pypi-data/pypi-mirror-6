


import os
import csv


class EDA(object):
    """Reads networks in EDA format


    EDA format is similar to SIF but provides a weight on each edge.

    So, it looks like::

        A (1) B = .5
        B (1) C =  1
        A (1) C = .1

    """
    def __init__(self, filename, threshold=0.5,verbose=False):
        """

        :param str filename:
        :param float threshold:
        :param bool verbose:


        """
        self.filename = filename
        self.verbose = verbose
        assert threshold >0 and threshold<1, "threshold must be in ]0,1["
        self.threshold = threshold
        try:
            self._load()
        except Exception, e:
            print(e)
            print("Could not read the eda file")
            raise Exception

    def _load(self):
        if self.verbose:
            print("Loading EDA scores from %s" % self.filename),
        tail = os.path.split(self.filename)[-1]
        data = open(self.filename)
        data_iter = csv.reader(data, delimiter=" ")
        data_iter = list(data_iter)
        
        if len(data_iter) and "EdgeScore" in data_iter[0]:
            del data_iter[0]

        # skip first row
        #header = data_iter.next()
        data = [] 
        for i, datum in enumerate(data_iter):
            if len(datum) == 5:
                data.append(datum)
            elif len(datum) == 0 or len(datum) == 1:
                print("Found empty line in EDA file %s" %  self.filename)
            else:
                self.error("- Line %s in %s is ill formed (expected 5 columns): %s" % (i,self.filename, datum))
                break
        self.nodes1 = [x[0] for x in data]
        self.nodes2 = [x[2] for x in data]
        self.edges = [x[1] for x in data]
        self.scores = [float(x[4]) for x in data]

    def export2sif(self, threshold=None):
        """Exports EDA data into SIF file

        :param float threshold:

        """
        if threshold == None:
            threshold = self.threshold

        from cellnopt.core.sif import SIF
        s = SIF()
        for n1, score, n2 in zip(self.nodes1, self.scores, self.nodes2):
            if score > self.threshold:
                s.add_reaction("%s=%s" % (n1, n2))
        return s
