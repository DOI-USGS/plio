import datetime
import json
from unittest import mock

import pytest
import pvl

from plio.camera import csm
from plio.examples import get_path

def mock_requests_post(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    if 'mars_reconnaissance_orbiter' in args[0]:
        with open(get_path('ctx.response'), 'r') as f:
            resp = json.load(f)
        return MockResponse(resp, 200)

    return MockResponse(None, 404)


@pytest.fixture
def header():
    return pvl.load(get_path('ctx.pvl'))

@pytest.fixture
def req_obj():
    return 

def test_data_from_cube(header):
    if csm.camera_support:
        data = csm.data_from_cube(header)
        assert data['START_TIME'] == datetime.datetime(2008, 9, 17, 5, 8, 10, 820000)

@mock.patch('requests.post', side_effect=mock_requests_post)
def test_create_camera(header):
    if csm.camera_support:
        #import usgscam
        cam = csm.create_camera(header)
        assert isinstance(cam, usgscam.genericls.SensorModel)