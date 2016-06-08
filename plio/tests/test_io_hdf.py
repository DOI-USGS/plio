import os
import unittest

import numpy as np
import pandas as pd

from .. import io_hdf


class TestHDF(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.hdf = io_hdf.HDFDataset('test_io_hdf.hdf', mode='w')
        cls.x = np.array([(0 ,2.,'String'), (1, 3.,"String2")],
                         dtype=[('index', 'i8'),('bar', 'f4'), ('baz', 'O')])
        cls.df = pd.DataFrame(cls.x[['bar', 'baz']], index=cls.x['index'],
                              columns=['bar', 'baz'])

    @classmethod
    def tearDownClass(cls):
        os.remove('test_io_hdf.hdf')

    def test_df_sarray(self):
        converted = self.hdf.df_to_sarray(self.df.reset_index())
        np.testing.assert_array_equal(converted, self.x)

    def test_sarray_df(self):
        converted = self.hdf.sarray_to_df(self.x)
        self.assertTrue((self.df == converted).all().all())


