import os
import numpy as np
from .io_gdal import GeoDataset
from .hcube import HCube
import gdal


class Crism(GeoDataset, HCube):
    """
    An M3 specific reader with the spectral mixin.
    """
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