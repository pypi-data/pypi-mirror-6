
import unittest

from sqlalchemy import create_engine

from rattail.db import Session
from rattail.db.model import Base


__all__ = ['DataTestCase']


class DataTestCase(unittest.TestCase):

    def setUp(self):
        engine = create_engine('sqlite://')
        Base.metadata.create_all(bind=engine)
        self.session = Session(bind=engine)

    def tearDown(self):
        self.session.close()
