import numpy as np
import gdal

from ..utils.indexing import _LocIndexer, _iLocIndexer


class HCube(object):
    """
    A Mixin class for use with the io_gdal.GeoDataset class
    to optionally add support for spectral labels, label
    based indexing, and lazy loading for reads. 
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
    
    @property
    def tolerance(self):
        return getattr(self, '_tolerance', 2)
    
    @tolerance.setter
    def tolerance(self, val):
        if isinstance(val, int):
            self._tolerance = val
            self._reindex()
        else:
            raise TypeError

    def _reindex(self):
        if self._original_wavelengths is not None:
            self._wavelengths = np.round(self._original_wavelengths, decimals=self.tolerance)

    def __getitem__(self, key):
        i = _iLocIndexer(self)
        return i[key]
    
    @property
    def loc(self):
        return _LocIndexer(self)
    
    @property
    def iloc(self):
        return _iLocIndexer(self)
    
    def _read(self, key):
        ifnone = lambda a, b: b if a is None else a

        y = key[1]
        x = key[2]
        if isinstance(x, slice):
            xstart = ifnone(x.start,0)
            xstop = ifnone(x.stop,self.raster_size[0])
            xstep = xstop - xstart
        else:
            raise TypeError("Loc style access elements must be slices, e.g., [:] or [10:100]")
        if isinstance(y, slice):
            ystart = ifnone(y.start, 0)
            ystop = ifnone(y.stop, self.raster_size[1])
            ystep = ystop - ystart
        else:
            raise TypeError("Loc style access elements must be slices, e.g., [:] or [10:100]")
            
        pixels = (xstart, ystart, xstep, ystep)
        if isinstance(key[0], (int, np.integer)):
            return self.read_array(band=int(key[0]+1), pixels=pixels)
        else:
            arrs = []
            for b in key[0]:
                arrs.append(self.read_array(band=int(b+1), pixels=pixels))
        return np.stack(arrs)