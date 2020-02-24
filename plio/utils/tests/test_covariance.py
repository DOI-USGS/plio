import numpy as np

import pytest

from plio.utils import covariance

def test_compute_covariance():
    # This test is using values from an ISIS control network
    lat = 86.235596
    lon = 140.006195
    rad = 1736777.625
    sigmalat = 15.0
    sigmalon = 15.0
    sigmarad = 25.0
    semimajor_rad = 1737400.0
    cov = covariance.compute_covariance(lat, lon, rad, sigmalat, sigmalon, sigmarad, semimajor_rad)
    expected =  np.array([[225.85120968, -0.84930178, -20.08405416233],
                          [225.55132129, 16.848822261184, 623.27512692323]])
    np.testing.assert_almost_equal(cov, expected)
