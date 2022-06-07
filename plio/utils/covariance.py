import numpy as np
import math

def compute_covariance(lat, lon, rad, latsigma=10., lonsigma=10., radsigma=15., semimajor_axis=None):
    """
    Given geospatial coordinates, desired ground distance accuracies in meters (sigmas), and an equatorial 
    radius, computes the rectangular covariance matrix using error propagation.

    Returns a 2x3 rectangular matrix containing the upper triangle of the rectangular covariance matrix.

    Parameters
    ----------
    lat : float
          A point's geocentric latitude in degrees

    lon : float
          A point's longitude in degrees

    rad : float
          The radius (z-value) of the point in meters

    latsigma : float
               The ground distance uncertainty in the latitude direction in meters (Default 10.0)

    lonsigma : float
               The ground distance uncertainty in the longitude direction in meters (Default 10.0)

    radsigma : float
               The radius uncertainty in meters (Default: 15.0)

    semimajor_axis : float
                     The semi-major or equatorial radius in meters. If not entered,
                     the local radius will be used.

    Returns
    -------
    rectcov : ndarray
              upper triangle of the covariance matrix in rectangular coordinates stored in a 
              rectangular (2,3) matrix. 
              __          __            __         __
              | c1  c2  c3 |           | c1  c2  c3 |
              | c4  c5  c6 |    --->   | c5  c6  c9 |
              | c7  c8  c9 |            __         __
              __          __


    """
    lat = math.radians(lat)
    lon = math.radians(lon)

    if semimajor_axis is None:
        semimajor_axis = rad

    # SetSphericalSigmasDistance
    scaled_lat_sigma = latsigma / semimajor_axis

    # This is specific to each lon.
    scaled_lon_sigma = lonsigma / (math.cos(lat) * semimajor_axis)

    # Calculate the covariance matrix in latitudinal coordinates
    # assuming no correlation
    cov = np.eye(3,3)
    cov[0,0] = scaled_lat_sigma ** 2
    cov[1,1] = scaled_lon_sigma ** 2
    cov[2,2] = radsigma ** 2

    # Calculate the jacobian of the transformation from latitudinal to rectangular coordinates
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

    # Conjugate the latitudinal covariance matrix by the jacobian (error propagation formula)
    mat = j.dot(cov)
    mat = mat.dot(j.T)

    # Extract the upper triangle 
    rectcov = np.zeros((2,3))
    rectcov[0,0] = mat[0,0]
    rectcov[0,1] = mat[0,1]
    rectcov[0,2] = mat[0,2]
    rectcov[1,0] = mat[1,1]
    rectcov[1,1] = mat[1,2]
    rectcov[1,2] = mat[2,2]
    return rectcov
