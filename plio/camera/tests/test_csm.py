import datetime
import json
from unittest import mock

import pytest
import pvl

from plio.camera import csm, cam, conditional_cameras
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

@pytest.mark.skipif(cam is None, reason="Cameras not installed")
def test_data_from_cube(header):
    data = csm.data_from_cube(header)
    assert data['START_TIME'] == datetime.datetime(2008, 9, 17, 5, 8, 10, 820000)

@pytest.mark.skipif(cam is None, reason="Cameras not installed")
@mock.patch('requests.post', side_effect=mock_requests_post)
def test_create_camera(header):
    created_camera = csm.create_camera(header)
    assert isinstance(create_camera, cam.genericls.SensorModel)
