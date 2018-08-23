import importlib
import warnings

cam = importlib.find_loader('usgscam')
cycsm_isd = importlib.find_loader('cycsm.isd')

if cam:
    cam = cam.load_module()

if cycsm_isd:
    cycsm_isd = cycsm_isd.load_module()

def conditional_cameras(func):
    def cam_check(*args, **kwargs):
        if cam:
            return func(*args, **kwargs)
        else:
            warning.warn('Trying to call a camera method, but usgscam is not installed.')
            return None
        return cam_check