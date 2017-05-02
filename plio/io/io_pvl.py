import pvl
from plio.utils.utils import find_in_dict

def extract_keywords(header, *args):
    """
    For a given header, find all of the keys and return an unnested dict.
    """
    try:
        header = pvl.load(header)
    except:
        header = pvl.loads(header)

    res = {}
    # Iterate through all of the requested keys
    for a in args:
        try:
            res[a] = find_in_dict(a)
        except:
            res[a] = None
    return res
