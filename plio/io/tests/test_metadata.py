import pytest

from plio.io import extract_metadata as em
from plio.io import gdal 

@pytest.fixture
def wkt_moon():
    wktsrs = 'PROJCS["Moon2000_Mercator180",GEOGCS["GCS_Moon_2000",DATUM["D_Moon_2000",SPHEROID["Moon_2000_IAU_IAG",1737400.0,0.0]],PRIMEM["Reference_Meridian",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Mercator"],PARAMETER["False_Easting",0.0],PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",180.0],PARAMETER["Standard_Parallel_1",0.0],UNIT["Meter",1.0]]'
    return em.extract_projstring(wktsrs)

@pytest.fixture
def srs_mars():
    wktsrs = 'PROJCS["Mercator",GEOGCS["GCS_Moon_2000",DATUM["D_Moon_2000",SPHEROID["Moon_2000_IAU_IAG",1737400.0,0.0]],PRIMEM["Reference_Meridian",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Mercator"],PARAMETER["False_Easting",0.0],PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",180.0],PARAMETER["Standard_Parallel_1",0.0],UNIT["Meter",1.0]]'
    return em.extract_projstring(wktsrs)

@pytest.mark.skipif(gdal is None, reason="GDAL not installed")
def test_false_easting(srs_mars):
    e = em.get_false_easting(srs_mars)
    assert e == 0.0

@pytest.mark.skipif(gdal is None, reason="GDAL not installed")
def test_false_northing(srs_mars):
    n = em.get_false_northing(srs_mars)
    assert n == 0.0

@pytest.mark.skipif(gdal is None, reason="GDAL not installed")
def test_projection_name(srs_mars):
    name = em.get_projection_name(srs_mars)
    assert name == 'Mercator_2SP'

@pytest.mark.skipif(gdal is None, reason="GDAL not installed")
def test_axes_extract(srs_mars):
    smajor, sminor, invflattening = em.get_spheroid(srs_mars)
    assert smajor == 1737400.0
    assert sminor == 1737400.0
    assert invflattening == 0.0

@pytest.mark.skipif(gdal is None, reason="GDAL not installed")
def test_get_standard_parallels(srs_mars):
    parallels = em.get_standard_parallels(srs_mars)
    assert parallels[0] == 0.0
    assert parallels[1] == 0.0

@pytest.mark.skipif(gdal is None, reason="GDAL not installed")
def test_get_central_meridian(srs_mars):
    clon = em.get_central_meridian(srs_mars)
    assert clon == 180.0

@pytest.mark.skipif(gdal is None, reason="GDAL not installed")
def test_export_to_proj4(srs_mars):
    """
    Check that proj4 is not supporting Moon2000_Mercator
    """
    proj4 = srs_mars.ExportToProj4()
    for element in '+proj=merc +lon_0=180 +lat_ts=0 +x_0=0 +y_0=0 +R=1737400 +units=m +no_defs'.split():
        assert element in proj4

@pytest.mark.skipif(gdal is None, reason="GDAL not installed")
def test_scale_factor(srs_mars):
    k = em.get_scale_factor(srs_mars)
    assert k == 1.0

@pytest.mark.skipif(gdal is None, reason="GDAL not installed")
def test_latitude_of_origin(srs_mars):
    lo = em.get_latitude_of_origin(srs_mars)
    assert lo == 90.0
