import os
import sys
import unittest

import pandas as pd

sys.path.insert(0, os.path.abspath('..'))

from plio.examples import get_path
from plio.io import io_spectral_profiler


class Test_Spectral_Profiler_IO(unittest.TestCase):
    
    def setUp(self):
        self.examplefile = get_path('SP_2C_02_02358_S138_E3586.spc')
    
    def test_openspc(self):
        ds = io_spectral_profiler.Spectral_Profiler(self.examplefile)
        self.assertEqual(ds.nspectra, 38)
        self.assertIsInstance(ds.spectra, pd.Panel)
        self.assertEqual(ds.spectra[0].columns.tolist(), ['RAW', 'REF1', 'REF2', 'QA'])


if __name__ == '__main__':
    unittest.main()
