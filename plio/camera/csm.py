import datetime
import json

try:
    import usgscam as cam
    from cycsm.isd import Isd
    camera_support = True
except:
    camera_support = False
import requests

from plio.utils.utils import find_in_dict
from plio.io.io_json import NumpyEncoder


def data_from_cube(header):
    data = {}
    data['START_TIME'] = find_in_dict(header, 'StartTime')
    data['SPACECRAFT_NAME'] = find_in_dict(header, 'SpacecraftName')
    data['INSTRUMENT_NAME'] = find_in_dict(header, 'InstrumentId')
    data['SAMPLING_FACTOR'] = find_in_dict(header, 'SpatialSumming')
    data['SAMPLE_FIRST_PIXEL'] = find_in_dict(header, 'SampleFirstPixel')
    data['IMAGE'] = {}
    data['IMAGE']['LINES'] = find_in_dict(header, 'Lines')
    data['IMAGE']['SAMPLES'] = find_in_dict(header, 'Samples')
    data['TARGET_NAME'] = find_in_dict(header, 'TargetName')
    data['LINE_EXPOSURE_DURATION'] = find_in_dict(header, 'LineExposureDuration')
    data['SPACECRAFT_CLOCK_START_COUNT'] = find_in_dict(header, 'SpacecraftClockCount')
    return data

def create_camera(obj, url='http://smalls:8002/api/1.0/missions/mars_reconnaissance_orbiter/csm_isd'):
    if not camera_support:
        print("Usgscam library not installed. Camera capabilities are disabled")
    
    data = json.dumps(data_from_cube(obj.metadata), cls=NumpyEncoder)
    r = requests.post(url, data=data)

    # Get the ISD back and instantiate a local ISD for the image
    isd = r.json()['data']['isd']
    i = Isd.loads(isd)

    # Create the plugin and camera as usual
    plugin = cam.genericls.Plugin()
    return plugin.from_isd(i, plugin.modelname(0))