import os
import sys
import unittest
from time import strftime, gmtime

import pandas as pd
import numpy as np
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

@pytest.mark.parametrize('messagetype, value', [
                         (2, 0.5),
                         (3, 0.5),
                         (4, -0.25),
                         (5, 1e6),
                         (6, 1),
                         (7, -1e10),
                         ('GoodnessOfFit', 0.5),
                         ('MinimumPixelZScore', 0.25)
])
def test_MeasureLog(messagetype, value):
    l = io_controlnetwork.MeasureLog(messagetype, value)
    if isinstance(messagetype, int):
        assert l.messagetype == io_controlnetwork.MeasureMessageType(messagetype)
    elif isinstance(messagetype, str):
        assert l.messagetype == io_controlnetwork.MeasureMessageType[messagetype]
        
    assert l.value == value
    assert isinstance(l.to_protobuf, object)

def test_log_error():
    with pytest.raises(TypeError) as err:
        io_controlnetwork.MeasureLog(2, 'foo')

def test_to_protobuf():
    value = 1.25
    int_dtype = 2
    log = io_controlnetwork.MeasureLog(int_dtype, value)
    proto = log.to_protobuf()
    assert proto.doubleDataType == int_dtype
    assert proto.doubleDataValue == value

@pytest.fixture
def cnet_dataframe(tmpdir):
    npts = 5
    serial_times = {295: '1971-07-31T01:24:11.754',
                    296: '1971-07-31T01:24:36.970'}
    serials = {i:'APOLLO15/METRIC/{}'.format(j) for i, j in enumerate(serial_times.values())}
    columns = ['id', 'pointType', 'serialnumber', 'measureType',
               'sample', 'line', 'image_index', 'pointLog', 'measureLog',
               'aprioriCovar']

    data = []
    for i in range(npts):
        aprioriCovar = None
        if i == npts - 1:
            aprioriCovar = np.ones((2,3))
        data.append((i, 2, serials[0], 2, 0, 0, 0, [], [], aprioriCovar))
        data.append((i, 2, serials[1], 2, 0, 0, 1, [], [io_controlnetwork.MeasureLog(2, 0.5)],aprioriCovar))

    df = pd.DataFrame(data, columns=columns)
    
    df.creation_date = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    df.modified_date = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    io_controlnetwork.to_isis(df, tmpdir.join('test.net'), mode='wb', targetname='Moon')

    df.header_message_size = 78
    df.point_start_byte = 65614 # 66949
    df.npts = npts
    df.measure_size = [149, 149, 149, 149, 200]  # Size of each measure in bytes
    df.serials = serials
    return df 

def test_create_buffer_header(cnet_dataframe, tmpdir):
    with open(tmpdir.join('test.net'), 'rb') as f:
        
        f.seek(io_controlnetwork.HEADERSTARTBYTE)
        raw_header_message = f.read(cnet_dataframe.header_message_size)
        header_protocol = cnf.ControlNetFileHeaderV0002()
        header_protocol.ParseFromString(raw_header_message)
        #Non-repeating
        #self.assertEqual('None', header_protocol.networkId)
        assert 'Moon' == header_protocol.targetName
        assert io_controlnetwork.DEFAULTUSERNAME == header_protocol.userName
        assert cnet_dataframe.creation_date == header_protocol.created
        assert 'None' == header_protocol.description
        assert cnet_dataframe.modified_date == header_protocol.lastModified
        #Repeating
        assert cnet_dataframe.measure_size == header_protocol.pointMessageSizes

def test_create_point(cnet_dataframe, tmpdir):
    with open(tmpdir.join('test.net'), 'rb') as f:
        f.seek(cnet_dataframe.point_start_byte)
        for i, length in enumerate(cnet_dataframe.measure_size):
            point_protocol = cnf.ControlPointFileEntryV0002()
            raw_point = f.read(length)
            point_protocol.ParseFromString(raw_point)
            assert str(i) == point_protocol.id
            assert 2 == point_protocol.type
            if i == cnet_dataframe.npts - 1:
                assert point_protocol.aprioriCovar == [1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
            for j, m in enumerate(point_protocol.measures):
                assert m.serialnumber in cnet_dataframe.serials.values()
                assert 2 == m.type
                assert len(m.log) == j  # Only the second measure has a message

def test_create_point_reference_index(cnet_dataframe, tmpdir):
    print(cnet_dataframe)
    assert False

def test_create_pvl_header(cnet_dataframe, tmpdir):
    with open(tmpdir.join('test.net'), 'rb') as f:
        pvl_header = pvl.load(f)

    npoints = find_in_dict(pvl_header, 'NumberOfPoints')
    assert 5 == npoints

    mpoints = find_in_dict(pvl_header, 'NumberOfMeasures')
    assert 10 == mpoints

    points_bytes = find_in_dict(pvl_header, 'PointsBytes')
    assert 796 == points_bytes

    points_start_byte = find_in_dict(pvl_header, 'PointsStartByte')
    assert cnet_dataframe.point_start_byte == points_start_byte
