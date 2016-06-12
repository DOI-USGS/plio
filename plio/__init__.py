import os
import plio

__version__ = "0.1.0"



def get_data(filename):
    packagdir = plio.__path__[0]
    dirname = os.path.join(os.path.dirname(packagdir), 'data')
    fullname = os.path.join(dirname, filename)
    return fullname

# Submodule imports
from plio import sqlalchemy_json
from plio import isis_serial_number
from plio import io_controlnetwork
from plio import io_gdal
from plio import utils
