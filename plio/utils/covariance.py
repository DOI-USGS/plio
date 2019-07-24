import numpy as np

def compute_covariance(lat, lon, radius, semimajor_radius, sigmalat=10.0, sigmalon=10.0, sigmarad=15.0):
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
                     The semi-major or equitorial radius in meters (Default: 1737400.0 - Moon)
    Returns
    -------
    rectcov : ndarray
              (2,3) covariance matrix
    """

    # Get the lat/lon/rad out of the geom
    lat = np.radians(lat)
    lon = np.radians(lon)
    rad = 1 

    # SetSphericalSigmasDistance
    scaled_lat_sigma = sigmalat / semimajor_radius

    # This is specific to each lon.
    scaled_lon_sigma = sigmalon * np.cos(lat) / semimajor_radius

    # SetSphericalSigmas
    cov = np.eye(3,3)
    cov[0,0] = np.radians(scaled_lat_sigma) ** 2
    cov[1,1] = np.radians(scaled_lon_sigma) ** 2
    cov[2,2] = sigmarad ** 2

    # Approximate the Jacobian
    j = np.zeros((3,3))
    cosphi = np.cos(lat)
    sinphi = np.sin(lat)
    cos_lmbda = np.cos(lon)
    sin_lmbda = np.sin(lon)
    rcosphi = rad * cosphi
    rsinphi = rad * sinphi
    j[0,0] = -rsinphi * cos_lmbda
    j[0,1] = -rcosphi * sin_lmbda
    j[0,2] = cosphi * cos_lmbda
    j[1,0] = -rsinphi * sin_lmbda
    j[1,1] = rcosphi * cos_lmbda
    j[1,2] = cosphi * sin_lmbda
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