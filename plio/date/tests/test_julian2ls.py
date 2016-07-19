import numpy as np
import unittest

from .. import julian2ls


class TestSmallJulian(unittest.TestCase):
    def runTest(self):
        smalldates = np.array([10834, 65432, 11111, 104])
        expected = np.array([177.77841982441714, 9.1150791399559239,
                             343.68773181354481, 335.45117593903956])
        expectedmyn = np.array([40, 120, 40, 24])
        result, myn = julian2ls.julian2ls(smalldates)
        np.testing.assert_allclose(expected, result, rtol=1e-4)
        np.testing.assert_allclose(expectedmyn, myn)


class TestLargeJulian(unittest.TestCase):

    def runTest(self):
        largedates = np.array([1100354, 1260543, 2020511, 1986287])
        expected = np.array([138.01380245992914, 289.56588061130606,
                             103.53916196653154, 165.34239548092592])
        expectedmyn = np.array([-1943, -1710, -603, -653])
        result, myn = julian2ls.julian2ls(largedates)
        np.testing.assert_allclose(expected, result, rtol=1e-4)
        np.testing.assert_allclose(expectedmyn, myn)


class TestReverse(unittest.TestCase):

    def runTest(self):
        expected = np.array([10834.400119543538])
        date = julian2ls.julian2ls(178, marsyear=40, reverse=True)
        np.testing.assert_allclose(date, expected, rtol=1e-4)

class TestLanders(unittest.TestCase):
    """
    Testing against: http://www-mars.lmd.jussieu.fr/mars/time/martian_time.html
    """
    def test_year_start(self):
        result, myn = julian2ls.julian2ls(2435198.5)
        self.assertEqual(myn, 0)
        np.testing.assert_array_almost_equal(result, 354.743, 3)

    def test_curiosity(self):
        result, myn = julian2ls.julian2ls(2456145.7207986116)
        print(result)
        np.testing.assert_array_almost_equal(result, 150.702, 3)

    def test_pathfinder(self):
        result, myn = julian2ls.julian2ls(2450634.2061921293)
        self.assertEqual(myn, 23)
        np.testing.assert_array_almost_equal(result, 142.725, 3)

if __name__ == '__main__':

    unittest.main()
