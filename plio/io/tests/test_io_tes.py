import os
import sys
import unittest

import pandas as pd

sys.path.insert(0, os.path.abspath('..'))

from plio.examples import get_path
from plio.io import io_tes
from plio.io.io_gdal import GeoDataset
from plio.io import tes2numpy

class Test_Tes_IO(unittest.TestCase):

    def setUp(self):
        self.examplefile = get_path('pos10001.tab')

    def test_opentab(self):
        ds = io_tes.Tes(self.examplefile)
        self.assertEqual(ds.data.size, 119106)
        self.assertIsInstance(ds.data, pd.DataFrame)
        self.assertEqual(ds.data.columns.tolist(), ['sclk_time', 'et', 'pos', 'sun', 'quat', 'id'])

    def test_tes2numpy(self):
        self.assertEqual(tes2numpy('MSB_UNSIGNED_INTEGER', 4), '>u4')
        self.assertEqual(tes2numpy('MSB_UNSIGNED_INTEGER', 4, 2), [('elem0', '>u4'), ('elem1', '>u4')])

        with self.assertRaises(Exception):
            tes2numpy('IEEE_REAL', 5)

if __name__ == '__main__':
    unittest.main()
