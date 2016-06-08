import unittest

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