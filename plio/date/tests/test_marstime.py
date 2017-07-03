import numpy as np
import unittest

from .. import marstime


class TestSmallJulian(unittest.TestCase):
    def runTest(self):
        earth = marstime.getUTCfromLS(24, 130)
        mars = marstime.getMTfromTime(earth)
        assert(earth.date() == marstime.getUTCfromLS(mars.year,mars.ls).date())
