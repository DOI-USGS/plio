import pyproj
from plio.utils.proj import parse_radii_from_proj

def add_latlon_to_network(network, crs):
    """
    Adds a 'lat' and 'lon' columns to a control network data frame. This
    function modifies the dataframe in place.
    
    Parameters
    ----------
    network : pd.DataFrame
            A pandas dataframe with 'adjustedX', 'adjustedY', and 'adjustedZ' columns
    
    semimajor_axis : float
                    The semimajor axis of the ellipsoid for the body. Defaults to 3396190 (Mars).
    
    semiminor_axis : float
                    The semiminor axis of the ellipsoid for the body. Defaults to 3396190 (Mars).
    """
    semimajor_axis, semiminor_axis = parse_radii_from_proj(crs)
    proj_str = f"""
        +proj=pipeline
        +step +proj=cart +a={semimajor_axis} +b={semiminor_axis} +inv
    """
    geocent2latlon = pyproj.transformer.Transformer.from_pipeline(proj_str)
    lon, lat, _ = geocent2latlon.transform(network['adjustedX'],
                                        network['adjustedY'],
                                        network['adjustedZ'],
                                        errcheck=True)
    network.loc[:, 'lon'] = lon
    network.loc[:, 'lat'] = lat