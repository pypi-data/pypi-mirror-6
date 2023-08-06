
import logging
from unittest import TestCase
from cStringIO import StringIO

from mock import patch

from rattail import logging as rattail_logging


class TestLogging(TestCase):

    @patch('rattail.logging.sys')
    @patch('rattail.logging.socket')
    def test_adapter_adds_all_context(self, socket, sys):
        socket.getfqdn.return_value = 'testing.rattailproject.org'
        socket.gethostbyname.return_value = '127.0.0.1'
        sys.argv = ['just', 'testing']
        formatter = logging.Formatter(u"%(hostname)s %(hostip)s %(argv)s %(levelname)s %(message)s")
        string = StringIO()
        handler = logging.StreamHandler(string)
        handler.setFormatter(formatter)
        log = logging.getLogger('fake_for_testing')
        log.addHandler(handler)
        log.propagate = False
        log = rattail_logging.RattailAdapter(log)
        self.assertEqual(string.getvalue(), "")
        log.debug("some random thing")
        self.assertEqual(string.getvalue(), u"testing.rattailproject.org 127.0.0.1 ['just', 'testing'] DEBUG some random thing\n")
        string.close()
