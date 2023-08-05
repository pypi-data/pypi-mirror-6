import pandas as pd
from cellnopt.core import CNOGraph


class CASPOModels(object):
    """Class to read and plot models as exported by CASPO

        >>> import models
        >>> m = models.CASPOModels()
        >>> m.plotdot() # average model, whcih can be obtained with  m.get_average_model()
        >>> m.plotdot(model_number=0)  # indices are m.df.index
        >>> m.plotdot(model_number=0)  # indices are m.df.index

    .. note:: One difficulty is the way ANDs are coded in different software. In CASPO,
        the AND gate is coded as "A+B=C". Note that internally we use ^ especially
        in CNOGraph. Then, an AND edge is splitted in sub edges. so, A+B=C is made
        of 3 edges A -> A+B=C , B -> A+B=C and A+B=C -> C. This explains the wierd
        code in :meth:`plotdot`.

    """
    def __init__(self, filename):
        self.filename = filename
        self.df = pd.read_csv(self.filename)
        self.df.columns = [x.replace("+", "^") for x in self.df.columns]

        self.cnograph = CNOGraph()
        for this in self.df.columns:
            self.cnograph.add_reaction(this)

    def get_average_model(self):
        """Returns the average model

        """
        return self.df.mean(axis=0)


    def plotdot(self, model_number=None, *args, **kargs):
        """

        :param int model_number: model_number as shown by :attr:`df.index`
            if not provided, the average is taken
        """
        if model_number==None:
            model = self.get_average_model()
        else:
            model = self.df.ix[model_number]

        for edge in self.cnograph.edges(data=True):
            link = edge[2]['link']
            if "^" not in edge[0] and "^" not in edge[1]:
                if link=="-":
                    name = "!"+edge[0]+"="+edge[1]
                else:
                    name = edge[0]+"="+edge[1]
                value = model[name]
            elif "^" in edge[0]:
                value = model[edge[0]]
            elif "^" in edge[1]:
                value = model[edge[1]]
            else:
                raise ValueError()
            self.cnograph.edge[edge[0]][edge[1]]["label"] = value
            self.cnograph.edge[edge[0]][edge[1]]["average"] = value

        self.cnograph.plotdot(edge_attribute="average", **kargs)

    def export2sif(self, filename):
        """Exports 2 SIF using the "and" convention

        can read the results with CellNOptR for instance

            >>> library(CellNOptR)
            >>> plotModel(readSIF("test.sif"))
        """
        self.cnograph.export2sif(filename)


