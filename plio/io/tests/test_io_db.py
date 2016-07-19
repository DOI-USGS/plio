import os
import sys
import unittest

from sqlalchemy.orm import session

from plio.data import get_data

sys.path.insert(0, os.path.abspath('..'))

from plio.io import io_db


class TestDataDB(unittest.TestCase):

    def test_setup_session(self):
        print(get_data('data.db'))
        data_session = io_db.setup_db_session(get_data('data.db'))
        self.assertIsInstance(data_session, session.Session)
