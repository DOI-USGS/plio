# Conditional imports for GDAL
import importlib
import warnings
import sys

try:
    gdal = importlib.util.find_spec('gdal')
    ogr = importlib.util.find_spec('osgeo.ogr')
    osr = importlib.util.find_spec('osr')

    gdal = gdal.loader.load_module()
    ogr = ogr.loader.load_module()
    osr = osr.loader.load_module()
    gdal.UseExceptions() 
except:
    try:
        gdal = importlib.util.find_spec('osgeo.gdal')
        gdal = gdal.loader.load_module()
    except:
        gdal = None
    ogr = None
    osr = None

def conditional_gdal(func):
    def has_gdal(*args, **kwargs):
        if gdal:
            return func(*args, **kwargs)
        else:
            warnings.warn('Trying to call a GDAL method, but GDAL is not installed.')
        return None
    return has_gdal

from . import io_autocnetgraph
from . import io_controlnetwork
from . import io_db
from . import io_gdal
from . import io_hdf
from . import io_json
from . import io_krc
from . import io_pvl
from . import io_spectral_profiler
from . import io_tes
from . import io_yaml
from . import isis_serial_number
