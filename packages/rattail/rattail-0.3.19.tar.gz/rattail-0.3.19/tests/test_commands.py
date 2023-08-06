
import csv
import datetime
import argparse
import logging
from unittest import TestCase
from cStringIO import StringIO

from mock import patch, Mock
from fixture import TempIO

from sqlalchemy import create_engine
from sqlalchemy import func

from . import DataTestCase
from rattail import commands
from rattail.db import Session
from rattail.db import model
from rattail.db.auth import authenticate_user


class TestArgumentParser(TestCase):

    def test_parse_args_preserves_extra_argv(self):
        parser = commands.ArgumentParser()
        parser.add_argument('--some-optional-arg')
        parser.add_argument('some_required_arg')
        args = parser.parse_args([
                '--some-optional-arg', 'optional-value', 'required-value',
                'some', 'extra', 'args'])
        self.assertEqual(args.some_required_arg, 'required-value')
        self.assertEqual(args.some_optional_arg, 'optional-value')
        self.assertEqual(args.argv, ['some', 'extra', 'args'])


class TestDateArgument(TestCase):

    def test_valid_date_string_returns_date_object(self):
        date = commands.date_argument('2014-01-01')
        self.assertEqual(date, datetime.date(2014, 1, 1))

    def test_invalid_date_string_raises_error(self):
        self.assertRaises(argparse.ArgumentTypeError, commands.date_argument, 'invalid-date')


class TestCommand(TestCase):

    def test_initial_subcommands_are_sane(self):
        command = commands.Command()
        self.assertTrue('filemon' in command.subcommands)

    def test_unicode(self):
        command = commands.Command()
        command.name = 'some-app'
        self.assertEqual(unicode(command), u'some-app')
        
    def test_iter_subcommands_includes_expected_item(self):
        command = commands.Command()
        found = False
        for subcommand in command.iter_subcommands():
            if subcommand.name == 'filemon':
                found = True
                break
        self.assertTrue(found)

    def test_print_help(self):
        command = commands.Command()
        stdout = StringIO()
        command.stdout = stdout
        command.print_help()
        output = stdout.getvalue()
        stdout.close()
        self.assertTrue('Usage:' in output)
        self.assertTrue('Options:' in output)

    def test_run_with_no_args_prints_help(self):
        command = commands.Command()
        with patch.object(command, 'print_help') as print_help:
            command.run()
            print_help.assert_called_once_with()

    def test_run_with_single_help_arg_prints_help(self):
        command = commands.Command()
        with patch.object(command, 'print_help') as print_help:
            command.run('help')
            print_help.assert_called_once_with()

    def test_run_with_help_and_unknown_subcommand_args_prints_help(self):
        command = commands.Command()
        with patch.object(command, 'print_help') as print_help:
            command.run('help', 'invalid-subcommand-name')
            print_help.assert_called_once_with()

    def test_run_with_help_and_subcommand_args_prints_subcommand_help(self):
        command = commands.Command()
        fake = command.subcommands['fake'] = Mock()
        command.run('help', 'fake')
        fake.return_value.parser.print_help.assert_called_once_with()

    def test_run_with_unknown_subcommand_arg_prints_help(self):
        command = commands.Command()
        with patch.object(command, 'print_help') as print_help:
            command.run('invalid-command-name')
            print_help.assert_called_once_with()

    def test_stdout_may_be_redirected(self):
        class Fake(commands.Subcommand):
            def run(self, args):
                self.stdout.write("standard output stuff")
                self.stdout.flush()
        command = commands.Command()
        fake = command.subcommands['fake'] = Fake
        tmp = TempIO()
        config_path = tmp.putfile('test.ini', '')
        out_path = tmp.putfile('out.txt', '')
        command.run('fake', '--config', config_path, '--stdout', out_path)
        with open(out_path) as f:
            self.assertEqual(f.read(), "standard output stuff")

    def test_stderr_may_be_redirected(self):
        class Fake(commands.Subcommand):
            def run(self, args):
                self.stderr.write("standard error stuff")
                self.stderr.flush()
        command = commands.Command()
        fake = command.subcommands['fake'] = Fake
        tmp = TempIO()
        config_path = tmp.putfile('test.ini', '')
        err_path = tmp.putfile('err.txt', '')
        command.run('fake', '--config', config_path, '--stderr', err_path)
        with open(err_path) as f:
            self.assertEqual(f.read(), "standard error stuff")

    def test_verbose_flag_sets_root_logging_level_to_info(self):
        self.assertEqual(logging.getLogger().getEffectiveLevel(), logging.NOTSET)
        tmp = TempIO()
        config_path = tmp.putfile('test.ini', '')
        command = commands.Command()
        fake = command.subcommands['fake'] = Mock()
        command.run('fake', '--config', config_path, '--verbose')
        self.assertEqual(logging.getLogger().getEffectiveLevel(), logging.INFO)

    def test_debug_flag_sets_root_logging_level_to_debug(self):
        self.assertEqual(logging.getLogger().getEffectiveLevel(), logging.NOTSET)
        tmp = TempIO()
        config_path = tmp.putfile('test.ini', '')
        command = commands.Command()
        fake = command.subcommands['fake'] = Mock()
        command.run('fake', '--config', config_path, '--debug')
        self.assertEqual(logging.getLogger().getEffectiveLevel(), logging.DEBUG)

    def test_noinit_flag_means_no_config(self):
        command = commands.Command()
        fake = command.subcommands['fake'] = Mock()
        command.run('fake', '--no-init')
        self.assertTrue(fake.return_value.config is None)


class TestSubcommand(TestCase):

    def test_repr(self):
        command = commands.Command()
        subcommand = commands.Subcommand(command)
        subcommand.name = 'fake-command'
        self.assertEqual(repr(subcommand), "Subcommand(name='fake-command')")

    def test_add_parser_args_does_nothing(self):
        command = commands.Command()
        subcommand = commands.Subcommand(command)
        # Not sure this is really the way to test this, but...
        self.assertEqual(len(subcommand.parser._action_groups[0]._actions), 1)
        subcommand.add_parser_args(subcommand.parser)
        self.assertEqual(len(subcommand.parser._action_groups[0]._actions), 1)

    def test_run_not_implemented(self):
        command = commands.Command()
        subcommand = commands.Subcommand(command)
        args = subcommand.parser.parse_args([])
        self.assertRaises(NotImplementedError, subcommand.run, args)


class TestAddUser(DataTestCase):
    
    def setUp(self):
        super(TestAddUser, self).setUp()
        self.tmp = TempIO()
        self.stdout_path = self.tmp.putfile('stdout.txt', '')
        self.stderr_path = self.tmp.putfile('stderr.txt', '')

    def test_no_user_created_if_username_already_exists(self):
        self.session.add(model.User(username='fred'))
        self.session.commit()
        self.assertEqual(self.session.query(model.User).count(), 1)
        commands.main('adduser', '--no-init', '--stderr', self.stderr_path, 'fred')
        with open(self.stderr_path) as f:
            self.assertEqual(f.read(), "User 'fred' already exists.\n")
        self.assertEqual(self.session.query(model.User).count(), 1)

    def test_no_user_created_if_password_prompt_is_canceled(self):
        self.assertEqual(self.session.query(model.User).count(), 0)
        with patch('rattail.commands.getpass') as getpass:
            getpass.side_effect = KeyboardInterrupt
            commands.main('adduser', '--no-init', '--stderr', self.stderr_path, 'fred')
        with open(self.stderr_path) as f:
            self.assertEqual(f.read(), "\nOperation was canceled.\n")
        self.assertEqual(self.session.query(model.User).count(), 0)

    def test_normal_user_created_with_correct_password_but_no_admin_role(self):
        self.assertEqual(self.session.query(model.User).count(), 0)
        with patch('rattail.commands.getpass') as getpass:
            getpass.return_value = 'fredpass'
            commands.main('adduser', '--no-init', '--stdout', self.stdout_path, 'fred')
        with open(self.stdout_path) as f:
            self.assertEqual(f.read(), "Created user: fred\n")
        fred = self.session.query(model.User).one()
        self.assertEqual(fred.username, 'fred')
        self.assertEqual(len(fred.roles), 0)
        user = authenticate_user(self.session, 'fred', 'fredpass')
        self.assertTrue(user is fred)

    def test_admin_user_created_with_administrator_role(self):
        self.assertEqual(self.session.query(model.User).count(), 0)
        with patch('rattail.commands.getpass') as getpass:
            getpass.return_value = 'fredpass'
            commands.main('adduser', '--no-init', '--stdout', self.stdout_path, 'fred', '--administrator')
        fred = self.session.query(model.User).one()
        self.assertEqual(len(fred.roles), 1)
        self.assertEqual(fred.roles[0].name, 'Administrator')


class TestDatabaseSync(TestCase):

    @patch('rattail.db.sync.linux.start_daemon')
    def test_start_daemon_with_default_args(self, start_daemon):
        commands.main('dbsync', '--no-init', 'start')
        start_daemon.assert_called_once_with(None, None, True)

    @patch('rattail.db.sync.linux.start_daemon')
    def test_start_daemon_with_explicit_args(self, start_daemon):
        tmp = TempIO()
        pid_path = tmp.putfile('test.pid', '')
        commands.main('dbsync', '--no-init', '--pidfile', pid_path, '--do-not-daemonize', 'start')
        start_daemon.assert_called_once_with(None, pid_path, False)

    @patch('rattail.db.sync.linux.start_daemon')
    def test_keyboard_interrupt_raises_error_when_daemonized(self, start_daemon):
        start_daemon.side_effect = KeyboardInterrupt
        self.assertRaises(KeyboardInterrupt, commands.main, 'dbsync', '--no-init', 'start')

    @patch('rattail.db.sync.linux.start_daemon')
    def test_keyboard_interrupt_handled_gracefully_when_not_daemonized(self, start_daemon):
        tmp = TempIO()
        stderr_path = tmp.putfile('stderr.txt', '')
        start_daemon.side_effect = KeyboardInterrupt
        commands.main('dbsync', '--no-init', '--stderr', stderr_path, '--do-not-daemonize', 'start')
        with open(stderr_path) as f:
            self.assertEqual(f.read(), "Interrupted.\n")

    @patch('rattail.db.sync.linux.stop_daemon')
    def test_stop_daemon_with_default_args(self, stop_daemon):
        commands.main('dbsync', '--no-init', 'stop')
        stop_daemon.assert_called_once_with(None, None)

    @patch('rattail.db.sync.linux.stop_daemon')
    def test_stop_daemon_with_explicit_args(self, stop_daemon):
        tmp = TempIO()
        pid_path = tmp.putfile('test.pid', '')
        commands.main('dbsync', '--no-init', '--pidfile', pid_path, 'stop')
        stop_daemon.assert_called_once_with(None, pid_path)


class TestDump(DataTestCase):

    def setUp(self):
        super(TestDump, self).setUp()
        self.session.add(model.Product(upc='074305001321'))
        self.session.add(model.Product(upc='074305001161'))
        self.session.commit()

    def test_unknown_model_cannot_be_dumped(self):
        tmp = TempIO()
        stderr_path = tmp.putfile('stderr.txt', '')
        self.assertRaises(SystemExit, commands.main, '--no-init', '--stderr', stderr_path, 'dump', 'NoSuchModel')
        with open(stderr_path) as f:
            self.assertEqual(f.read(), "Unknown model: NoSuchModel\n")

    def test_dump_goes_to_stdout_by_default(self):
        tmp = TempIO()
        stdout_path = tmp.putfile('stdout.txt', '')
        commands.main('--no-init', '--stdout', stdout_path, 'dump', 'Product')
        with open(stdout_path, 'rb') as csv_file:
            reader = csv.DictReader(csv_file)
            upcs = [row['upc'] for row in reader]
        self.assertEqual(len(upcs), 2)
        self.assertTrue('00074305001321' in upcs)
        self.assertTrue('00074305001161' in upcs)

    def test_dump_goes_to_file_if_so_invoked(self):
        tmp = TempIO()
        output_path = tmp.putfile('output.txt', '')
        commands.main('--no-init', 'dump', 'Product', '--output', output_path)
        with open(output_path, 'rb') as csv_file:
            reader = csv.DictReader(csv_file)
            upcs = [row['upc'] for row in reader]
        self.assertEqual(len(upcs), 2)
        self.assertTrue('00074305001321' in upcs)
        self.assertTrue('00074305001161' in upcs)


class TestFileMonitor(TestCase):

    @patch('rattail.filemon.linux.start_daemon')
    def test_start_daemon_with_default_args(self, start_daemon):
        commands.main('filemon', '--no-init', 'start')
        start_daemon.assert_called_once_with(None, None, True)

    @patch('rattail.filemon.linux.start_daemon')
    def test_start_daemon_with_explicit_args(self, start_daemon):
        tmp = TempIO()
        pid_path = tmp.putfile('test.pid', '')
        commands.main('filemon', '--no-init', '--pidfile', pid_path, '--do-not-daemonize', 'start')
        start_daemon.assert_called_once_with(None, pid_path, False)

    @patch('rattail.filemon.linux.stop_daemon')
    def test_stop_daemon_with_default_args(self, stop_daemon):
        commands.main('filemon', '--no-init', 'stop')
        stop_daemon.assert_called_once_with(None, None)

    @patch('rattail.filemon.linux.stop_daemon')
    def test_stop_daemon_with_explicit_args(self, stop_daemon):
        tmp = TempIO()
        pid_path = tmp.putfile('test.pid', '')
        commands.main('filemon', '--no-init', '--pidfile', pid_path, 'stop')
        stop_daemon.assert_called_once_with(None, pid_path)

    @patch('rattail.commands.sys')
    def test_unknown_platform_not_supported(self, sys):
        tmp = TempIO()
        stderr_path = tmp.putfile('stderr.txt', '')
        sys.platform = 'bogus'
        commands.main('--no-init', '--stderr', stderr_path, 'filemon', 'start')
        sys.exit.assert_called_once_with(1)
        with open(stderr_path) as f:
            self.assertEqual(f.read(), "File monitor is not supported on platform: bogus\n")


# # TODO: The purge-batches command tests don't work yet; the db.batches.util
# # tests need to be figured out first...
# class TestPurgeBatches(DataTestCase):

#     def setUp(self):
#         super(TestPurgeBatches, self).setUp()
#         self.session.add(model.Batch(purge=datetime.date(2014, 1, 1)))
#         self.session.add(model.Batch(purge=datetime.date(2014, 2, 1)))
#         self.session.add(model.Batch(purge=datetime.date(2014, 3, 1)))
#         self.session.commit()
#         self.tmp = TempIO()
#         self.stdout_path = self.tmp.putfile('stdout.txt', '')

#     def test_purging_honors_batch_purge_dates(self):
#         self.assertEqual(self.session.query(model.Batch).count(), 3)
#         commands.main('--no-init', '--stdout', self.stdout_path, 'purge-batches', '--date', '2014-01-15')
#         self.assertEqual(self.session.query(model.Batch).count(), 2)
#         self.assertEqual(self.session.query(func.min(model.Batch.purge)).scalar(), datetime.date(2014, 2, 1))
#         with open(self.stdout_path) as f:
#             self.assertTrue(f.read().endswith("\nPurged 1 normal and 0 orphaned batches.\n"))

#     def test_specifying_all_purges_everything(self):
#         self.assertEqual(self.session.query(model.Batch).count(), 3)
#         commands.main('--no-init', '--stdout', self.stdout_path, 'purge-batches', '--all')
#         self.assertEqual(self.session.query(model.Batch).count(), 0)
#         with open(self.stdout_path) as f:
#             self.assertTrue(f.read().endswith("\nPurged 3 normal and 0 orphaned batches.\n"))

#     def test_orphaned_tables_are_also_purged(self):
#         self.session.delete(self.session.query(model.Batch).first())
#         self.session.commit()
#         self.assertEqual(self.session.query(model.Batch).count(), 2)
#         commands.main('--no-init', '--stdout', self.stdout_path, 'purge-batches', '--date', '2013-12-31')
#         self.assertEqual(self.session.query(model.Batch).count(), 2)
#         with open(self.stdout_path) as f:
#             self.assertTrue(f.read().endswith("\nPurged 0 normal and 1 orphaned batches.\n"))
