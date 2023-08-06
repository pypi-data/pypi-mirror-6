
# TODO: These tests are now broken and need fixing...

# from unittest import TestCase
# from mock import patch, DEFAULT

# from rattail.db.sync import linux


# class SyncDaemonTests(TestCase):

#     @patch.multiple('rattail.db.sync.linux',
#                     edbob=DEFAULT,
#                     get_default_engine=DEFAULT,
#                     get_sync_engines=DEFAULT,
#                     synchronize_changes=DEFAULT)
#     def test_run(self, edbob, get_default_engine, get_sync_engines, synchronize_changes):

#         daemon = linux.SyncDaemon('/tmp/rattail_dbsync.pid')

#         # no remote engines configured
#         get_sync_engines.return_value = None
#         daemon.run()
#         get_sync_engines.assert_called_once_with(edbob.config)
#         self.assertFalse(get_default_engine.called)
#         self.assertFalse(synchronize_changes.called)

#         # with remote engines configured
#         get_sync_engines.return_value = 'fake_remotes'
#         get_default_engine.return_value = 'fake_local'
#         daemon.run()
#         synchronize_changes.assert_called_once_with('fake_local', 'fake_remotes')


# class ModuleTests(TestCase):

#     @patch.multiple('rattail.db.sync.linux', edbob=DEFAULT, SyncDaemon=DEFAULT)
#     def test_get_daemon(self, edbob, SyncDaemon):

#         # pid file provided
#         linux.get_daemon('some_pidfile')
#         self.assertFalse(edbob.config.get.called)
#         SyncDaemon.assert_called_once_with('some_pidfile')

#         # no pid file; fall back to config
#         SyncDaemon.reset_mock()
#         edbob.config.get.return_value = 'configured_pidfile'
#         linux.get_daemon()
#         edbob.config.get.assert_called_once_with('rattail.db', 'sync.pid_path',
#                                                  default='/var/run/rattail/dbsync.pid')
#         SyncDaemon.assert_called_once_with('configured_pidfile')

#     @patch('rattail.db.sync.linux.get_daemon')
#     def test_start_daemon(self, get_daemon):
#         linux.start_daemon(pidfile='some_pidfile', daemonize='maybe')
#         get_daemon.assert_called_once_with('some_pidfile')
#         get_daemon.return_value.start.assert_called_once_with('maybe')

#     @patch('rattail.db.sync.linux.get_daemon')
#     def test_stop_daemon(self, get_daemon):
#         linux.stop_daemon(pidfile='some_pidfile')
#         get_daemon.assert_called_once_with('some_pidfile')
#         get_daemon.return_value.stop.assert_called_once_with()
