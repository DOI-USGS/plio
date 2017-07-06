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

def is_clockwise(vertices):
    """
    Returns whether a list of points describing a polygon are clockwise or counterclockwise.
    is_clockwise(Point list) -> bool
    Parameters
    ----------
    vertices : a list of points that form a single ring
    Examples
    --------
    >>> is_clockwise([Point((0, 0)), Point((10, 0)), Point((0, 10))])
    False
    >>> is_clockwise([Point((0, 0)), Point((0, 10)), Point((10, 0))])
    True
    >>> v = [(-106.57798, 35.174143999999998), (-106.583412, 35.174141999999996), (-106.58417999999999, 35.174143000000001), (-106.58377999999999, 35.175542999999998), (-106.58287999999999, 35.180543), (-106.58263099999999, 35.181455), (-106.58257999999999, 35.181643000000001), (-106.58198299999999, 35.184615000000001), (-106.58148, 35.187242999999995), (-106.58127999999999, 35.188243), (-106.58138, 35.188243), (-106.58108, 35.189442999999997), (-106.58104, 35.189644000000001), (-106.58028, 35.193442999999995), (-106.580029, 35.194541000000001), (-106.57974399999999, 35.195785999999998), (-106.579475, 35.196961999999999), (-106.57922699999999, 35.198042999999998), (-106.578397, 35.201665999999996), (-106.57827999999999, 35.201642999999997), (-106.57737999999999, 35.201642999999997), (-106.57697999999999, 35.201543000000001), (-106.56436599999999, 35.200311999999997), (-106.56058, 35.199942999999998), (-106.56048, 35.197342999999996), (-106.56048, 35.195842999999996), (-106.56048, 35.194342999999996), (-106.56048, 35.193142999999999), (-106.56048, 35.191873999999999), (-106.56048, 35.191742999999995), (-106.56048, 35.190242999999995), (-106.56037999999999, 35.188642999999999), (-106.56037999999999, 35.187242999999995), (-106.56037999999999, 35.186842999999996), (-106.56037999999999, 35.186552999999996), (-106.56037999999999, 35.185842999999998), (-106.56037999999999, 35.184443000000002), (-106.56037999999999, 35.182943000000002), (-106.56037999999999, 35.181342999999998), (-106.56037999999999, 35.180433000000001), (-106.56037999999999, 35.179943000000002), (-106.56037999999999, 35.178542999999998), (-106.56037999999999, 35.177790999999999), (-106.56037999999999, 35.177143999999998), (-106.56037999999999, 35.175643999999998), (-106.56037999999999, 35.174444000000001), (-106.56037999999999, 35.174043999999995), (-106.560526, 35.174043999999995), (-106.56478, 35.174043999999995), (-106.56627999999999, 35.174143999999998), (-106.566541, 35.174144999999996), (-106.569023, 35.174157000000001), (-106.56917199999999, 35.174157999999998), (-106.56938, 35.174143999999998), (-106.57061499999999, 35.174143999999998), (-106.57097999999999, 35.174143999999998), (-106.57679999999999, 35.174143999999998), (-106.57798, 35.174143999999998)]
    >>> is_clockwise(v)
    True
    """
    if len(vertices) < 3:
        return True
    area = 0.0
    ax, ay = vertices[0]
    for bx, by in vertices[1:]:
        area += ax * by - ay * bx
        ax, ay = bx, by
    bx, by = vertices[0]
    area += ax * by - ay * bx
    return area < 0.0
