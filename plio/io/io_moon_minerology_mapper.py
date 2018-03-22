import numpy as np
from .io_gdal import GeoDataset


def open(input_data):
    if input_data.split('.')[-1] == 'hdr':
        # GDAL wants the img, but many users aim at the .hdr
        input_data = input_data.split('.')[0] + '.img'
    ds = GeoDataSet(input_data)
    ref_array = ds.read_array()
    metadata = ds.metadata
    wv_array = metadatatoband(metadata)
    return wv_array, ref_array, ds

def metadatatoband(metadata):
    wv2band = []
    for k, v in metadata.items():
        try:
            wv2band.append(float(v))
        except:
            v = v.split(" ")[-1].split("(")[1].split(")")[0]
            wv2band.append(float(v))
    wv2band.sort(key=int)
    return np.asarray(wv2band)
