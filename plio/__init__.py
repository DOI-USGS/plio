from pkg_resources import get_distribution, DistributionNotFound
import os.path

try:
    _dist = get_distribution('plio')
    # Normalize case for Windows systems
    dist_loc = os.path.normcase(_dist.location)
    here = os.path.normcase(__file__)
    if not here.startswith(os.path.join(dist_loc, 'plio')):
        # not installed, but there is another version that *is*
        raise DistributionNotFound
    __version__ = _dist.version
except DistributionNotFound:
    __version__ = 'Please install this project with setup.py'

# Submodule imports
from . import io
from . import date
from . import data
from . import examples
from . import geofuncs
from . import utils
