import numpy as np

def intersection_to_pixels(latlon_to_pixel, ul, lr, xmax, ymax, buffer=300):
    """

    """
    x_start, y_start = latlon_to_pixel(ul[1], ul[0])
    x_stop, y_stop = latlon_to_pixel(lr[1], lr[0])

    if x_start > x_stop:
        x_start, x_stop = x_stop, x_start
    if y_start > y_stop:
        y_start, y_stop = y_stop, y_start

    if x_start < buffer:
        x_start = 0
    if xmax - x_stop < buffer:
        x_stop = xmax

    if y_start < buffer:
        y_start = 0
    if ymax - y_stop < buffer:
        y_stop = ymax
    return np.s_[y_start:y_stop, x_start:x_stop]

def estimate_mbr(geodata_a, geodata_b):
    p1 = geodata_a.footprint
    p2 = geodata_b.footprint
    minx, maxx, miny, maxy = p1.Intersection(p2).GetEnvelope()
    ul = (minx, maxy)
    lr = (maxx, miny)

    a_slice = intersection_to_pixels(geodata_a.latlon_to_pixel,
                                    ul, lr, *geodata_a.xy_extent[1])
    b_slice = intersection_to_pixels(geodata_b.latlon_to_pixel,
                                    ul, lr, *geodata_b.xy_extent[1])

    return a_slice, b_slice                                
