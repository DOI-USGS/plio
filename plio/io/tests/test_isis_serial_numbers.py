import os
import sys

import pytest

from plio.io import isis_serial_number
from plio.examples import get_path

@pytest.fixture
def apollo_lbl():
    return get_path('Test_PVL.lbl')

@pytest.fixture
def ctx_lbl():
    return get_path('ctx.pvl')

@pytest.mark.parametrize("label, expected", [(apollo_lbl(), 'APOLLO15/METRIC/1971-07-31T14:02:27.179'),
                                             (ctx_lbl(),'MRO/CTX/0906095311:038')
                                             ])
def test_generate_serial_number(label, expected):
    serial = isis_serial_number.generate_serial_number(label)
    assert serial == expected

    