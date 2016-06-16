from functools import reduce
import shutil
import tempfile
import os
import fnmatch
import shutil
import tempfile


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