import json
import re
from functools import singledispatch

import numpy as np
import pandas as pd

def socetset_keywords_to_json(keywords, ell=None):
    """
    Convert a SocetCet keywords.list file to JSON

    Parameters
    ----------
    keywords : str
               Path to the socetset keywords.list file

    Returns
    -------
     : str
       The serialized JSON string.
    """
    matcher = re.compile(r'\b(?!\d)\w+\b')
    numeric_matcher = re.compile(r'\W-?(?:0|[1-9]\d*)(?:\.\d*)?(?:[eE][+\-]?\d+)?')
    stream = {}

    def parse(fi):
        with open(fi, 'r') as f:
            for l in f:
                l = l.rstrip()
                if not l:
                    continue
                matches = matcher.findall(l)
                if matches:
                    key = matches[0]
                    stream[key] = []
                    # Case where the kw are strings after the key
                    if len(matches) > 1:
                        stream[key] = matches[1:]
                    # Case where the kw are numeric types after the key
                    else:
                        nums = numeric_matcher.findall(l)
                        if len(nums) == 1:
                            stream[key] = float(nums[0])
                        else:
                            stream[key] += map(float, nums)
                else:
                    # Case where the values are on a newline after the key
                    nums = numeric_matcher.findall(l)
                    stream[key] += map(float, nums)

    parse(keywords)
    if ell:
        parse(ell)
    return json.dumps(stream)

@singledispatch
def read_ipf(arg): # pragma: no cover
    return str(arg)

@read_ipf.register(str)
def read_ipf_str(input_data):
    """
    Read a socet ipf file into a pandas data frame

    Parameters
    ----------
    input_data : str
                 path to the an input data file

    Returns
    -------
    df : pd.DataFrame
         containing the ipf data with appropriate column names and indices
    """
    # Check that the number of rows is matching the expected number
    with open(input_data, 'r') as f:
        for i, l in enumerate(f):
            if i == 1:
                cnt = int(l)
            elif i == 2:
                col = l
                break

    columns = np.genfromtxt(input_data, skip_header=2, dtype='unicode',
                            max_rows = 1, delimiter = ',')

    # TODO: Add unicode conversion
    d = [line.split() for line in open(input_data, 'r')]
    d = np.hstack(np.array(d[3:]))

    d = d.reshape(-1, 12)

    df = pd.DataFrame(d, columns=columns)
    file = os.path.split(os.path.splitext(input_data)[0])[1]
    df['ipf_file'] = pd.Series(np.full((len(df['pt_id'])), file), index = df.index)

    assert int(cnt) == len(df), 'Dataframe length {} does not match point length {}.'.format(int(cnt), len(df))

    # Soft conversion of numeric types to numerics, allows str in first col for point_id
    df = df.apply(pd.to_numeric, errors='ignore')

    return df

@read_ipf.register(list)
def read_ipf_list(input_data_list):
    """
    Read a socet ipf file into a pandas data frame

    Parameters
    ----------
    input_data_list : list
                 list of paths to the a set of input data files

    Returns
    -------
    df : pd.DataFrame
         containing the ipf data with appropriate column names and indices
    """
    frames = []

    for input_file in input_data_list:
        frames.append(read_ipf(input_file))

    df = pd.concat(frames)

    return df

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
         containing the gpf data with appropriate column names and indices
    """

    # Check that the number of rows is matching the expected number
    with open(input_data, 'r') as f:
        for i, l in enumerate(f):
            if i == 1:
                cnt = int(l)
            elif i == 2:
                col = l
                break

    default_columns = np.genfromtxt(input_data, skip_header=2, dtype='unicode',
                                    max_rows = 1, delimiter = ',')

    columns = []

    for column in default_columns:

        if '(' in column and ')' in column:
            column_name ,suffix = column.split('(')
            num = int(suffix.split(')')[0])

            for column_num in range(int(num)):
                new_column = '{}{}'.format(column_name, column_num)
                columns.append(new_column);

        else:
            columns.append(column)

    # Mixed types requires read as unicode - let pandas soft convert
    d = np.genfromtxt(input_data, skip_header=3, dtype='unicode')
    d = d.reshape(-1, 12)

    df = pd.DataFrame(d, columns=columns)

    # Soft conversion of numeric types to numerics, allows str in first col for point_id
    df = df.apply(pd.to_numeric, errors='ignore')

    # Validate the read data with the header point count
    assert int(cnt) == len(df), 'Dataframe length {} does not match point length {}.'.format(int(cnt), len(df))

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
        print('Unable to open output gpf file: {0}'.format(output_file))
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
        outGPF.write('{0}         {1}         {2}\n'.format(row['lat_Y_North'], row['long_X_East'], row['ht']))
        outGPF.write('{0} {1} {2}\n'.format(row['sig0'], row['sig1'], row['sig2']))
        outGPF.write('{0} {1} {2}\n\n'.format(row['res0'], row['res1'], row['res2']))

    outGPF.close()
    return
