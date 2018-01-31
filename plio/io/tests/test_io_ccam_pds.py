import os
import sys
import unittest

sys.path.insert(0, os.path.abspath('..'))

from plio.examples import get_path
from plio.io import io_ccam_pds

class Test_CCAM_IO(unittest.TestCase):

    def setUp(self):
        self.examplefile = get_path('CL5_398645626CCS_F0030004CCAM02013P3.csv')

    def test_14_item_header_csv(self):
        io_ccam_pds.CCAM_CSV(self.examplefile)

if __name__ == '__main__':
    unittest.main()
