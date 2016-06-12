import os
import plio

__version__ = "0.1.0"



def get_data(filename):
    packagdir = plio.__path__[0]
    dirname = os.path.join(os.path.dirname(packagdir), 'data')
    fullname = os.path.join(dirname, filename)
    return fullname

# Submodule imports
from . import sqlalchemy_json
from . import isis_serial_number
from . import io_controlnetwork
from . import io_gdal
from . import io_json
from . import io_yaml
from . import io_db
from . import io_hdf
from . import utils

