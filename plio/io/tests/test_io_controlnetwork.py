import os
import sys
import unittest
from time import strftime, gmtime

import pandas as pd
import pvl

from plio.io import io_controlnetwork
from plio.io import ControlNetFileV0002_pb2 as cnf
from plio.utils.utils import find_in_dict

from plio.examples import get_path

import pytest

sys.path.insert(0, os.path.abspath('..'))

@pytest.mark.parametrize('cnet_file',
                         (get_path('apollo_out.net'), get_path('apollo_out_v5.net'))
)
def test_cnet_read(cnet_file):
    df = io_controlnetwork.from_isis(cnet_file)
    assert len(df) == find_in_dict(df.header, 'NumberOfMeasures')
    assert isinstance(df, io_controlnetwork.IsisControlNetwork)
    assert len(df.groupby('id')) == find_in_dict(df.header, 'NumberOfPoints')
    for proto_field, mangled_field in io_controlnetwork.IsisStore.point_field_map.items():
        assert proto_field not in df.columns
        assert mangled_field in df.columns
    for proto_field, mangled_field in io_controlnetwork.IsisStore.measure_field_map.items():
        assert proto_field not in df.columns
        assert mangled_field in df.columns

class TestWriteIsisControlNetwork(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.npts = 5
        serial_times = {295: '1971-07-31T01:24:11.754',
                        296: '1971-07-31T01:24:36.970'}
        cls.serials = {i:'APOLLO15/METRIC/{}'.format(j) for i, j in enumerate(serial_times.values())}
        columns = ['id', 'pointType', 'serialnumber', 'measureType', 'sample', 'line', 'image_index', 'pointLog', 'measureLog']

        data = []
        for i in range(cls.npts):
            data.append((i, 2, cls.serials[0], 2, 0, 0, 0, [], []))
            data.append((i, 2, cls.serials[1], 2, 0, 0, 1, [], []))

        df = pd.DataFrame(data, columns=columns)

        cls.creation_date = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        cls.modified_date = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        io_controlnetwork.to_isis(df, 'test.net', mode='wb', targetname='Moon')

        cls.header_message_size = 78
        cls.point_start_byte = 65614 # 66949

    def test_create_buffer_header(self):
        npts = 5
        serial_times = {295: '1971-07-31T01:24:11.754',
                        296: '1971-07-31T01:24:36.970'}
        serials = {i:'APOLLO15/METRIC/{}'.format(j) for i, j in enumerate(serial_times.values())}
        columns = ['id', 'pointType', 'serialnumber', 'measureType', 'sample', 'line', 'image_index']

        data = []
        for i in range(self.npts):
            data.append((i, 2, serials[0], 2, 0, 0, 0))
            data.append((i, 2, serials[1], 2, 0, 0, 1))

        df = pd.DataFrame(data, columns=columns)

        self.creation_date = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        self.modified_date = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        io_controlnetwork.to_isis(df, 'test.net', mode='wb', targetname='Moon')

        self.header_message_size = 78
        self.point_start_byte = 65614 # 66949

        with open('test.net', 'rb') as f:
            f.seek(io_controlnetwork.HEADERSTARTBYTE)
            raw_header_message = f.read(self.header_message_size)
            header_protocol = cnf.ControlNetFileHeaderV0002()
            header_protocol.ParseFromString(raw_header_message)
            #Non-repeating
            #self.assertEqual('None', header_protocol.networkId)
            self.assertEqual('Moon', header_protocol.targetName)
            self.assertEqual(io_controlnetwork.DEFAULTUSERNAME,
                             header_protocol.userName)
            self.assertEqual(self.creation_date,
                             header_protocol.created)
            self.assertEqual('None', header_protocol.description)
            self.assertEqual(self.modified_date, header_protocol.lastModified)
            #Repeating
            self.assertEqual([135] * self.npts, header_protocol.pointMessageSizes)

    def test_create_point(self):

        with open('test.net', 'rb') as f:
            f.seek(self.point_start_byte)
            for i, length in enumerate([135] * self.npts):
                point_protocol = cnf.ControlPointFileEntryV0002()
                raw_point = f.read(length)
                point_protocol.ParseFromString(raw_point)
                self.assertEqual(str(i), point_protocol.id)
                self.assertEqual(2, point_protocol.type)
                for m in point_protocol.measures:
                    self.assertTrue(m.serialnumber in self.serials.values())
                    self.assertEqual(2, m.type)

    def test_create_pvl_header(self):
        pvl_header = pvl.load('test.net')

        npoints = find_in_dict(pvl_header, 'NumberOfPoints')
        self.assertEqual(5, npoints)

        mpoints = find_in_dict(pvl_header, 'NumberOfMeasures')
        self.assertEqual(10, mpoints)

        points_bytes = find_in_dict(pvl_header, 'PointsBytes')
        self.assertEqual(675, points_bytes)

        points_start_byte = find_in_dict(pvl_header, 'PointsStartByte')
        self.assertEqual(self.point_start_byte, points_start_byte)

    @classmethod
    def tearDownClass(cls):
        os.remove('test.net')
