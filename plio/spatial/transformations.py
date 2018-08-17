import os
import pvl
import math
import pyproj

import numpy as np

import plio.io.isis_serial_number as sn
from plio.utils.utils import find_in_dict

def line_sample_size(record, path):
    """
    Converts columns l. and s. to sample size, line size, and generates an
    image index

    Parameters
    ----------
    record : object
             Pandas series object

    path : str
           Path to the associated sup files for a socet project

    Returns
    -------
    : list
      A list of sample_size, line_size, and img_index
    """
    with open(os.path.join(path, record['ipf_file'] + '.sup')) as f:
        for i, line in enumerate(f):
            if i == 2:
                img_index = line.split('\\')
                img_index = img_index[-1].strip()
                img_index = img_index.split('.')[0]

            if i == 3:
                line_size = line.split(' ')
                line_size = line_size[-1].strip()
                assert int(line_size) > 0, "Line number {} from {} is a negative number: Invalid Data".format(line_size, record['ipf_file'])

            if i == 4:
                sample_size = line.split(' ')
                sample_size = sample_size[-1].strip()
                assert int(sample_size) > 0, "Sample number {} from {} is a negative number: Invalid Data".format(sample_size, record['ipf_file'])
                break


        line_size = int(line_size)/2.0 + record['l.'] + 1
        sample_size = int(sample_size)/2.0 + record['s.'] + 1
        return sample_size, line_size, img_index

def known(record):
    """
    Converts the known field from a socet dataframe into the
    isis point_type column

    Parameters
    ----------
    record : object
             Pandas series object

    Returns
    -------
    : str
      String representation of a known field
    """

    lookup = {0: 'Free',
              1: 'Constrained',
              2: 'Constrained',
              3: 'Constrained'}
    return lookup[record['known']]

def reverse_known(record):
    """
    Converts the known field from an isis dataframe into the
    socet known column

    Parameters
    ----------
    record : object
             Pandas series object

    Returns
    -------
    : str
      String representation of a known field
    """
    lookup = {0:0,
              2:0,
              1:3,
              3:3,
              4:3}
    record_type = record['known']
    return lookup[record_type]

def to_360(num):
    """
    Transforms a given number into 0 - 360 space

    Parameters
    ----------
    num : int
          A given integer

    Returns
    -------
    : int
      num moduloed by 360
    """
    return num % 360

def oc2og(dlat, dMajorRadius, dMinorRadius):
    """
    Ocentric to ographic latitudes

    Parameters
    ----------
    dlat : float
           Latitude to convert

    dMajorRadius : float
                   Radius from the center of the body to the equater

    dMinorRadius : float
                   Radius from the pole to the center of mass

    Returns
    -------
    dlat : float
           Converted latitude into ographic space
    """
    try:
        dlat = math.radians(dlat)
        dlat = math.atan(((dMajorRadius / dMinorRadius)**2) * (math.tan(dlat)))
        dlat = math.degrees(dlat)
    except:
        print ("Error in oc2og conversion")
    return dlat

def og2oc(dlat, dMajorRadius, dMinorRadius):
    """
    Ographic to ocentric latitudes

    Parameters
    ----------
    dlat : float
           Latitude to convert

    dMajorRadius : float
                   Radius from the center of the body to the equater

    dMinorRadius : float
                   Radius from the pole to the center of mass

    Returns
    -------
    dlat : float
           Converted latitude into ocentric space
    """
    try:
        dlat = math.radians(dlat)
        dlat = math.atan((math.tan(dlat) / ((dMajorRadius / dMinorRadius)**2)))
        dlat = math.degrees(dlat)
    except:
        print ("Error in og2oc conversion")
    return dlat

def get_axis(file):
    """
    Gets eRadius and pRadius from a .prj file

    Parameters
    ----------
    file : str
           file with path to a given socet project file

    Returns
    -------
    : list
      A list of the eRadius and pRadius of the project file
    """
    with open(file) as f:
        from collections import defaultdict

        files = defaultdict(list)

        for line in f:

            ext = line.strip().split(' ')
            files[ext[0]].append(ext[-1])

        eRadius = float(files['A_EARTH'][0])
        pRadius = eRadius * math.sqrt(1 - (float(files['E_EARTH'][0]) ** 2))

        return eRadius, pRadius

def reproject(record, semi_major, semi_minor, source_proj, dest_proj, **kwargs):
    """
    Thin wrapper around PyProj's Transform() function to transform 1 or more three-dimensional
    point from one coordinate system to another. If converting between Cartesian
    body-centered body-fixed (BCBF) coordinates and Longitude/Latitude/Altitude coordinates,
    the values input for semi-major and semi-minor axes determine whether latitudes are
    planetographic or planetocentric and determine the shape of the datum for altitudes.
    If semi_major == semi_minor, then latitudes are interpreted/created as planetocentric
    and altitudes are interpreted/created as referenced to a spherical datum.
    If semi_major != semi_minor, then latitudes are interpreted/created as planetographic
    and altitudes are interpreted/created as referenced to an ellipsoidal datum.

    Parameters
    ----------
    record : object
             Pandas series object

    semi_major : float
                 Radius from the center of the body to the equater

    semi_minor : float
                 Radius from the pole to the center of mass

    source_proj : str
                         Pyproj string that defines a projection space ie. 'geocent'

    dest_proj : str
                      Pyproj string that defines a project space ie. 'latlon'

    Returns
    -------
    : list
      Transformed coordinates as y, x, z

    """
    source_pyproj = pyproj.Proj(proj = source_proj, a = semi_major, b = semi_minor)
    dest_pyproj = pyproj.Proj(proj = dest_proj, a = semi_major, b = semi_minor)

    y, x, z = pyproj.transform(source_pyproj, dest_pyproj, record[0], record[1], record[2], **kwargs)
    return y, x, z

def stat_toggle(record):
    if record['stat'] == 0:
        return True
    else:
        return False

def apply_isis_transformations(df, eRadius, pRadius, serial_dict, cub_dict):
    """
    Takes a atf dictionary and a socet dataframe and applies the necessary
    transformations to convert that dataframe into a isis compatible
    dataframe

    Parameters
    ----------
    df : object
         Pandas dataframe object

    eRadius : float
              Equitorial radius

    pRadius : float
              Polar radius

    serial_dict : dict
                  Dictionary mapping serials as keys to images as the values

    extension : str
                String extension of all cubes being used

    cub_path : str
               Path to all cubes being used

    """
    # Convert from geocentered coords (x, y, z), to lat lon coords (latitude, longitude, alltitude)
    ecef = np.array([[df['long_X_East']], [df['lat_Y_North']], [df['ht']]])
    lla = reproject(ecef, semi_major = eRadius, semi_minor = pRadius,
                           source_proj = 'latlon', dest_proj = 'geocent')

    df['long_X_East'], df['lat_Y_North'], df['ht'] = lla[0][0], lla[1][0], lla[2][0]

    # Update the stat fields and add the val field as it is just a clone of stat
    df['stat'] = df.apply(ignore_toggle, axis = 1)
    df['val'] = df['stat']

    # Update the known field, add the ipf_file field for saving, and
    # update the line, sample using data from the cubes
    df['known'] = df.apply(reverse_known, axis = 1)
    df['ipf_file'] = df['serialnumber'].apply(lambda serial_number: serial_dict[serial_number])
    df['l.'], df['s.'] = zip(*df.apply(fix_sample_line, serial_dict = serial_dict,
                                       cub_dict = cub_dict, axis = 1))

    # Add dummy for generic value setting
    x_dummy = lambda x: np.full(len(df), x)

    df['sig0'] = x_dummy(1)
    df['sig1'] = x_dummy(1)
    df['sig2'] = x_dummy(1)

    df['res0'] = x_dummy(0)
    df['res1'] = x_dummy(0)
    df['res2'] = x_dummy(0)

    df['fid_x'] = x_dummy(0)
    df['fid_y'] = x_dummy(0)

    df['no_obs'] = x_dummy(1)
    df['fid_val'] = x_dummy(0)

def apply_socet_transformations(atf_dict, df):
    """
    Takes a atf dictionary and a socet dataframe and applies the necessary
    transformations to convert that dataframe into a isis compatible
    dataframe

    Parameters
    ----------
    atf_dict : dict
               Dictionary containing information from an atf file

    df : object
         Pandas dataframe object

    """
    prj_file = os.path.join(atf_dict['PATH'], atf_dict['PROJECT'])

    eRadius, pRadius = get_axis(prj_file)

    lla = np.array([[df['long_X_East']], [df['lat_Y_North']], [df['ht']]])

    ecef = reproject(lla, semi_major = eRadius, semi_minor = pRadius,
                              source_proj = 'geocent', dest_proj = 'latlon')

    df['s.'], df['l.'], df['image_index'] = (zip(*df.apply(line_sample_size, path = atf_dict['PATH'], axis=1)))
    df['known'] = df.apply(known, axis=1)
    df['long_X_East'] = ecef[0][0]
    df['lat_Y_North'] = ecef[1][0]
    df['ht'] = ecef[2][0]
    df['aprioriCovar'] = df.apply(compute_cov_matrix, semimajor_axis = eRadius, axis=1)
    df['stat'] = df.apply(stat_toggle, axis=1)

# TODO: Does isis cnet need a convariance matrix for sigmas? Even with a static matrix of 1,1,1,1
def compute_sigma_covariance_matrix(lat, lon, rad, latsigma, lonsigma, radsigma, semimajor_axis):

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
    lat = math.radians(lat)
    lon = math.radians(lon)

    # SetSphericalSigmasDistance
    scaled_lat_sigma = latsigma / semimajor_axis

    # This is specific to each lon.
    scaled_lon_sigma = lonsigma * math.cos(lat) / semimajor_axis

    # SetSphericalSigmas
    cov = np.eye(3,3)
    cov[0,0] = math.radians(scaled_lat_sigma) ** 2
    cov[1,1] = math.radians(scaled_lon_sigma) ** 2
    cov[2,2] = radsigma ** 2

    # Approximate the Jacobian
    j = np.zeros((3,3))
    cosphi = math.cos(lat)
    sinphi = math.sin(lat)
    cos_lmbda = math.cos(lon)
    sin_lmbda = math.sin(lon)
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

def compute_cov_matrix(record, semimajor_axis):
    cov_matrix = compute_sigma_covariance_matrix(record['lat_Y_North'], record['long_X_East'], record['ht'], record['sig0'], record['sig1'], record['sig2'], semimajor_axis)
    return cov_matrix.ravel().tolist()



def fix_sample_line(record, serial_dict, cub_dict):
    """
    Extracts the sample, line data from a cube and computes deviation from the
    center of the image

    Parameters
    ----------
    record : dict
             Dict containing the key serialnumber, l., and s.

    serial_dict : dict
                  Maps serial numbers to images

    cub_dict : dict
                     Maps basic cub names to their assocated absoluate path cubs

    Returns
    -------
    new_line : int
               new line deviation from the center

    new_sample : int
                 new sample deviation from the center

    """
    # Cube location to load
    cube = pvl.load(cub_dict[serial_dict[record['serialnumber']]])
    line_size = find_in_dict(cube, 'Lines')
    sample_size = find_in_dict(cube, 'Samples')

    new_line = record['l.'] - (int(line_size / 2.0)) - 1
    new_sample = record['s.'] - (int(sample_size / 2.0)) - 1

    return new_line, new_sample

def ignore_toggle(record):
    """
    Maps the stat column in a record to 0 or 1 based on True or False

    Parameters
    ----------
    record : dict
             Dict containing the key stat
    """
    if record['stat'] == True:
        return 0
    else:
        return 1
