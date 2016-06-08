import os
import sys
import unittest
import numpy as np
import pandas as pd
import pvl

from .. import io_controlnetwork
from .. import ControlNetFileV0002_pb2 as cnf

from plio.utils import find_in_dict

sys.path.insert(0, os.path.abspath('..'))


class TestWriteIsisControlNetwork(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        cls.npts = 5
        serial_times = {295: '1971-07-31T01:24:11.754',
                        296: '1971-07-31T01:24:36.970'}
        cls.serials = ['APOLLO15/METRIC/{}'.format(i) for i in serial_times.values()]
        net = CandidateGraph({'a': ['b'], 'b': ['a']})
        for i, n in net.nodes_iter(data=True):
            n._keypoints = pd.DataFrame(np.arange(10).reshape(cls.npts,-1), columns=['x', 'y'])
            n._isis_serial = cls.serials[i]

        source = np.zeros(cls.npts)
        destination = np.ones(cls.npts)
        pid = np.arange(cls.npts)

        matches = pd.DataFrame(np.vstack((source, pid, destination, pid)).T, columns=['source_image',
                                                                                      'source_idx',
                                                                                      'destination_image',
                                                                                      'destination_idx'])

        net.edge[0][1].matches = matches
        net.generate_cnet(clean_keys=[])

        cls.creation_date = net.creationdate
        cls.modified_date = net.modifieddate
        io_controlnetwork.to_isis('test.net', net, mode='wb', targetname='Moon')

        cls.header_message_size = 98
        cls.point_start_byte = 65634

    def test_create_buffer_header(self):
        with open('test.net', 'rb') as f:
            f.seek(io_controlnetwork.HEADERSTARTBYTE)
            raw_header_message = f.read(self.header_message_size)
            header_protocol = cnf.ControlNetFileHeaderV0002()
            header_protocol.ParseFromString(raw_header_message)

            #Non-repeating
            self.assertEqual('None', header_protocol.networkId)
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

            with open('test.net', 'rb') as f:
                f.seek(self.point_start_byte)
                for i, length in enumerate([135] * self.npts):
                    point_protocol = cnf.ControlPointFileEntryV0002()
                    raw_point = f.read(length)
                    point_protocol.ParseFromString(raw_point)
                    self.assertEqual(str(i), point_protocol.id)
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
        self.assertEqual(675, points_bytes)

        points_start_byte = find_in_dict(pvl_header, 'PointsStartByte')
        self.assertEqual(65634, points_start_byte)

    @classmethod
    def tearDownClass(cls):
        os.remove('test.net')
