import numpy as np
import math

def compute_covariance(lat, lon, rad, latsigma=10., lonsigma=10., radsigma=15., semimajor_axis=None):
    """
    Given geospatial coordinates, desired accuracy sigmas, and an equitorial radius, compute a 2x3
    sigma covariange matrix.

    Parameters
    ----------
    lat : float
          A point's latitude in degrees

    lon : float
          A point's longitude in degrees

    rad : float
          The radius (z-value) of the point in meters

    latsigma : float
               The desired latitude accuracy in meters (Default 10.0)

    lonsigma : float
               The desired longitude accuracy in meters (Default 10.0)

    radsigma : float
               The desired radius accuracy in meters (Defualt: 15.0)

    semimajor_axis : float
                     The semi-major or equitorial radius in meters. If not entered,
                     the local radius will be used.

    Returns
    -------
    rectcov : ndarray
              (2,3) covariance matrix

    """
    lat = math.radians(lat)
    lon = math.radians(lon)

    if semimajor_axis is None:
        semimajor_axis = rad

    # SetSphericalSigmasDistance
    scaled_lat_sigma = latsigma / semimajor_axis

    # This is specific to each lon.
    scaled_lon_sigma = lonsigma / (math.cos(lat) * semimajor_axis)

    # SetSphericalSigmas
    cov = np.eye(3,3)
    cov[0,0] = scaled_lat_sigma ** 2
    cov[1,1] = scaled_lon_sigma ** 2
    cov[2,2] = radsigma ** 2

    # Approximate the Jacobian
    j = np.zeros((3,3))
    cosphi = math.cos(lat)
    sinphi = math.sin(lat)
    coslambda = math.cos(lon)
    sinlambda = math.sin(lon)
    rcosphi = rad * cosphi
    rsinphi = rad * sinphi
    j[0,0] = -rsinphi * coslambda
    j[0,1] = -rcosphi * sinlambda
    j[0,2] = cosphi * coslambda
    j[1,0] = -rsinphi * sinlambda
    j[1,1] = rcosphi * coslambda
    j[1,2] = cosphi * sinlambda
    j[2,0] = rcosphi
    j[2,1] = 0.
    j[2,2] = sinphi

    mat = j.dot(cov)
    mat = mat.dot(j.T)
    rectcov = np.zeros((2,3))
    rectcov[0,0] = mat[0,0]
    rectcov[0,1] = mat[0,1]
    rectcov[0,2] = mat[0,2]
    rectcov[1,0] = mat[1,1]
    rectcov[1,1] = mat[1,2]
    rectcov[1,2] = mat[2,2]
    return rectcov
