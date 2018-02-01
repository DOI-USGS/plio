import numpy as np
import pandas as pd
from pandas.util.testing import assert_frame_equal

from plio.io.io_gpf import read_gpf
from plio.io.io_gpf import save_gpf
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
