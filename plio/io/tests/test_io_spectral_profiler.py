import os
import sys
import unittest

import pandas as pd

sys.path.insert(0, os.path.abspath('..'))

from plio.examples import get_path
from plio.io import io_spectral_profiler
from plio.io.io_gdal import GeoDataset

class Test_Spectral_Profiler_IO(unittest.TestCase):

    def setUp(self):
        self.examplefile = get_path('SP_2C_02_02358_S138_E3586.spc')

    def test_openspc(self):
        ds = io_spectral_profiler.Spectral_Profiler(self.examplefile)
        self.assertEqual(ds.nspectra, 38)
        self.assertEqual(ds.spectra[0].columns.tolist(), ['RAW', 'REF1', 'REF2', 'QA', 'RAD'])
    
    @pytest.mark.skipif(gdal is None, reason="GDAL not installed")
    def test_read_browse(self):
        ds = io_spectral_profiler.Spectral_Profiler(self.examplefile)
        ds.open_browse()
        self.assertIsInstance(ds.browse, GeoDataset)
        self.assertEqual(ds.browse.read_array().shape, (512, 456))

if __name__ == '__main__':
    unittest.main()
