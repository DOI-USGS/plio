import os
import plio

__version__ = "0.1.0"


def get_data(filename):
    packagdir = plio.__path__[0]
    dirname = os.path.join(os.path.dirname(packagdir), 'data')
    fullname = os.path.join(dirname, filename)
    return fullname
