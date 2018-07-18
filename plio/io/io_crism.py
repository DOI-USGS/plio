import os
import numpy as np
from .io_gdal import GeoDataset
from .hcube import HCube

try:
    from libpysat.derived import crism
    from libpysat.derived.utils import get_derived_funcs
    libpysat_enabled = True
except:
    print('No libpysat module. Unable to attach derived product functions')
    libpysat_enabled = False

import gdal


class Crism(GeoDataset, HCube):
    """
    An Crism specific reader with the spectral mixin.
    """
    def __init__(self, file_name):

        GeoDataset.__init__(self, file_name)
        HCube.__init__(self)

        self.derived_funcs = {}

        if libpysat_enabled:
            self.derived_funcs = get_derived_funcs(crism)

    def __getattr__(self, name):
        try:
            func = self.derived_funcs[name]

            setattr(self, name, func.__get__(self))
            return getattr(self, name)

        except KeyError as keyerr:
            raise AttributeError("'M3' object has no attribute '{}'".format(name)) from None

    @property
    def wavelengths(self):
        if not hasattr(self, '_wavelengths'):
            try:
                info = gdal.Info(self.file_name, format='json')
                wv = dict((k,v) for (k,v) in info['metadata'][''].items() if 'Band' in k) # Only get the 'Band_###' keys
                wavelengths = [float(j.split(" ")[0]) for i, j in sorted(wv.items(),
                                key=lambda x: int(x[0].split('_')[-1]))]
                self._original_wavelengths = wavelengths
                self._wavelengths = np.round(wavelengths, self.tolerance)
            except:
                self._wavelengths = []
        return self._wavelengths

def open(input_data):
    if os.path.splitext(input_data)[-1] == 'hdr':
        # GDAL wants the img, but many users aim at the .hdr
        input_data = os.path.splitext(input_data)[:-1] + '.img'
    ds = Crism(input_data)

    return ds
