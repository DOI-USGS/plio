import os
import sys
import unittest

import pandas as pd

sys.path.insert(0, os.path.abspath('..'))

from plio.examples import get_path
from plio.io import io_tes
from plio.io.io_gdal import GeoDataset

class Test_Tes_IO(unittest.TestCase):

    def setUp(self):
        self.examplefile = get_path('pos10001.tab')

    def test_openspc(self):
        ds = io_tes.Tes(self.examplefile)
        self.assertEqual(ds.data.size, 119106)
        self.assertIsInstance(ds.data, pd.DataFrame)
        self.assertEqual(ds.data.columns.tolist(), ['sclk_time', 'et', 'pos', 'sun', 'quat', 'id'])

if __name__ == '__main__':
    unittest.main()
