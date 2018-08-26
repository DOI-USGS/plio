import json
import os

import numpy as np
import pandas as pd
from pandas.util.testing import assert_frame_equal

from plio.io.io_bae import socetset_keywords_to_dict, read_gpf, save_gpf, read_ipf, save_ipf
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

class TestISDFromSocetLis():

    def test_parse_with_empty_newlines(self):
        # Ensure all keys read when whitespace present
        empty_newlines = r"""T0_QUAT 1.0000000000000000000000000e-01

T1_QUAT 1.0000000000000000000000000e-01"""
        data = socetset_keywords_to_dict(empty_newlines)
        assert len(data.keys()) == 2

    def test_duplicate_key_check(self):
        duplicate_keys = r"""T 1
T 1"""
        with pytest.raises(ValueError):
            data = socetset_keywords_to_dict(duplicate_keys)

    def test_multiple_per_line(self):
        multiple_per_line = r"""T 1 1 1"""
        data = socetset_keywords_to_dict(multiple_per_line)
        assert len(data['T']) == 3

    def test_key_on_different_line(self):
        key_on_different_line = r"""A
0.0 1.00000000000000e+00 2.00000000000000e+00
3.0000000000000e+00 4.00000000000000e+00 5.00000000000000e+00
B 1.0e-01 2.000000e+00 3.00000000000000e+00"""
        data = socetset_keywords_to_dict(key_on_different_line)
        assert len(data['A']) == 6
        assert data['A'] == [0, 1, 2, 3, 4, 5]

        assert len(data['B']) == 3
        assert data['B'] == [0.1, 2, 3]

    def test_key_on_different_line_whitespace(self):
        key_on_different_line_whitespace = r"""A
    0.0 1.00000000000000e+00 2.00000000000000e+00
    3.0000000000000e+00 4.00000000000000e+00 5.00000000000000e+00
B 1.0e-01 2.000000e+00 3.00000000000000e+00"""
        data = socetset_keywords_to_dict(key_on_different_line_whitespace)
        assert len(data['A']) == 6
        assert data['A'] == [0, 1, 2, 3, 4, 5]

        assert len(data['B']) == 3
        assert data['B'] == [0.1, 2, 3]
