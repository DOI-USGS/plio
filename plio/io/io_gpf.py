import math
import numpy as np
import pandas as pd


GPF_DATA_DTYPE = np.dtype([('point_id', np.int), ('stat', np.int), ('known', np.int),
                  ('lat_Y_North', np.float), ('long_X_East', np.float), ('ht', np.float),
                  ('sigma0', np.float), ('sigma1', np.float), ('sigma2', np.float),
                  ('res0', np.float), ('res1', np.float), ('res2', np.float)])


def read_gpf(input_data):
    """
    Read a socet gpf file into a pandas data frame

    Parameters
    ----------
    input_file : str
                 path to the input data file

    Returns
    -------
    df : pd.DataFrame
         containing the gfp data with appropriate column names and indices
    """

    # Check that the number of rows is matching the expected number
    with open(input_data, 'r') as f:
        for i, l in enumerate(f):
            if i == 1:
                cnt = int(l)
            elif i == 2:
                col = l
                break



    # Mixed types requires read as unicode - let pandas soft convert
    d = np.genfromtxt(input_data, skip_header=3, dtype='unicode')
    d = d.reshape(-1, 12)

    #TODO: cols should be used to dynamically generate the column names

    df = pd.DataFrame(d, columns=['point_id', 'stat', 'known',
                              'lat_y_North', 'long_X_East','ht',
                              'sigma0', 'sigma1', 'sigma2',
                              'res0', 'res1', 'res2'])
    # Soft conversion of numeric types to numerics
    df = df.apply(pd.to_numeric, errors='ignore')

    # Validate the read data with the header point count
    assert int(cnt) == len(df)

    return df
