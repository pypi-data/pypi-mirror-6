"""This test file cover the cno.midas module"""
from os.path import join as pj
import os.path

from cellnopt.core import *
import numpy



filenames = ['MD-ToyMMB_bis.csv',
             'MD-LiverDREAM.csv']


def test_all_file():
    # this is a nosetests trick to have one test per file reportig in the output
    # and not just one for all files. This way, we now how many files are tested
    for filename in filenames:
        yield readfiles, filename

   
class TestMidas(object):
    def __init__(self):

        self.m = MIDASReader() # try empty file
        self.m = MIDASReader(cnodata('MD-ToyMMB_bis.csv'))

        assert self.m.nrows == 18
        assert self.m.ncols == 18
        assert self.m.TRcol == range(0,4)
        assert self.m.DAcol == range(4,11)
        assert self.m.DVcol == range(11,18)
        #assert self.m.PJcol == []
        #assert self.m.indices['CellLines'] == [0]
        
        assert self.m.names == [
                           'TR:EGF',
                           'TR:TNFa',
                           'TR:Rafi',
                           'TR:PI3Ki',
                           'DA:Akt',
                           'DA:Hsp27',
                           'DA:NFkB',
                           'DA:Erk',
                           'DA:p90RSK',
                           'DA:Jnk',
                           'DA:cJun',
                           'DV:Akt',
                           'DV:Hsp27',
                           'DV:NFkB',
                           'DV:Erk',
                           'DV:p90RSK',
                           'DV:Jnk',
                           'DV:cJun']

        self.m.nInhibitors
        self.m.nStimuli
        self.m.nCues
        self.m.ntimes
        self.m.namesCues

    def test_getitem(self):
        assert self.m['DV:Akt'].all() == numpy.array([ 0. ,  0.7,  0.7,  0. ,
                 0.7,  0.7,  0. ,  0.7,  0.7,  0. ,  0. , 0. ,  0. ,  0. ,
                 0. ,  0. ,  0. ,  0. ]).all()
        try:
            self.m['dummy']
            assert False
        except:
            assert True
    def _test_delitem(self):
        assert self.m.ncols == 18
        self.m.delitem('DV:Akt')
        self.remove("DA:Akt")
        assert self.m.ncols == 17
        
        try:
            self.m.delitem('dummy')
            assert False
        except:
            assert True

    def test_plots(self):
        self.m.plotMSEs()
        self.m.plotExp()
        self.m.plotSim()
    
    #def test_cnolist(self):
    #    assert self.m.cnolist
        
    def test_print(self):
        print self.m
        

def test_export():
    m = MIDASReader(get_share_file("MD-Test.csv"))
    c = m.export2CNOGraph()

def test_celllines():
    c = MIDASReader(get_share_file("MD-MultipleCellLines.csv"), celltype="C1")        


def test_MultiMIDAS():
    c1 = MIDASReader(get_share_file("MD-MultipleCellLines.csv"), celltype="C1")        
    c2 = MIDASReader(get_share_file("MD-MultipleCellLines.csv"), celltype="C2")
    mm = MultiMIDAS()
    mm.addMIDAS(c1)
    mm.addMIDAS(c2)
    mm.cellLines
    mm.plot()


    mm = MultiMIDAS(get_share_file("MD-MultipleCellLines.csv"))

def readfiles(filename):
    m = MIDASReader(cnodata(filename))


def test_compare_pycno_vs_cnor():
    # test all sif files 
    for f in filenames:
        yield compare_pycno_vs_cnor, f
    
    
def compare_pycno_vs_cnor(filename):
    """check that the sif file read by CNOR and pyCNO are identical"""
    filename = cnodata(filename)
    try:
        from cellnopt.wrapper import rpack_CNOR as cnor
        from cellnopt.core import midas
 
        mr = cnor.readMIDAS(filename)
        m = midas.MIDASReader(filename)

        assert sorted(list(mr.rx2('DAcol'))) == sorted([x+1 for x in list(m.DAcol)])
        assert sorted(list(mr.rx2('DVcol'))) == sorted([x+1 for x in list(m.DVcol)])
        assert sorted(list(mr.rx2('TRcol'))) == sorted([x+1 for x in list(m.TRcol)])
    except:
        pass

    # TODO(tc): seems that we need to transpose one matrix. do not seem neat
    #assert numpy.array(m.dataMatrix).all() == numpy.array(mr.dataMatrix).transpose().all()


class Test_MIDASRandomiser(object):
    def __init__(self):
        m = MIDASReader(cnodata("MD-ToyMMB.csv"))
        self.m = MIDASRandomiser(m)

    def test_addnoise_and_plots(self):
        self.m.midas.plot()
        self.m.add_noise(dynamic_range=2)
        self.m.midas.plotExp(color="green")

