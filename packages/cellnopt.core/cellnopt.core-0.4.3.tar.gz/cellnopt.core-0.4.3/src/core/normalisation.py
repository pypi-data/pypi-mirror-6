# -*- python -*-
#
#  This file is part of cellnopt.core software
#
#  Copyright (c) 2011-2013 - EBI-EMBL
#
#  File author(s): Thomas Cokelaer <cokelaer@ebi.ac.uk>
#
#  Distributed under the GPLv3 License.
#  See accompanying file LICENSE.txt or copy at
#      http://www.gnu.org/licenses/gpl-3.0.html
#
#  website: www.cellnopt.org
#
##############################################################################

# cannot do from cellnopt.core import * ???
import midas
import cnograph
from cnograph import CNOGraph
from midas import MIDASReader
import easydev
import numpy


__all__ = ["NormaliseMIDAS"]


class NormaliseMIDAS(object):
    r"""Class dedicated to the normalisation of MIDAS data

    Before normalisation, the measurements that are out of the dynamic 
    range [:attr:`detection`; :attr:`saturation`] are tagged to be ignored.

    The fold change matrix is computed with a choice of algorithm. The following is
    the mode="time" case (see :meth:`normalise`):

    .. math:: 

        \hat{x} = \frac{\left\lvert X(t) - X(t_0) \right\lvert }{ X(t_0)}

    Then, a penalty coefficient is computed as follows:

    .. math:: P(t) = \frac{X(t)}{ EC_{50}^{(noise)} + X(t)}


    and the a new matrix is computed using a Hill transformation:

    .. math::

       H(t) = \frac{X^{k_H}}{ {EC_{50}^{(data)}}^{k_H} + X^{k_H} }

    rescale negative values. 

    For each specy over all experiment and time, if a negative value is found and then the column is rescaled as follows:

    .. math:: X(t) = P(t) H(t)

    .. math:: X_{s}(t) = \frac{X_{s}(t) - m_s }{M_s - m_s}

    where m_s and M_s are the minimum and maximum value over time and 
    experiment for the given specy :math:`s`.
    

    


    """
    def __init__(self, data, mode="time", verbose=True, saturation=numpy.inf, 
                 detection=0., EC50noise=0., EC50data=0.5, HillCoeff=2.,
                changeThreshold=0., rescale_negative=True):
        """.. rubric:: constructor

        :param data: the MIDAS data. Could be a filename, an instance of MIDASReader 
            or an instance of CNOGraph.
        :param mode: either "time" or "ctrl". :math:`X(t)` is a matrix with experiments as 
            rows and species as columns. If mode is "time", the relative change is X(t) - X(t=t0).
            In other word, each measurement is compared to the exact same condition at time 0.
            If mode is "ctrl", the relative change is computed relative to the
            control at the same time, which is case without stimuli, but with the same
            inhibitors. 
        :param float saturation: 
        :param float detection:
        :param float EC50noise:
        :param float EC50data:
        :param float HillCoeff:
        :param float changeThres:
        :param bool rescale_negative: 
        :param verbose: print informative messages
        

    
	"""
        if isinstance(data, str):
            self.midas = MIDASReader(data)
        elif isinstance(data, MIDASReader):
            self.midas = data # a reference ?
        elif isinstance(data, CNOGraph):
            self.midas = data.copy()
        else:
            raise TypeError("data must be either a filename or an instance of MIDASReader or CNOGraph")

        self.data = numpy.array(self.midas.cnolist.valueSignals)

        self.verbose = verbose

        # read-write attributes
        self.mode = mode
        self.saturation = saturation
        self.EC50noise = EC50noise
        self.EC50data = EC50data
        self.HillCoeff = HillCoeff
        self.changeThreshold = changeThreshold
        self.detection = detection

        
        # read-only attributes
        self.rescale_negative = rescale_negative


    def _get_mode(self):
        return self._mode
    def _set_mode(self, mode):
        easydev.checkParam(mode, ["time", "control"])
        self._mode = mode
    mode = property(_get_mode, _set_mode, doc="todo")

    def _get_saturation(self):
        return self._saturation
    def _set_saturation(self, saturation):
        if isinstance(saturation, (int, long, float)):
            self._saturation = saturation
        else:
            raise TypeError("saturation argument must be a number")
    saturation = property(_get_saturation, _set_saturation, 
        doc="saturation above which measurement are ignored")
    
    def _get_detection(self):
        return self._detection
    def _set_detection(self, detection):
        if isinstance(detection, (int, long, float)):
            self._detection = detection
        else:
            raise TypeError("detection argument must be a number")
    detection = property(_get_detection, _set_detection, 
        doc="detection above which measurement are ignored")


    def _get_EC50noise(self):
        return self._EC50noise
    def _set_EC50noise(self, EC50noise):
        if isinstance(EC50noise, (int, long, float)):
            self._EC50noise = EC50noise
        else:
            raise TypeError("EC50noise argument must be a number")
    EC50noise = property(_get_EC50noise, _set_EC50noise, doc="todo")

    def _get_EC50data(self):
        return self._EC50data
    def _set_EC50data(self, EC50data):
        if isinstance(EC50data, (int, long, float)):
            self._EC50data = EC50data
        else:
            raise TypeError("EC50data argument must be a number")
    EC50data = property(_get_EC50data, _set_EC50data, doc="todo")

    def _get_changeThreshold(self):
        return self._changeThreshold
    def _set_changeThreshold(self, changeThreshold):
        if isinstance(changeThreshold, (int, long, float)):
            self._changeThreshold = changeThreshold
        else:
            raise TypeError("changeThreshold argument must be a number")
    changeThreshold = property(_get_changeThreshold, _set_changeThreshold, doc="todo")


    def _get_HillCoeff(self):
        return self._HillCoeff
    def _set_HillCoeff(self, HillCoeff):
        if isinstance(HillCoeff, (int, long, float)):
            self._HillCoeff = HillCoeff
        else:
            raise TypeError("HillCoeff argument must be a number")
    HillCoeff = property(_get_HillCoeff, _set_HillCoeff, doc="todo")

    def dynamicRange(self):
        """Returns a mask to ignore values out of the dynamic range

        This function masks values out of the dynamic range defined by the :attr:`detection`
        and :attr:`saturation`.

	:return: a numpy mask on the data matrix
        """
        # create a mask for the data dynamic range
        if self.verbose:
            N = len(self.data[self.data>self.saturation])
            if N>0:
                print("found %s values above saturation (%s). " % (N, self.saturation))

        # deal with saturation threshold
        data = numpy.where(self.data > self.saturation, numpy.inf, self.data)

        # here below, self.data must not be used
        if self.verbose:
            N = len(data[data<self.detection])
            if N>0:
                print("found %s values below detection (%s). " % (N, self.detection))
        # deal with detection threshold
        data = numpy.where(data < self.detection, numpy.inf, data) 
        
        if self.verbose:
            N = numpy.sum(numpy.isnan(data))
            if N>0:
                print("found %s NAN values. " % (N))

        # set NA to infinite
        data[numpy.isnan(data)] = numpy.inf
        
        return numpy.isfinite(data)

    def normalise(self):
        """Performs the normalisation using the :attr:`mode` attribute"""
        if self.verbose:
            print("normalise using the mode '%s'" % self.mode)

        if self.mode == "time":
            res = self.timeNormalisation()
        else:
            raise NotImplementedError()
        return res 

    def _get_masked_dynamic_range(self):
        y = numpy.ma.masked_where(self.dynamicRange()==False, self.data)
        return y
    
    def _get_masked_pos(self):
        return numpy.ma.masked_inside((self.data-self.data[0,:,:]), self.changeThreshold, numpy.inf)

    def _get_masked_neg(self):
        return numpy.ma.masked_inside((self.data-self.data[0,:,:]), -numpy.inf, -self.changeThreshold)

    def _get_masked_ignore(self):
        return numpy.ma.masked_inside((self.data-self.data[0,:,:]), -self.changeThreshold, self.changeThreshold)

    def timeNormalisation(self):
        """Performs the normalisation over time. See the class docstring for details."""        
        # create a mask with values within the 
        y = self._get_masked_dynamic_range()
        
        # todo: right now changeThr is absolute like in CellNOptR, but it would be better
        # to implement changeThreshold in a relative manner.
        # we could also uise the langmuir function like in the paper Saez MSB 2009
        
        #1. Compute the max across all measurements for each signal, excluding 
        # the values out of the dynamic range
        signalMax = numpy.max(y, axis=0)
        # for debugging
        self._signalMax = signalMax 

        foldChange = abs(y-y[0,:,:])/y[0,:,:]
        # for debugging
        self._foldChange = foldChange

        # 2. get the saturation penalty using EC50noise 
        # compute the penalty for being noisy, which is calculated for each
        # measurement as the measurement divided by the max measurement across all
        # conditions and time for that particular signal (excluding values out of the
        # dynamic range).
        data = y/signalMax

        satPenalty = data / (self.EC50noise + data)
        # for debugging
        self._satPenalty = satPenalty
    
        # Now I make the data go through the Hill function
        HillData = foldChange**self.HillCoeff/((self.EC50data**self.HillCoeff)+(foldChange**self.HillCoeff))
        # for debugging
        self._HillData = HillData

        # multiply HillData and SatPenalty, matrix by matrix and element by element.
        NormData = HillData * satPenalty

        # use masked_dynamic_range to set to NAN values out of dynamic range
        NormData[y.mask] = numpy.nan

        # multiply negative values by -1
        #NormData[self._get_masked_pos().mask] *= -1
        NormData[self._get_masked_neg().mask] *= -1 

        # set non significant values to zero
        NormData[self._get_masked_ignore().mask] = 0


        # rescale negative values
        if self.rescale_negative:
            # search for min and max over each colum ignoring time=t0
            m = numpy.nanmin(NormData, axis=0).data[0]
            M = numpy.nanmax(NormData, axis=0).data[0]
            # loop over species
            for i, x in enumerate(m):
                if m[i] <0 and m[i]!=M[i]:
                    NormData[:,:,i] = (NormData[:,:,i] - m[i] ) / (M[i] - m[i])

        normdata = NormData.data
        
        """
signalMax
        A   B   C   D   E 
800 900 600 400 800 

PenaltyList
 0.5 0.5 0.6666667 1 0.5
[1,] 1 1 0.65 0.5 NA
[1,] 0.5 1.125 1 0.0025 1

SatPenalty
[1,] 0.8333333 0.8333333 0.8695652 0.9090909 0.8333333
[1,] 0.9090909 0.9090909 0.8666667 0.8333333 NA
[1,] 0.8333333 0.9183673 0.9090909 0.02439024 0.9090909

foldchangeList
[1,]    0    0    0    0    0
[1,] 1 1 0.025 0.5 NA
[1,] 0 1.25 0.5 0.9975 1

hilldata
[1,]    0    0    0    0    0
[1,] 0.8 0.8 0.002493766 0.5 NA
[1,] 0 0.862069 0.5 0.7991978 0.8

normdata
 A B C D E
[1,] 0 0 0 0 0
[1,] 0.7272727 0.7272727 0 -0.4166667 0
[1,] 0 0.791696 0.4545455 -0.01949263 0.7272727

     A B C D E
[1,] 0 0 0 1 0
[1,] 0.7272727 0.7272727 0 0 NaN
[1,] 0 NaN 0.4545455 0.9532177 0.7272727

"""
        # finally set to zero values that are not significant.
        return normdata

    def control_normalisation(self):
        """   A   B   C   D   E
	[1,] 400 400 400 400 400
	[2,] 400 400 400 400 400
	$`10`
	[1,] 800 800 390 200 NA
	[2,] 400 400 400 400 NA
	$`20`
	[1,] 400 900 600   1 800
	[2,] 400 400 400 400 400

	   [,1] [,2] [,3] [,4] [,5]
	[1,]    0    0    0    0    0
	[2,]    0    0    0    0    0
	$`10`
	[1,] 1 1 0.025 0.5 NA
	[2,] 0 0 0.000 0.0 NA
	$`20`
	[1,] 0 1.25 0.5 0.9975 1
	[2,] 0 0.00 0.0 0.0000 0
	"""
	pass



"""
    if(mode == "ctrl"){

    # if mode="ctrl" then the relative change is computed relative to the
    # ctrl at the same time the ctrl is the case without stimuli, but with the same
    # inhibitors.   In our case this still means that at t0 we are going to have
    # zero everywhere since only two measurements were made: with and without the
    # inhibitor(s) and these measurements have been copied across corresponding
    # position this last bit makes sense because we assume that the inhibitors are
    # already present at time 0 when we add the stimuli to find the right row to
    # normalise, we look for a row in the valueStimuli that has only 0's but where
    # the corresponding row in the inhibitor matrix has the same status as the row
    # that we are trying to normalise.
        for(i in 2:length(FoldChangeList)){
            for(n in 1:dim(FoldChangeList[[i]])[1]){
                #First I treat the rows that are not ctrls
                if(sum(CNOlist@stimuli[n,]) != min(apply(CNOlist@stimuli,MARGIN=1,sum))){
                    ctrlRow <- intersect(
                        which(
                            apply(CNOlist@stimuli,MARGIN=1,sum) ==
                                min(apply(CNOlist@stimuli,MARGIN=1,sum))),
                        which(
                            apply(CNOlist@inhibitors,MARGIN=1,
                                function(x) all(x == CNOlist@inhibitors[n,]))))
                    FoldChangeList[[i]][n,] <- abs(CNOlist@signals[[i]][n,] - CNOlist@signals[[i]][ctrlRow,])/CNOlist@signals[[i]][ctrlRow,]
                    negList[[i]][n,which((CNOlist@signals[[i]][n,] - CNOlist@signals[[i]][ctrlRow,]) < (-1*changeTh) )] <- TRUE
                    posList[[i]][n,which((CNOlist@signals[[i]][n,] - CNOlist@signals[[i]][ctrlRow,]) > changeTh )] <- TRUE

                    }else{

                        #Then I set to 0 all the rows that are ctrls
                        FoldChangeList[[i]][n,] <- rep(0,dim(FoldChangeList[[i]])[2])
                    }
                }
            }
            FoldChangeList[[1]] <- matrix(
                0,
                ncol=dim(FoldChangeList[[1]])[2],
                nrow=dim(FoldChangeList[[1]])[1])
        }
}
"""
