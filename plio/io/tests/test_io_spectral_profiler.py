import os
import sys
import unittest

import pandas as pd
import pytest

sys.path.insert(0, os.path.abspath('..'))

from plio.examples import get_path
from plio.io import io_spectral_profiler
from plio.io.io_gdal import GeoDataset
from plio.io import gdal


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

class Test_Spectral_Profiler_IO_Detached(unittest.TestCase):
    
    def setUp(self):
        self.examplefile = get_path('SP_2C_03_04184_N187_E0053.spc')
        self.examplelabel = get_path('SP_2C_03_04184_N187_E0053.lbl')
        
    def test_openspc(self):
        ds = io_spectral_profiler.Spectral_Profiler(self.examplefile, self.examplelabel)
        self.assertEqual(ds.nspectra, 38)
        self.assertEqual(ds.spectra[0].columns.tolist(), ['RAW', 'REF1', 'REF2', 'QA', 'RAD'])

if __name__ == '__main__':
    unittest.main()
