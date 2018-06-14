
import pytest
from plio.examples import get_path
from plio.spatial import transformations as trans

@pytest.mark.parametrize("stat, expected",
                         [({'stat':0}, True),
                          ({'stat':1}, False),
                          ({'stat':True}, False),  # Is this the desired result?
                          ({'stat':False}, True)])
def test_stat_toggle(stat, expected):
    assert trans.stat_toggle(stat) == expected

def test_get_axis():
    fname = get_path('CTX_Athabasca_Middle.prj')
    erad, prad = trans.get_axis(fname)
    assert erad == 3.39619000000000e+006
    assert prad == 3.3762000000000866e+006

@pytest.mark.parametrize("og, major, minor, oc",
                         [(0, 3396190, 3376200, 0),
                          (90, 3396190, 3376200, 90),
                          (-90, 3396190, 3376200, -90),
                          (45, 3396190, 3376200, 44.6617680)])
def test_og2oc(og, major, minor, oc):
    assert trans.og2oc(og, major, minor) == pytest.approx(oc)

@pytest.mark.parametrize("og, major, minor, oc",
                         [(0, 3396190, 3376200, 0),
                          (90, 3396190, 3376200, 90),
                          (-90, 3396190, 3376200, -90),
                          (45.338231, 3396190, 3376200, 45)])
def test_oc2og(og, major, minor, oc):
    assert trans.oc2og(oc, major, minor) == pytest.approx(og)


@pytest.mark.parametrize("known, expected",
                         [({'known':0},'Free'),
                          ({'known':1},'Constrained'),
                          ({'known':2},'Constrained'),
                          ({'known':3},'Constrained'),
                          ({'known':False},'Free'),  # Is this the desired result?
                          ({'known':True},'Constrained')])
def test_known(known, expected):
    assert trans.known(known) == expected

@pytest.mark.parametrize("num, expected",
                         [(0, 0),
                          (-180, 180),
                          (370, 10),
                          (-90, 270), 
                          (90, 90)])
def test_to_360(num, expected):
    assert trans.to_360(num) == expected