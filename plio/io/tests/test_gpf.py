import numpy as np
import pandas as pd

from plio.io.io_gpf import read_gpf
from plio.examples import get_path

import pytest

@pytest.fixture
def insight_gpf():
    return get_path('InSightE08_XW.gpf')

@pytest.mark.parametrize('gpf, expected', [(insight_gpf(),'foo')])
def test_read_gfp(gpf, expected):
    df = read_gpf(gpf)
    print(df)
    assert False
