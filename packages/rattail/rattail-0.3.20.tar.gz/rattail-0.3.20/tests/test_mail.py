
from unittest import TestCase

from mock import patch, Mock, MagicMock

from edbob.configuration import AppConfigParser

from rattail import mail


class TestMail(TestCase):

    @patch('rattail.mail.deliver_message')
    @patch('rattail.mail.make_message')
    def test_send_message(self, make_message, deliver_message):
        config = AppConfigParser('rattail')
        mail.send_message(config,
                          'sender@mailinator.com', ['recip1@mailinator.com', 'recip2@mailinator.com'],
                          'test subject', 'test body')
        make_message.assert_called_once_with(
            'sender@mailinator.com', ['recip1@mailinator.com', 'recip2@mailinator.com'],
            'test subject', 'test body', content_type='text/plain')
        deliver_message.assert_called_once_with(config, make_message.return_value)

    def test_make_message(self):
        message = mail.make_message('sender@mailinator.com', ['recip1@mailinator.com', 'recip2@mailinator.com'],
                                    'test subject', 'test body', content_type='text/html')
        self.assertEqual(message['From'], 'sender@mailinator.com')
        self.assertEqual(message.get_all('To'), ['recip1@mailinator.com', 'recip2@mailinator.com'])
        self.assertEqual(message['Subject'], 'test subject')
        self.assertEqual(message.get_content_type(), 'text/html')
        self.assertEqual(message.get_payload(), 'test body')


@patch('rattail.mail.smtplib')
class TestDeliverMessage(TestCase):
    
    def test_config_defaults(self, smtplib):
        config = AppConfigParser('rattail')
        message = MagicMock()
        session = Mock()
        smtplib.SMTP.return_value = session
        mail.deliver_message(config, message)
        smtplib.SMTP.assert_called_once_with('localhost')
        self.assertFalse(session.login.called)
        self.assertEqual(session.sendmail.call_count, 1)
        session.quit.assert_called_once_with()

    def test_config_custom(self, smtplib):
        config = AppConfigParser('rattail')
        config.set('rattail.mail', 'smtp.server', 'mail.mailinator.com')
        config.set('rattail.mail', 'smtp.username', 'foo')
        config.set('rattail.mail', 'smtp.password', 'bar')
        message = MagicMock()
        session = Mock()
        smtplib.SMTP.return_value = session
        mail.deliver_message(config, message)
        smtplib.SMTP.assert_called_once_with('mail.mailinator.com')
        session.login.assert_called_once_with('foo', 'bar')
        self.assertEqual(session.sendmail.call_count, 1)
        session.quit.assert_called_once_with()

    @patch('rattail.mail.deprecation_warning')
    def test_config_deprecated(self, deprecation_warning, smtplib):
        config = AppConfigParser('rattail')
        config.set('edbob.mail', 'smtp.server', 'mail.mailinator.com')
        config.set('edbob.mail', 'smtp.username', 'foo')
        config.set('edbob.mail', 'smtp.password', 'bar')
        message = MagicMock()
        session = Mock()
        smtplib.SMTP.return_value = session
        mail.deliver_message(config, message)
        smtplib.SMTP.assert_called_once_with('mail.mailinator.com')
        session.login.assert_called_once_with('foo', 'bar')
        self.assertEqual(session.sendmail.call_count, 1)
        session.quit.assert_called_once_with()
        self.assertEqual(deprecation_warning.call_count, 3)
