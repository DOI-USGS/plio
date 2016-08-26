import os
import sys
import unittest

from plio.examples import get_path

sys.path.insert(0, os.path.abspath('..'))

from plio.io import isis_serial_number


class TestIsisSerials(unittest.TestCase):

    def test_generate_serial_number(self):
        label = get_path('Test_PVL.lbl')
        serial = isis_serial_number.generate_serial_number(label)
        self.assertEqual('APOLLO15/METRIC/1971-07-31T14:02:27.179', serial)