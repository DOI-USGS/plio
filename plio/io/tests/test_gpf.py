import numpy as np
import pandas as pd
from pandas.util.testing import assert_frame_equal

from plio.io.io_gpf import read_gpf
from plio.io.io_gpf import save_gpf
from plio.examples import get_path

import filecmp
import pytest

@pytest.fixture

def insight_gpf():
    return get_path('InSightE08_XW.gpf')

def out_insight_gpf():
    return get_path('out_InSightE08_XW.gpf')

@pytest.fixture()
def insight_expected():
    return pd.read_csv(get_path('InSightE08_XW.csv'))

@pytest.mark.parametrize('gpf, expected', [(insight_gpf(),insight_expected())])
def test_read_gfp(gpf, expected):
    df = read_gpf(gpf)
    assert_frame_equal(df, expected)

@pytest.mark.parametrize('gpf, out_gpf', [(insight_gpf(),out_insight_gpf())])
def test_write_gfp(gpf, out_gpf):
    df = read_gpf(gpf)
    val = save_gpf(df, out_gpf)
    assertTrue(filecmp.cmp(gpf, out_gpf, shallow=True), "save_gpf does not create an equal file.")

