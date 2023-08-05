from cellnopt.core import *


def test_normalise():
    m = NormaliseMIDAS(get_share_file("MD-unnorm.csv"))
    m.normalise()
