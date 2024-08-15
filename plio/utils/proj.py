import pyproj

def parse_radii_from_proj(crs):
    prj = pyproj.CRS(crs)
    semimajor_axis = prj.ellipsoid.semi_major_metre
    semiminor_axis = prj.ellipsoid.semi_minor_metre
    return semimajor_axis, semiminor_axis