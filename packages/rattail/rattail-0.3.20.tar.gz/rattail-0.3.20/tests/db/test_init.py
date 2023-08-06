
from unittest import TestCase

from mock import patch

from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Engine

from edbob.configuration import AppConfigParser

from rattail import db


class TestConfigureSessionFactory(TestCase):

    def setUp(self):
        self.config = AppConfigParser('rattail')
        self.config.add_section('edbob.db')
        self.config.add_section('rattail.db')
        self.Session = sessionmaker()

    def test_session_is_not_bound_if_no_engine_is_defined_by_config(self):
        db.configure_session_factory(self.config, self.Session)
        session = self.Session()
        self.assertTrue(session.bind is None)
        session.close()

    def test_session_is_correctly_bound_if_engine_is_defined_by_config(self):
        self.config.set('edbob.db', 'sqlalchemy.url', 'sqlite:////a/very/custom/db')
        session = self.Session()
        self.assertTrue(session.bind is None)
        session.close()
        db.configure_session_factory(self.config, self.Session)
        session = self.Session()
        self.assertTrue(isinstance(session.bind, Engine))
        self.assertEqual(str(session.bind.url), 'sqlite:////a/very/custom/db')
        session.close()

    def test_global_session_is_configured_by_default(self):
        self.config.set('edbob.db', 'sqlalchemy.url', 'sqlite:////path/to/rattail.sqlite')
        session = db.Session()
        self.assertTrue(session.bind is None)
        session.close()
        db.configure_session_factory(self.config)
        session = db.Session()
        self.assertTrue(isinstance(session.bind, Engine))
        self.assertEqual(str(session.bind.url), 'sqlite:////path/to/rattail.sqlite')
        session.close()
        # Must undo that configuration, this thing is global.
        db.Session.configure(bind=None)

    @patch('rattail.db.changes.record_changes')
    def test_changes_will_not_be_recorded_by_default(self, record_changes):
        self.config.set('edbob.db', 'sqlalchemy.url', 'sqlite://')
        db.configure_session_factory(self.config, self.Session)
        self.assertFalse(record_changes.called)

    @patch('rattail.db.changes.record_changes')
    def test_changes_will_be_recorded_by_so_configured(self, record_changes):
        self.config.set('edbob.db', 'sqlalchemy.url', 'sqlite://')
        self.config.set('rattail.db', 'changes.record', 'true')
        db.configure_session_factory(self.config, self.Session)
        # Role changes are ignored by default.
        record_changes.assert_called_once_with(self.Session, True)

    @patch('rattail.db.changes.record_changes')
    def test_changes_will_still_be_recorded_with_deprecated_config(self, record_changes):
        self.config.set('edbob.db', 'sqlalchemy.url', 'sqlite://')
        self.config.set('rattail.db', 'record_changes', 'true')
        db.configure_session_factory(self.config, self.Session)
        # Role changes are ignored by default.
        record_changes.assert_called_once_with(self.Session, True)

    @patch('rattail.db.changes.record_changes')
    def test_config_determines_if_role_changes_are_ignored(self, record_changes):
        self.config.set('edbob.db', 'sqlalchemy.url', 'sqlite://')
        self.config.set('rattail.db', 'changes.record', 'true')
        self.config.set('rattail.db', 'changes.ignore_roles', 'false')
        db.configure_session_factory(self.config, self.Session)
        # Role changes are ignored by default; False means config works.
        record_changes.assert_called_once_with(self.Session, False)
