import re
import os
import json
from collections import defaultdict
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
    numeric_matcher = re.compile(r'\W?-?(?:0|[1-9]\d*)(?:\.\d*)?(?:[eE][+\-]?\d+)?')
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

    d = [line.split() for line in open(input_data, 'r')]
    d = np.hstack(np.array(d[3:]))

    d = d.reshape(-1, 12).astype('unicode')

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

def save_ipf(df, output_path):
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

    for ipf_file, ipf_df in df.groupby('ipf_file'):

        output_file = os.path.join(output_path, ipf_file + '.ipf')

        # Check that file can be opened
        try:
            outIPF = open(output_file, 'w', newline='\r\n')
        except:
            print('Unable to open output ipf file: {0}'.format(output_file))
            return 1

        #grab number of rows in pandas dataframe ipf group
        numpts = len(ipf_df)

        #Output ipf header
        outIPF.write('IMAGE POINT FILE\n')
        outIPF.write('{0}\n'.format(numpts))
        outIPF.write('pt_id,val,fid_val,no_obs,l.,s.,sig_l,sig_s,res_l,res_s,fid_x,fid_y\n')

        for index, row in ipf_df.iterrows():
            #Output coordinates to ipf file
            outIPF.write('{0} {1} {2} {3}\n'.format(row['pt_id'], row['val'], row['fid_val'], row['no_obs']))
            outIPF.write('{:0.6f}  {:0.6f}\n'.format(row['l.'], row['s.']))
            outIPF.write('{:0.6f}  {:0.6f}\n'.format(row['sig_l'], row['sig_s']))
            outIPF.write('{:0.6f}  {:0.6f}\n'.format(row['res_l'], row['res_s']))
            outIPF.write('{:0.6f}  {:0.6f}\n\n'.format(row['fid_x'], row['fid_y']))

        outIPF.close()
    return

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

def read_atf(atf_file):
    """
    Reads a .atf file and outputs all of the
    .ipf, .gpf, .sup, .prj, and path to locate the
    .apf file (should be the same as all others)

    Parameters
    ----------
    atf_file : str
               Full path to a socet atf file

    Returns
    -------
    files_dict : dict
                 Dict of files and data associated with a socet
                 project
    """
    with open(atf_file) as f:
        # Extensions of files we want
        files_ext = ['.prj', '.sup', '.ipf', '.gpf']
        files_dict = []
        files = defaultdict(list)

        for line in f:
            ext = os.path.splitext(line)[-1].strip()

            # Check is needed for split as all do not have a space
            if ext in files_ext:

                # If it is the .prj file, it strips the directory away and grabs file name
                if ext == '.prj':
                    files[ext].append(line.strip().split(' ')[1].split('\\')[-1])

                # If the ext is in the list of files we care about, it addes to the dict
                files[ext].append(line.strip().split(' ')[-1])

            else:

                # Adds to the dict even if not in files we care about
                files[ext.strip()].append(line)

        # Gets the base filepath
        files['basepath'] = os.path.dirname(os.path.abspath(atf_file))

        # Creates a dict out of file lists for GPF, PRJ, IPF, and ATF
        files_dict = (dict(files_dict))

        # Sets the value of IMAGE_IPF to all IPF images
        files_dict['IMAGE_IPF'] = files['.ipf']

        # Sets the value of IMAGE_SUP to all SUP images
        files_dict['IMAGE_SUP'] = files['.sup']

        # Sets value for GPF file
        files_dict['GP_FILE'] = files['.gpf'][0]

        # Sets value for PRJ file
        files_dict['PROJECT'] = files['.prj'][0]

        # Sets the value of PATH to the path of the ATF file
        files_dict['PATH'] = files['basepath']

        return files_dict
