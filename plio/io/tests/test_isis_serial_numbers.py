import os
import sys

import pytest

from plio.io import isis_serial_number
from plio.examples import get_path

@pytest.fixture
def label(request):
    return get_path(request.param)

@pytest.mark.parametrize("label, expected", [('Test_PVL.lbl', 'APOLLO15/METRIC/1971-07-31T14:02:27.179'),
                                             ('ctx.pvl','MRO/CTX/0906095311:038'),
                                             ('testing_142.pvl', 'MRO/CTX/1153242990:243')
                                             ], indirect=['label'])
def test_generate_serial_number(label, expected):
    serial = isis_serial_number.generate_serial_number(label)
    assert serial == expected

    