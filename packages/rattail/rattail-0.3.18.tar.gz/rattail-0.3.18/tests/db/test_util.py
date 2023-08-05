
from unittest import TestCase

from sqlalchemy.pool import SingletonThreadPool, NullPool

from edbob.configuration import AppConfigParser

from rattail.db import util


class TestEngineConfig(TestCase):

    def test_standard(self):
        config = {
            'sqlalchemy.url': 'sqlite://',
            }
        engine = util.engine_from_config(config)
        self.assertEqual(str(engine.url), 'sqlite://')
        self.assertTrue(isinstance(engine.pool, SingletonThreadPool))

    def test_custom_poolclass(self):
        config = {
            'sqlalchemy.url': 'sqlite://',
            'sqlalchemy.poolclass': 'sqlalchemy.pool:NullPool',
            }
        engine = util.engine_from_config(config)
        self.assertEqual(str(engine.url), 'sqlite://')
        self.assertTrue(isinstance(engine.pool, NullPool))

    def test_get_engines_default(self):
        config = AppConfigParser('rattail')
        config.set('edbob.db', 'sqlalchemy.url', 'sqlite://')
        engines = util.get_engines(config)
        self.assertEqual(len(engines), 1)
        self.assertEqual(str(engines['default'].url), 'sqlite://')

    def test_get_engines_custom(self):
        config = AppConfigParser('rattail')
        config.set('edbob.db', 'keys', 'host, store')
        config.set('edbob.db', 'host.url', 'sqlite:///rattail.host.sqlite')
        config.set('edbob.db', 'store.url', 'sqlite:///rattail.store.sqlite')
        config.set('edbob.db', 'store.poolclass', 'sqlalchemy.pool:SingletonThreadPool')
        engines = util.get_engines(config)
        self.assertEqual(len(engines), 2)
        self.assertEqual(str(engines['host'].url), 'sqlite:///rattail.host.sqlite')
        self.assertTrue(isinstance(engines['host'].pool, NullPool))
        self.assertEqual(str(engines['store'].url), 'sqlite:///rattail.store.sqlite')
        self.assertTrue(isinstance(engines['store'].pool, SingletonThreadPool))

    def test_get_engines_none(self):
        config = AppConfigParser('rattail')
        config.set('edbob.db', 'unknown.url', 'sqlite://')
        engines = util.get_engines(config)
        self.assertEqual(len(engines), 0)
