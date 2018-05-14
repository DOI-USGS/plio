import os
import math
import pyproj

import plio.io.isis_serial_number as sn

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
    if record['known'] == 0:
        return 'Free'

    elif record['known'] == 1 or record['known'] == 2 or record['known'] == 3:
        return 'Constrained'

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
        pRadius = eRadius * (1 - float(files['E_EARTH'][0]))

        return eRadius, pRadius

def lat_ISIS_coord(record, semi_major, semi_minor):
    """
    Function to convert lat_Y_North to ISIS_lat

    Parameters
    ----------
    record : object
             Pandas series object

    semi_major : float
                 Radius from the center of the body to the equater

    semi_minor : float
                 Radius from the pole to the center of mass

    Returns
    -------
    coord_360 : float
                Converted latitude into ocentric space, and mapped
                into 0 to 360
    """
    ocentric_coord = og2oc(record['lat_Y_North'], semi_major, semi_minor)
    coord_360 = to_360(ocentric_coord)
    return coord_360

def lon_ISIS_coord(record, semi_major, semi_minor):
    """
    Function to convert long_X_East to ISIS_lon

    Parameters
    ----------
    record : object
             Pandas series object

    semi_major : float
                 Radius from the center of the body to the equater

    semi_minor : float
                 Radius from the pole to the center of mass

    Returns
    -------
    coord_360 : float
                Converted longitude into ocentric space, and mapped
                into 0 to 360
    """
    ocentric_coord = og2oc(record['long_X_East'], semi_major, semi_minor)
    coord_360 = to_360(ocentric_coord)
    return coord_360

def body_fix(record, semi_major, semi_minor):
    """
    Transforms latitude, longitude, and height of a socet point into
    a body fixed point

    Parameters
    ----------
    record : object
             Pandas series object

    semi_major : float
                 Radius from the center of the body to the equater

    semi_minor : float
                 Radius from the pole to the center of mass

    Returns
    -------
    : list
      Body fixed lat, lon and height coordinates as lat, lon, ht

    """
    ecef = pyproj.Proj(proj='geocent', a=semi_major, b=semi_minor)
    lla = pyproj.Proj(proj='latlon', a=semi_major, b=semi_minor)
    lon, lat, height = pyproj.transform(lla, ecef, record['long_X_East'], record['lat_Y_North'], record['ht'])
    return lon, lat, height

def apply_transformations(atf_dict, df):
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
    prj_file = os.path.join(atf_dict['PATH'], atf_dict['PROJECT'].split('\\')[-1])

    eRadius, pRadius = get_axis(prj_file)

    df['s.'], df['l.'], df['image_index'] = (zip(*df.apply(line_sample_size, path = atf_dict['PATH'], axis=1)))
    df['known'] = df.apply(known, axis=1)
    df['lat_Y_North'] = df.apply(lat_ISIS_coord, semi_major = eRadius, semi_minor = pRadius, axis=1)
    df['long_X_East'] = df.apply(lon_ISIS_coord, semi_major = eRadius, semi_minor = pRadius, axis=1)
    df['long_X_East'], df['lat_Y_North'], df['ht'] = zip(*df.apply(body_fix, semi_major = eRadius, semi_minor = pRadius, axis = 1))

def serial_numbers(image_dict, path):
    """
    Creates a dict of serial numbers with the cub being the key

    Parameters
    ----------
    images : list

    path : str

    extension : str

    Returns
    -------
    serial_dict : dict
    """
    serial_dict = dict()

    for key in image_dict:
        serial_dict[key] = sn.generate_serial_number(os.path.join(path, image_dict[key]))
    return serial_dict
