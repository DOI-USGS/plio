import json
import numpy as np

def intersection_to_pixels(inverse_affine, ul, ur, lr, ll):
    """
    Given an inverse affine transformation, take four bounding coordinates
    in lat/lon space and convert them to a minimum bounding rectangle in pixel
    space.

    inverse_affine : object
                     An Affine transformation object

    ul : tuple
         Upper Left coordinate in the form (x,y)

    ur : tuple
         Upper Right coordinate in the form (x,y)

    lr : tuple
         Lower Right coordinate in the form (x,y)

    ll : tuple
         Lower Left coordinate in the form (x,y)
    """
    minx = np.inf
    maxx = -np.inf
    miny = np.inf
    maxy = -np.inf

    for c in [ul, ur, lr, ll]:
        px, py = map(int, inverse_affine * (c[0], c[1]))

        if px < minx:
            minx = px
        if px > maxx:
            maxx = px

        if py < miny:
            miny = py
        if py > maxy:
            maxy = py

    if minx < 0:
        minx = 0
    if miny < 0:
        miny = 0

    return minx, maxx, miny, maxy

def compute_overlap(geodata_a, geodata_b):
    p1 = geodata_a.footprint
    p2 = geodata_b.footprint
    intersection = json.loads(p1.Intersection(p2).ExportToJson())['coordinates'][0]

    ul, ur, lr, ll = find_four_corners(intersection)

    a_intersection = intersection_to_pixels(geodata_a.inverse_affine, ul, ur, lr, ll)
    b_intersection = intersection_to_pixels(geodata_b.inverse_affine, ul, ur, lr, ll)

    return (ul, ur, lr, ll), a_intersection, b_intersection

def estimate_mbr(geodata_a, geodata_b, bufferd=50):
    p1 = geodata_a.footprint
    p2 = geodata_b.footprint
    minx, maxx, miny, maxy = p1.Intersection(p2).GetEnvelope()
    ul = (minx, maxy)
    lr = (maxx, miny)
    a_slice = intersection_to_pixels(geodata_a.latlon_to_pixel,
                                    ul, lr, *geodata_a.xy_extent[1], bufferd)
    b_slice = intersection_to_pixels(geodata_b.latlon_to_pixel,
                                    ul, lr, *geodata_b.xy_extent[1], bufferd)

    return a_slice, b_slice


def find_corners(coords, threshold=120):
    """
    Given a list of coordinates in the form [(x, y), (x1, y1), ..., (xn, yn)],
    attempt to find corners by identifying all angles < the threshold.  For a
    line segment composed of 3 points, the angle between ab and ac is 180 if the
    segments are colinear.  If they are less than threshold, the line segments
    are considered to be a corner.

    Parameters
    ----------
    coords : list
             of coordinates

    threshold : numeric
                Angle under which a corner is identified, Default: 120
    """
    corners = [coords[0]]
    for i, a in enumerate(coords[:-2]):
        a = np.asarray(a)
        b = np.asarray(coords[i+1])
        c = np.asarray(coords[i+2])
        ba = a - b
        bc = c - b
        angle = np.arccos(np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc)))
        if np.degrees(angle) < threshold:
            corners.append(b.tolist())

    return corners

def find_four_corners(coords, threshold=120):
    """
    Find four corners in a polygon by making a call to the find_corners
    function and using the first four corners.

    Parameters
    ----------
    coords: list
            of coordinates

    threshold : numeric
                Anfle under which a corner is identified, Default: 120

    See Also
    --------
    plio.geofuncs.geofuncs.find_corners
    """
    corners = find_corners(coords, threshold)

    corners.sort(key = lambda x:x[1])
    upper = corners[2:]
    lower = corners[:2]


    key = lambda x:x[0]
    ul = min(upper, key=key)
    ur = max(upper, key=key)
    lr = max(lower, key=key)
    ll = min(lower, key=key)

    return ul, ur, lr, ll
