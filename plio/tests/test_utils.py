import os
import unittest

from ..examples import get_path
from .. import utils

class TestUtils(unittest.TestCase):

    def test_find_in_dict(self):
        d = {'a':1,
             'b':2,
             'c':{
                'd':3,
                'e':4,
                'f':{
                    'g':5,
                    'h':6
                    }
                }
            }

        self.assertEqual(utils.find_in_dict(d, 'a'), 1)
        self.assertEqual(utils.find_in_dict(d, 'f'), {'g':5,'h':6})
        self.assertEqual(utils.find_in_dict(d, 'e'), 4)

    def test_find_nested_in_dict(self):
        d = {'a':1,
            'b':2,
            'c':{
                'd':3,
                'e':4,
                'f':{
                    'g':5,
                    'h':6
                    }
                }
            }

        self.assertEqual(utils.find_nested_in_dict(d, 'a'), 1)
        self.assertEqual(utils.find_nested_in_dict(d, ['c', 'f', 'g']), 5)



    def test_create_and_destroy_directory(self):
        path = utils.create_dir()
        self.assertTrue(os.path.exists(path))
        utils.delete_dir(path)
        self.assertFalse(os.path.exists(path))

    def test_file_to_list(self):
        truth = ['AS15-M-0295_SML.png', 'AS15-M-0296_SML.png',
                 'AS15-M-0297_SML.png', 'AS15-M-0298_SML.png',
                 'AS15-M-0299_SML.png', 'AS15-M-0300_SML.png']

        self.assertEqual(utils.file_to_list(get_path('pngs.lis')), truth)