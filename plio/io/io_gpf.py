import numpy as np
import pandas as pd

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

    # Soft conversion of numeric types to numerics, allows str in first col for point_id
    df = df.apply(pd.to_numeric, errors='ignore')

    # Validate the read data with the header point count
    assert int(cnt) == len(df)

    return df

def save_gpf(df, output_file):
    """
    Write a socet gpf file from a gpf-defined pandas dataframe

    Parameters
    ----------
    df          : pd.DataFrame
                  Pandas DataFrame

    output_file : str
                  path to the output data file

    Returns
    -------
    int         : success value
                  0 = success, 1 = errors
    """

    # Check that file can be opened
    try:
        outGPF = open(output_file, 'w', newline='\r\n')
    except:
        print ('Unable to open output gpf file: {0}'.format(output_file))
        return 1

    #grab number of rows in pandas dataframe
    numpts = len(df)

    #Output gpf header
    outGPF.write('GROUND POINT FILE\n')
    outGPF.write('{0}\n'.format(numpts))
    outGPF.write('point_id,stat,known,lat_Y_North,long_X_East,ht,sig(3),res(3)\n')

    for index,row in df.iterrows():
        #Output coordinates to gpf file
        outGPF.write('{0} {1} {2}\n'.format(row['point_id'], row['stat'], row['known']))
        outGPF.write('{0}         {1}         {2}\n'.format(row['lat_y_North'], row['long_X_East'], row['ht']))
        outGPF.write('{0} {1} {2}\n'.format(row['sigma0'], row['sigma1'], row['sigma2']))
        outGPF.write('{0} {1} {2}\n\n'.format(row['res0'], row['res1'], row['res2']))

    outGPF.close()
    return
