#!/usr/bin/env python
# -*- coding: utf-8  -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2012 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU Affero General Public License as published by the Free
#  Software Foundation, either version 3 of the License, or (at your option)
#  any later version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for
#  more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################

"""
``rattail.mail`` -- Email Framework
"""

import smtplib
import warnings
import logging
from email.message import Message

from edbob.mail import sendmail_with_config


log = logging.getLogger(__name__)


def deprecation_warning(): # pragma no cover
    warnings.warn(
        "Configuration found in [edbob.mail] section, which is deprecated.  "
        "Please update configuration to use [rattail.mail] instead.",
        DeprecationWarning, stacklevel=2)


def send_message(config, sender, recipients, subject, body, content_type='text/plain'):
    """
    Assemble and deliver an email message using the given parameters and configuration.
    """
    message = make_message(sender, recipients, subject, body, content_type=content_type)
    deliver_message(config, message)


def make_message(sender, recipients, subject, body, content_type='text/plain'):
    """
    Assemble an email message object using the given parameters.
    """
    message = Message()
    message.set_type(content_type)
    message['From'] = sender
    for recipient in recipients:
        message['To'] = recipient
    message['Subject'] = subject
    message.set_payload(body)
    return message
    

def deliver_message(config, message):
    """
    Deliver an email message using the given SMTP configuration.
    """
    server = config.get('rattail.mail', 'smtp.server')
    if not server:
        server = config.get('edbob.mail', 'smtp.server')
        if server:
            deprecation_warning()
        else:
            server = 'localhost'

    username = config.get('rattail.mail', 'smtp.username')
    if not username:
        username = config.get('edbob.mail', 'smtp.username')
        if username:
            deprecation_warning()

    password = config.get('rattail.mail', 'smtp.password')
    if not password:
        password = config.get('edbob.mail', 'smtp.password')
        if password:
            deprecation_warning()

    log.debug("deliver_message: connecting to server: {0}".format(repr(server)))
    session = smtplib.SMTP(server)
    if username and password:
        result = session.login(username, password)
        log.debug("deliver_message: login result is: {0}".format(repr(result)))
    result = session.sendmail(message['From'], message.get_all('To'), message.as_string())
    log.debug("deliver_message: sendmail result is: {0}".format(repr(result)))
    session.quit()
