import os
import sys
import unittest

import numpy as np

from plio.examples import get_path

sys.path.insert(0, os.path.abspath('..'))

from plio.io import io_gdal


class TestMercator(unittest.TestCase):
    def setUp(self):
        self.dataset = io_gdal.GeoDataset(get_path('Mars_MGS_MOLA_ClrShade_MAP2_0.0N0.0_MERC.tif'))

    def test_geotransform(self):
        self.assertEqual(self.dataset.geotransform, (0.0, 4630.0, 0.0, 3921610.0, 0.0, -4630.0))

    def test_get_unit_type(self):
        # Write a test that has a unit_type or check why this is not 'm'
        self.assertEqual(self.dataset.unit_type, '')

    def test_get_xy_extent(self):
        self.assertEqual(self.dataset.xy_extent, [(0, 0), (2304, 1694)])

    def test_get_no_data_value(self):
        self.assertEqual(self.dataset.no_data_value, 0.0)

    """
    def test_pixel_to_latlon(self):
        lat, lon = self.dataset.pixel_to_latlon(0, 0)
        self.assertAlmostEqual(lat, 55.3322890, 6)
        self.assertAlmostEqual(lon, 0.0, 6)
    """

    def test_scale(self):
        self.assertEqual(self.dataset.scale, ('Meter', 1.0))

    def test_xy_extent(self):
        xy_extent = self.dataset.xy_extent
        self.assertEqual(xy_extent, [(0, 0), (2304, 1694)])

    def test_xy_corners(self):
        xy_corners = self.dataset.xy_corners
        self.assertEqual(xy_corners, [(0, 0), (0, 1694), (2304, 1694), (2304, 0)])

    """
    def test_latlon_extent(self):
        self.assertEqual(self.dataset.latlon_extent, [(55.33228905180849, 0.0),
                                                      (-55.3322890518085, 179.96751473604124)])

    def test_latlon_corners(self):
        self.assertEqual(self.dataset.latlon_corners, [(55.33228905180849, 0.0),
                                                      (-55.3322890518085, 179.96751473604124)])
    """

    def test_spheroid(self):
        sphere = self.dataset.spheroid
        self.assertAlmostEqual(sphere[0], 3396190.0, 6)
        self.assertEqual(self.dataset.spheroid, (3396190.0, 3376200.0, 169.8944472236118))
        self.assertAlmostEqual(sphere[1], 3376200.0, 6)
        self.assertAlmostEqual(sphere[2], 169.8944472236118, 6)

    def test_raster_size(self):
        size = self.dataset.raster_size
        self.assertEqual(size[0], 2304)
        self.assertEqual(size[1], 1694)

    def test_base_name(self):
        self.assertEqual(self.dataset.base_name, 'Mars_MGS_MOLA_ClrShade_MAP2_0.0N0.0_MERC')

    def test_pixel_width(self):
        self.assertAlmostEqual(self.dataset.pixel_width, 4630.0, 6)

    def test_pixel_height(self):
        self.assertAlmostEqual(self.dataset.pixel_height, -4630.0, 6)

    def test_x_rotation(self):
        self.assertAlmostEqual(self.dataset.x_rotation, 0.0, 6)

    def test_y_rotation(self):
        self.assertAlmostEqual(self.dataset.y_rotation, 0.0, 6)

    def test_central_meridian(self):
        self.assertAlmostEqual(self.dataset.central_meridian, 0.0, 6)

    """
    def test_latlon_to_pixel(self):
        self.assertEqual(self.dataset.latlon_to_pixel(0.0, 0.0), (0.0, 846.9999999999999))
    """

    def test_read_array(self):
        arr = self.dataset.read_array()
        self.assertEqual(arr.shape, (1694, 2304))
        self.assertEqual(arr.dtype, np.float32)

    def test_read_array_set_dtype(self):
        arr = self.dataset.read_array(dtype='int8')
        self.assertEqual(arr.dtype, np.int8)
        self.assertAlmostEqual(np.mean(arr), 10.10353227, 6)


class TestLambert(unittest.TestCase):
    def setUp(self):
        self.dataset = io_gdal.GeoDataset(get_path('Lunar_LRO_LOLA_Shade_MAP2_90.0N20.0_LAMB.tif'))

    def test_geotransform(self):
        self.assertEqual(self.dataset.geotransform, (-464400.0, 3870.0, 0.0, -506970.0, 0.0, -3870.0))

    def test_get_unit_type(self):
        #Write a test that has a unit_type or check why this is not 'm'
        self.assertEqual(self.dataset.unit_type, '')

    def test_get_xy_extent(self):
        self.assertEqual(self.dataset.xy_extent, [(0, 0), (239, 275)])

    def test_latlon_extent(self):
        self.assertEqual(self.dataset.latlon_extent, [(-29.721669024636785, 37.834604457982444),
                                                      (69.44231975603968, 69.99086737565507)])
    def test_latlon_corners(self):
        self.assertEqual(self.dataset.latlon_corners, [(-29.721669024636785, 69.99086737565507),
                                                       (-29.721669024636785, 37.834604457982444),
                                                       (69.44231975603968, 37.834604457982444),
                                                       (69.44231975603968, 69.99086737565507)])
    def test_get_no_data_value(self):
        self.assertEqual(self.dataset.no_data_value, 0.0)

    def test_pixel_to_latlon(self):
        lat, lon = self.dataset.pixel_to_latlon(0,0)
        self.assertAlmostEqual(lat, 69.9034915, 6)
        self.assertAlmostEqual(lon, -29.72166902, 6)

    def test_latlon_to_pixel(self):
        lat, lon = 69.90349154912009, -29.72166902463681
        pixel = self.dataset.latlon_to_pixel(lat, lon)
        self.assertAlmostEqual(pixel[0], 0.0, 6)
        self.assertAlmostEqual(pixel[1], 0.0, 6)

    def test_standard_parallels(self):
        sp = self.dataset.standard_parallels
        self.assertEqual(sp, [73.0, 42.0])


class TestPolar(unittest.TestCase):
    def setUp(self):
        self.dataset = io_gdal.GeoDataset(get_path('Mars_MGS_MOLA_ClrShade_MAP2_90.0N0.0_POLA.tif'))

    def test_geotransform(self):
        self.assertEqual(self.dataset.geotransform, (-2129800.0, 4630.0, 0.0, 2129800.0, 0.0, -4630.0))

    def test_get_unit_type(self):
        #Write a test that has a unit_type or check why this is not 'm'
        self.assertEqual(self.dataset.unit_type, '')

    def test_get_xy_extent(self):
        self.assertEqual(self.dataset.xy_extent, [(0, 0), (920, 920)])

    def test_get_no_data_value(self):
        self.assertEqual(self.dataset.no_data_value, 0.0)

    def test_pixel_to_latlon(self):
        lat, lon = self.dataset.pixel_to_latlon(0,0)
        self.assertAlmostEqual(lat, 42.2574735, 6)
        self.assertAlmostEqual(lon, -135.0, 6)

    def test_latlon_to_pixel(self):
        lat, lon = 42.2574735013, -135.0
        pixel = self.dataset.latlon_to_pixel(lat, lon)
        self.assertAlmostEqual(pixel[0], 0.0, 6)
        self.assertAlmostEqual(pixel[1], 0.0, 6)

class TestWriter(unittest.TestCase):
    def setUp(self):
        self.arr = np.random.random((100,100))
        self.ndarr = np.random.random((100,100,3))

    def test_write_array(self):
        io_gdal.array_to_raster(self.arr, 'test.tif')
        self.assertTrue(os.path.exists('test.tif'))
        os.remove('test.tif')

    def test_write_ndarray(self):
        io_gdal.array_to_raster(self.arr, 'test.tif')
        self.assertTrue(os.path.exists('test.tif'))
        os.remove('test.tif')

    def test_with_geotrasform(self):
        gt =  (-464400.0, 3870.0, 0.0, -506970.0, 0.0, -3870.0)
        io_gdal.array_to_raster(self.arr, 'test.tif', geotransform=gt)
        dataset = io_gdal.GeoDataset('test.tif')
        self.assertEqual(gt, dataset.geotransform)

    def test_with_no_data_value_nd(self):
        no_data_value = 0.0
        io_gdal.array_to_raster(self.ndarr, 'test.tif', ndv=no_data_value)
        dataset = io_gdal.GeoDataset('test.tif')
        self.assertEqual(dataset.no_data_value, no_data_value)

    def test_with_no_data_value(self):
        no_data_value = 0.0
        io_gdal.array_to_raster(self.arr, 'test.tif', ndv=no_data_value)
        dataset = io_gdal.GeoDataset('test.tif')
        self.assertEqual(dataset.no_data_value, no_data_value)

    def test_with_projection(self):
        wktsrs = """PROJCS["Moon2000_Mercator180",
            GEOGCS["GCS_Moon_2000",
                DATUM["Moon_2000",
                    SPHEROID["Moon_2000_IAU_IAG",1737400.0,0.0]],
                PRIMEM["Reference_Meridian",0.0],
                UNIT["Degree",0.017453292519943295]],
            PROJECTION["Mercator_1SP"],
            PARAMETER["False_Easting",0.0],
            PARAMETER["False_Northing",0.0],
            PARAMETER["Central_Meridian",180.0],
            PARAMETER["latitude_of_origin",0.0],
            UNIT["Meter",1.0]]"""
        io_gdal.array_to_raster(self.arr, 'test.tif', projection=wktsrs)
        expected_srs = """PROJCS["Moon2000_Mercator180",
            GEOGCS["GCS_Moon_2000",
                DATUM["Moon_2000",
                    SPHEROID["Moon_2000_IAU_IAG",1737400,0]],
                PRIMEM["Reference_Meridian",0],
                UNIT["Degree",0.017453292519943295]],
            PROJECTION["Mercator_2SP"],
            PARAMETER["central_meridian",180],
            PARAMETER["false_easting",0],
            PARAMETER["false_northing",0],
            PARAMETER["standard_parallel_1",0],
            UNIT["Meter",1]]"""
        dataset = io_gdal.GeoDataset('test.tif')
        test_srs = dataset.spatial_reference.__str__()
        self.assertEqual(test_srs.split(), expected_srs.split())

    def tearDown(self):
        try:
            os.remove('test.tif')
        except:
            pass

class TestWithoutGdal(unittest.TestCase):
    def test_without_gdal(self):
        io_gdal.has_gdal = False
        with self.assertRaises(ImportError):
            io_gdal.GeoDataset('foo')

    def tearDown(self):
        io_gdal.has_gdal = True
