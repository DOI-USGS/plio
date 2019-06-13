import yaml


def read_yaml(inputfile):
    """
    Read the input yaml file into a python dictionary

    Parameters
    =========
    inputfile : str
                PATH to the file on disk

    Returns
    =======
    ydict : dict
            YAML file parsed to a Python dict
    """
    try:
        with open(inputfile, 'r') as f:
            ydict = yaml.safe_load(f)
    except:  # pragma: no cover
        raise IOError('Unable to load YAML file.')
    return ydict
