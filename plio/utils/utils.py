from functools import reduce
import shutil
import tempfile
import os
import fnmatch
import shutil
import tempfile
import pandas as pd


def create_dir(basedir=''):
    """
    Create a unique, temporary directory in /tmp where processing will occur

    Parameters
    ----------
    basedir : str
              The PATH to create the temporary directory in.
    """
    return tempfile.mkdtemp(dir=basedir)

def check_file_exists(fpath):
    #Ensure that the file exists at the PATH specified
    if os.path.isfile(fpath) == False:
        error_msg = "Unable to find file: {}\n".format(fpath)
        try:
            logging.error(error_msg)
        except:
            print(error_msg)
        return
    return True

def delete_dir(dir):
    """
    Delete a directory

    Parameters
    ----------
    dir : str
          Remove a directory
    """
    shutil.rmtree(dir)


def file_to_list(file):
    with open(file, 'r') as f:
        file_list = f.readlines()
        file_list = map(str.rstrip, file_list)
        file_list = filter(None, file_list)

    return list(file_list)


def create_dir(basedir=''):
    """
    Create a unique, temporary directory in /tmp where processing will occur

    Parameters
    ----------
    basedir : str
              The PATH to create the temporary directory in.
    """
    return tempfile.mkdtemp(dir=basedir)


def delete_dir(dir):
    """
    Delete a directory

    Parameters
    ----------
    dir : str
          Remove a directory
    """
    shutil.rmtree(dir)


def file_search(searchdir,searchstring):
    """
    Recursively search for files in the specified directory

    Parameters
    ----------
    searchdir : str
                The directory to be searched

    searchstring : str
                   The string to be searched for

    Returns
    -------
    filelist : list
               of files
    """

    filelist = []
    for root, dirnames, filenames in os.walk(searchdir):
        for filename in fnmatch.filter(filenames, searchstring):
            filelist.append(os.path.join(root, filename))

    return filelist


def find_in_dict(obj, key):
    """
    Recursively find an entry in a dictionary

    Parameters
    ----------
    obj : dict
          The dictionary to search
    key : str
          The key to find in the dictionary

    Returns
    -------
    item : obj
           The value from the dictionary
    """
    if key in obj:
        return obj[key]
    for k, v in obj.items():
        if isinstance(v,dict):
            item = find_in_dict(v, key)
            if item is not None:
                return item


def find_nested_in_dict(data, key_list):
    """
    Traverse a list of keys into a dict.

    Parameters
    ----------
    data : dict
           The dictionary to be traversed
    key_list: list
              The list of keys to be travered.  Keys are
              traversed in the order they are entered in
              the list

    Returns
    -------
    value : object
            The value in the dict
    """
    return reduce(lambda d, k: d[k], key_list, data)


def xstr(s):
    """
    Return an empty string if the input is a NoneType.  Otherwise
    cast to string and return

    Parameters
    ----------
    s : obj
        An input object castable to a string

    Returns
    -------
     : str
       The input object cast to a string
    """
    if s is None:
        return ''
    return str(s)

def lookup(df,lookupfile=None,lookupdf=None,sep=',',skiprows=1,left_on='sclock',right_on='Spacecraft Clock'):
#TODO: automatically determine the number of rows to skip to handle ccam internal master list and PDS "official" master list formats
    if lookupfile is not None:
        # this loop concatenates together multiple lookup files if provided
        # (mostly to handle the three different master lists for chemcam)
        for x in lookupfile:
            try:
                tmp = pd.read_csv(x, sep=sep, skiprows=skiprows, error_bad_lines=False)
                lookupdf = pd.concat([lookupdf, tmp])
            except:
                lookupdf = pd.read_csv(x, sep=sep, skiprows=skiprows, error_bad_lines=False)
    metadata = df['meta']

    metadata = metadata.merge(lookupdf, left_on=left_on, right_on=right_on, how='left')

    # remove metadata columns that already exist in the data frame to avoid non-unique columns
    meta_cols = set(metadata.columns.values)
    meta_cols_keep = list(meta_cols - set(df['meta'].columns.values))
    metadata = metadata[meta_cols_keep]

    # make metadata into a multiindex
    metadata.columns = [['meta'] * len(metadata.columns), metadata.columns.values]
    # give it the same indices as the df
    metadata.index = df.index
    # combine the df and the new metadata
    df = pd.concat([metadata, df], axis=1)
    return df
