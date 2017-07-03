import numpy as np
import unittest
import datetime

from .. import marstime

class TestMarsTime(unittest.TestCase):
    def equality_test(self):
        earth = marstime.getUTCfromLS(24, 130)
        mars = marstime.getMTfromTime(earth)
        assert(earth.date() == marstime.getUTCfromLS(mars.year,mars.ls).date())

    def test_J2000(self):
        iTime = [2001,11,13,2,45,2]
        testJD = marstime.getJ2000(iTime)
        callibration = 58891502.000000 #test should be this value.
        diff = testJD - callibration
        print(testJD)
        print(diff)
        self.assertTrue(diff == -58890820.38465065)


    def test_UTC(self):
        jd = 2452226.614606
        date = marstime.getUTC(jd)
        callibration = datetime.datetime(2001,11,13,2,45,2)
        diff = callibration - date
        self.assertTrue(str(diff) == '0:00:00.041599')


    def test_LS(self):
        iTime = [2000,1,6,0,0,0]
        lsdata = marstime.getMTfromTime(iTime)
        ls = lsdata.ls
        year = lsdata.year
        callibration = 277.18677
        diff = ls - callibration
        print(diff)
        self.assertAlmostEqual(diff, 0.0)

    def test_SZA(self):
        '''test getSZAfromTime'''
        itime = [2000,1,6,0,0,0]
        lon = 0.0
        lat = 0.0
        expected = 154.261908004
        sza = marstime.getSZAfromTime(itime,lon,lat)
        self.assertAlmostEqual(sza, expected)

    def test_SZAGetTime(self):
        out = marstime.SZAGetTime(0, [1,1,1], 0,0)
        self.assertAlmostEqual(out[1], 9.454213735250395)


    def test_LTfromTime(self):
        '''test getLTfromTime function'''
        iTime = [2000,1,6,0,0,0]
        lon = 0.0
        LTST = marstime.getLTfromTime(iTime,lon)
        expected = 23.648468934
        self.assertAlmostEqual(LTST, expected)
