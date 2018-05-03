import json
import os

import numpy as np
import pandas as pd
from pandas.util.testing import assert_frame_equal

from plio.io.io_bae import socetset_keywords_to_json, read_gpf, save_gpf, read_ipf, save_ipf
from plio.examples import get_path

import pytest

@pytest.fixture
def insight_gpf():
    return get_path('InSightE08_XW.gpf')

@pytest.fixture()
def insight_expected_gpf():
    return pd.read_csv(get_path('InSightE08_XW.csv'))

@pytest.fixture
def insight_ipf():
    return get_path('P20_008845_1894_XN_09N203W.ipf')

@pytest.fixture()
def insight_expected_ipf():
    return pd.read_csv(get_path('P20_008845_1894_XN_09N203W.csv'))

@pytest.mark.parametrize('ipf, expected', [([insight_ipf()],insight_expected_ipf())])
def test_read_ifp(ipf, expected):
    df = read_ipf(ipf)
    assert_frame_equal(df, expected)

@pytest.mark.parametrize('gpf, expected', [(insight_gpf(),insight_expected_gpf())])
def test_read_gfp(gpf, expected):
    df = read_gpf(gpf)
    assert_frame_equal(df, expected)

@pytest.mark.parametrize('ipf, file', [(insight_ipf(), 'plio/io/tests/temp')])
def test_write_ipf(ipf, file):
    df = read_ipf(ipf)
    save_ipf(df, file)

    file = os.path.join(file, 'P20_008845_1894_XN_09N203W.ipf')

    with open(ipf) as f:
        fl = f.readlines()

    with open(file) as f:
        fs = f.readlines()

    # Check that the header is the same
    for i in range(3):
        assert fl[i] == fs[i]

    truth_arr = [line.split() for line in open(ipf, 'r')][3:]
    truth_arr = np.hstack(np.array(truth_arr))
    truth_arr = truth_arr.reshape(-1, 12)

    test_arr  = [line.split() for line in open(file, 'r')][3:]
    test_arr = np.hstack(np.array(test_arr))
    test_arr = test_arr.reshape(-1, 12)

    assert (truth_arr == test_arr).all()

@pytest.mark.parametrize('gpf, file', [(insight_gpf(), 'out.gpf')])
def test_write_gpf(gpf, file):
    """
    We test by manually comparing files and not using filecmp so that we
    are not testing float point precision differences, e.g. 0.0 == 0.00000000.
    """
    df = read_gpf(gpf)
    save_gpf(df, file)

    with open(gpf) as f:
        fl = f.readlines()

    with open(file) as f:
        fs = f.readlines()

    # Check that the header is the same
    for i in range(3):
        assert fl[i] == fs[i]

    truth_arr = np.genfromtxt(gpf, skip_header=3)
    test_arr = np.genfromtxt(file, skip_header=3)

    np.testing.assert_array_almost_equal(truth_arr, test_arr)

    # np.testing.assert_array_almost_equal(truth_arr, test_arr)

def test_create_from_socet_lis():
    socetlis = get_path('socet_isd.lis')
    socetell = get_path('ellipsoid.ell')
    js = json.loads(socetset_keywords_to_json(socetlis))
    assert isinstance(js, dict)  # This is essentially a JSON linter
    # Manually validated
    assert 'RECTIFICATION_TERMS' in js.keys()
    assert 'SEMI_MAJOR_AXIS' in js.keys()  # From ellipsoid file
    assert 'NUMBER_OF_EPHEM' in js.keys()
    assert len(js['EPHEM_PTS']) / 3 == js['NUMBER_OF_EPHEM']
