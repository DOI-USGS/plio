import numpy as np
from .io_gdal import GeoDataset

def open(input_data):
    ds = GeoDataset(input_data)
    return ds

def getspectra(x, y, ds):
    nbands = ds.RasterCount
    reflectance = np.empty(nbands)
    for b in range(1, nbands + 1):
        reflectance[b - 1] = ds.GetRasterBand(b).ReadAsArray(y, x, 1, 1)

    mergedref = np.empty(nbands - 1)
    mergedref[:4] = reflectance[:4]
    mergedref[4] = (reflectance[4] + reflectance[5]) / 2
    mergedref[5:] = reflectance[6:]
    return mergedref
