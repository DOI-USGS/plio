import os
import sys
import unittest
from time import strftime, gmtime

import networkx as nx
import pandas as pd
import pvl

from .. import io_controlnetwork
from .. import ControlNetFileV0002_pb2 as cnf
from plio.utils.utils import find_in_dict

sys.path.insert(0, os.path.abspath('..'))


class TestWriteIsisControlNetwork(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.npts = 5
        serial_times = {295: '1971-07-31T01:24:11.754',
                        296: '1971-07-31T01:24:36.970'}
        cls.serials = ['APOLLO15/METRIC/{}'.format(i) for i in serial_times.values()]
        columns = ['point_id', 'point_type', 'serialnumber', 'measure_type', 'x', 'y', 'node_id']

        G = nx.Graph()
        G.add_node(0, node_type='image')
        G.add_node(1, node_type='image')
        G.add_edge(0,1)
        G.point_nodes = []
        for i in range(cls.npts):
            i += 1
            G.point_nodes.append(i*100)
            G.add_node(i * 100, node_type='point', pointid = i * 100, subpixel=False)
            G.add_edge(i*100, 0)
            G.add_edge(i*100, 1)
            # Add a single correspondence
            G.add_node(i * 1000, x=i*.5, y=i*.5, id=i*1000, node_type='correspondence', measure_type=2, serialnumber=cls.serials[0])
            G.add_edge(i*1000, i*100)
            # Add a second correspondence
            G.add_node(i * 2000, x=i*.5, y=i*.5, id=i*2000, node_type='correspondence', measure_type=2, serialnumber=cls.serials[1])
            G.add_edge(i * 2000, i*100)


        cls.creation_date = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        cls.modified_date = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        io_controlnetwork.to_isis('test.net', [G], mode='wb', targetname='Moon')

        cls.header_message_size = 78
        cls.point_start_byte = 65614 # 66949

    def test_create_buffer_header(self):
        self.header_message_size = 78
        self.point_start_byte = 66104 # 66949

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
            self.assertEqual([137] * self.npts, header_protocol.pointMessageSizes)

    def test_create_point(self):
        with open('test.net', 'rb') as f:
            f.seek(self.point_start_byte)
            for i, length in enumerate(5*[137]):
                point_protocol = cnf.ControlPointFileEntryV0002()
                raw_point = f.read(length)
                point_protocol.ParseFromString(raw_point)
                self.assertEqual(str((i + 1) * 100), point_protocol.id)
                self.assertEqual(2, point_protocol.type)
                for m in point_protocol.measures:
                    self.assertTrue(m.serialnumber in self.serials)
                    self.assertEqual(2, m.type)

    def test_create_pvl_header(self):
        pvl_header = pvl.load('test.net')

        npoints = find_in_dict(pvl_header, 'NumberOfPoints')
        self.assertEqual(5, npoints)

        mpoints = find_in_dict(pvl_header, 'NumberOfMeasures')
        self.assertEqual(10, mpoints)

        points_bytes = find_in_dict(pvl_header, 'PointsBytes')
        self.assertEqual(685, points_bytes)

        points_start_byte = find_in_dict(pvl_header, 'PointsStartByte')
        self.assertEqual(self.point_start_byte, points_start_byte)

    @classmethod
    def tearDownClass(cls):
        #os.remove('test.net')
        pass
