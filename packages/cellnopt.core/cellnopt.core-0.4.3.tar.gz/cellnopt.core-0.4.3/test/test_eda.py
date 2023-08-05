from cellnopt.core.io.eda import EDA
from cellnopt.core.sif import SIF
import easydev

filename = easydev.get_share_file("cellnopt.core", "data", "simple.eda") 
sifname = easydev.get_share_file("cellnopt.core", "data", "simple.sif") 



def test_eda():
   e = EDA(filename)
   s1 = e.export2sif()
   s2 = SIF(sifname)
   assert s1 == s2
