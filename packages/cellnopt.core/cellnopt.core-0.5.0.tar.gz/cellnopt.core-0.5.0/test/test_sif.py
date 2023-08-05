from cellnopt.core.sif import SIF
import easydev


simple = easydev.get_share_file("cellnopt.core", "data", "simple.sif")
double = easydev.get_share_file("cellnopt.core", "data", "double.sif")
net = easydev.get_share_file("cellnopt.core", "data", "PKN-ToyMMB.net")
  



def test_sifreader():
    """Test the 2 different ways of coding SIF files

    double contains a relation:
     
        A 1 B C

    that is coded in simple as:

        A 1 B
        A 1 C

    """
    s1 = SIF(simple)
    s2 = SIF(double)

    assert s1.nodes1 == ['A', 'B', 'A']
    assert s1.nodes2 == ['B', 'C', 'C']
    assert s1.edges == ['1', '1', '1']

    assert s1 == s2

    #assert s1.reacID == s2.reacID
    assert s1.specID == s2.specID
    print(s1)
    len(s1)

def test_save():
    s1 = SIF(simple)
    import tempfile
    f = tempfile.NamedTemporaryFile(suffix=".sif")
    print f.name
    s1.save(f.name)
    s3 = SIF(f.name)
    assert s1 == s3
    f.close()

def test_sifreader_wrong():
    try:
        sif = SIF("wrong.sif")
        assert False
    except:
        assert True

    try:
        sif = SIF("missing.sif")
        assert False
    except IOError:
        assert True

    #try:
    #    sif = SIF("wrong.badextension")
    #    assert False
    #except ValueError:
    #    assert True
    #except:
    #    assert False


def test_sif2reaction():
    from cellnopt.data import cnodata
    filename = cnodata("PKN-ToyMMB.sif")
    s = SIF(filename)
    s.add_reaction("a=and1")
    s.add_reaction("b=and1")
    s.add_reaction("and1=c")
    r = s.sif2reaction()
    

def test_operators():
    s1 = SIF()
    s1.add_reaction("a=b")
    s2 = SIF()
    s2.add_reaction("a=b")
    assert s1==s2
    assert (s1 == 1) == False

    s2.add_reaction("a=c")
    assert (s1 == s2) == False


def test_exportsbml():
    s1 = SIF()
    s1.add_reaction("A=C")
    s1.add_reaction("!B=C")
    s1.export2SBMLQual("test.xml")

    s2 = SIF()
    s2.importSBMLQual("test.xml")
    assert s1 == s2
    
