import os.path
from importlib.metadata import PackageNotFoundError, distribution, version

try:
    dist = distribution("plio")
    dist_loc = os.path.normcase(dist.locate_file(""))  # Root location of package
    here = os.path.normcase(__file__)
    if not here.startswith(os.path.join(dist_loc, "plio")):
        raise PackageNotFoundError
    __version__ = version("plio")
except PackageNotFoundError:
    __version__ = "Please install this project with setup.py"

# Submodule imports
from . import data, date, examples, geofuncs, io, utils
