import os
import numpy as np
from .io_gdal import GeoDataset
from .hcube import HCube
import gdal


class M3(GeoDataset, HCube):
    """
    An M3 specific reader with the spectral mixin.
    """
    @property
    def wavelengths(self):
        if not hasattr(self, '_wavelengths'):
            try:
                info = gdal.Info(self.file_name, format='json')
                wavelengths = [float(j) for i, j in sorted(info['metadata'][''].items(),
                                 key=lambda x: float(x[0].split('_')[-1]))]
                self._original_wavelengths = wavelengths
                self._wavelengths = np.round(wavelengths, self.tolerance)
            except:
                self._wavelengths = []
        return self._wavelengths

def open(input_data):
    if os.path.splitext(input_data)[-1] == 'hdr':
        # GDAL wants the img, but many users aim at the .hdr
        input_data = os.path.splitext(input_data)[:-1] + '.img'
    ds = M3(input_data)

    return ds
