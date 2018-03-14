import json
import numpy as np
import pandas as pd
from pandas.util.testing import assert_frame_equal

from plio.io.io_bae import socet_keywords_to_json, read_gpf, save_gpf
from plio.examples import get_path

import pytest

@pytest.fixture
def insight_gpf():
    return get_path('InSightE08_XW.gpf')

@pytest.fixture()
def insight_expected():
    return pd.read_csv(get_path('InSightE08_XW.csv'))

@pytest.mark.parametrize('gpf, expected', [(insight_gpf(),insight_expected())])
def test_read_gfp(gpf, expected):
    df = read_gpf(gpf)
    assert_frame_equal(df, expected)

@pytest.mark.parametrize('gpf', [(insight_gpf())])
def test_write_gpf(gpf):
    """
    We test by manually comparing files and not using filecmp so that we
    are not testing float point precision differences, e.g. 0.0 == 0.00000000.
    """
    df = read_gpf(gpf)
    save_gpf(df, 'out.gpf')

    with open(gpf) as f:
        fl = f.readlines()

    with open('out.gpf') as f:
        fs = f.readlines()

    # Check that the header is the same
    for i in range(3):
        assert fl[i] == fs[i]

    truth_arr = np.genfromtxt(gpf, skip_header=3)
    test_arr = np.genfromtxt('out.gpf', skip_header=3)
    np.testing.assert_array_almost_equal(truth_arr, test_arr)

def test_create_from_socet_lis():
    socetlis = get_path('socet_isd.lis')
    socetell = get_path('ellipsoid.ell')
    js = json.loads(socet_keywords_to_json(socetlis))
    assert isinstance(js, dict)  # This is essentially a JSON linter
    # Manually validated 
    assert 'RECTIFICATION_TERMS' in js.keys()
    assert 'SEMI_MAJOR_AXIS' in js.keys()  # From ellipsoid file
    assert 'NUMBER_OF_EPHEM' in js.keys()
    assert len(js['EPHEM_PTS']) / 3 == js['NUMBER_OF_EPHEM'] 