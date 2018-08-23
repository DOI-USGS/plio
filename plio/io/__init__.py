# Conditional imports for GDAL
import importlib
import warnings

gdal = importlib.find_loader('gdal')
ogr = importlib.find_loader('osgeo.ogr')
osr = importlib.find_loader('osr')

if gdal:
    gdal = gdal.load_module()
    ogr = ogr.load_module()
    osr = osr.load_module()
    gdal.UseExceptions() 

def conditional_gdal(func):
    def has_gdal(*args, **kwargs):
        if gdal:
            return func(*args, **kwargs)
        else:
            warning.warn('Trying to call a GDAL method, but GDAL is not installed.')
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
